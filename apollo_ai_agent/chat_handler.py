# chat_handler.py — category-only routing with full history (incl. guests),
# normalization uses recent conversation context, user_location=None fallback.

import json
import time
import asyncio
import re
from fastapi import WebSocket, WebSocketDisconnect

# Your loader bundles: retrieval, LLM handler, normalizer, DB helpers
from helpers import load_heavy_modules
from logger import apollo_logger

# Load heavy modules once
retrieval_func, llm_handler, llm_query_normalization, db_functions = load_heavy_modules()

# In-memory stores (DB is source of truth, but memory drives rapid context)
user_contexts = {}        # optional normalized context for the normalizer (list/any)
user_instructions = {}    # stored instruction strings (optional)
user_chat_history = {}    # [{user: "...", assistant: "..."}] per user_id


# --------- Utilities ---------

def _is_guest(user_id: str) -> bool:
    if not user_id:
        return True
    uid = user_id.lower()
    return uid.startswith("guest") or bool(re.match(r"^guest\d{10}$", uid))

def _short_history(user_id: str, k: int = 3) -> str:
    """Return last k exchanges as compact text for the LLM chain."""
    hx = user_chat_history.get(user_id, [])[-k:]
    lines = []
    for ex in hx:
        u = ex.get("user", "").strip()
        a = ex.get("assistant", "").strip()
        if u:
            lines.append(f"User: {u}")
        if a:
            lines.append(f"Assistant: {a}")
    return "\n".join(lines)

def _history_for_normalizer(user_id: str, k: int = 5):
    """
    Return a light-weight list of recent exchanges for the normalizer.
    Keep raw strings — the normalizer can expand follow-ups (e.g., “And price?”).
    """
    hx = user_chat_history.get(user_id, [])[-k:]
    out = []
    for ex in hx:
        if ex.get("user"):
            out.append({"role": "user", "content": ex["user"]})
        if ex.get("assistant"):
            out.append({"role": "assistant", "content": ex["assistant"]})
    return out

def _strip_triple_ticks(text: str) -> str:
    """Remove code fence markers that sometimes appear."""
    if not text:
        return ""
    return re.sub(r"```(?:structured|markdown)?|```", "", text, flags=re.DOTALL)

def _format_rows_for_context(rows) -> str:
    """
    Convert DB rows into a compact text blob suited for the LLM context.
    Expect rows to be a list of dicts. Keep it brief.
    """
    if not rows:
        return ""
    out = []
    for r in rows[:8]:  # cap to avoid overloading context
        model = str(r.get("model_name", "")).strip()
        dim = str(r.get("dimension", "")).strip()
        mrp = r.get("mrp")
        li = str(r.get("load_index", "")).strip()
        sr = str(r.get("speed_rating", "")).strip()
        parts = []
        if model: parts.append(f"Model: {model}")
        if dim: parts.append(f"Size: {dim}")
        if li: parts.append(f"LI: {li}")
        if sr: parts.append(f"SR: {sr}")
        if mrp is not None: parts.append(f"MRP: {mrp}")
        if parts:
            out.append(" | ".join(parts))
    return "\n".join(out)

def _render_dealers_list(dealers) -> str:
    """
    Render a minimal list of dealers; expects iterable of dicts with name/address/phone.
    """
    if not dealers:
        return "No authorized dealers found for that location."
    lines = ["Here are nearby authorized Apollo Tyres dealers:"]
    for d in dealers[:5]:
        name = d.get("name", "Dealer")
        addr = d.get("address", "")
        phone = d.get("phone", "")
        line = f"- {name}"
        if addr:
            line += f", {addr}"
        if phone:
            line += f" | {phone}"
        lines.append(line)
    lines.append("Would you like directions or a callback from one of them?")
    return "\n".join(lines)

def _update_history(user_id: str, user_text: str, bot_text: str):
    ex = {"user": user_text or "", "assistant": bot_text or ""}
    if user_id in user_chat_history:
        user_chat_history[user_id].append(ex)
    else:
        user_chat_history[user_id] = [ex]
    # Trim memory (last ~20 exchanges)
    if len(user_chat_history[user_id]) > 20:
        user_chat_history[user_id] = user_chat_history[user_id][-20:]

async def _persist_history(user_id: str, user_text: str, bot_text: str):
    """
    Persist history for ALL users, including guests.
    Store as-is with the provided user_id (guest IDs help analytics too).
    """
    try:
        db_functions.save_chat_history_to_db(user_id, "user", user_text or "")
        db_functions.save_chat_history_to_db(user_id, "assistant", bot_text or "")
    except Exception:
        # Swallow DB errors to avoid breaking UX
        pass

def _safe_json_send(ws: WebSocket, payload: dict):
    """Send JSON with basic guard."""
    return asyncio.create_task(ws.send_text(json.dumps(payload)))

def _normalize_output_to_dict(result):
    """
    Accept either a dict (new normalizer) or tuple (old normalizer) and return a normalized dict:
    {
      category, normalized_input, sql_query, user_response, metadata, updated_context?
    }
    """
    # New: direct dict
    if isinstance(result, dict):
        return {
            "category": result.get("category"),
            "normalized_input": result.get("normalized_input") or result.get("query") or "",
            "sql_query": result.get("sql_query"),
            "user_response": result.get("user_response"),
            "metadata": result.get("metadata") or {},
            "updated_context": result.get("updated_context") or None,
        }

    # Legacy: tuple shape (category, normalized_input, sql_query, user_response, updated_context?, metadata?)
    if isinstance(result, (list, tuple)) and len(result) >= 4:
        category, normalized_input, sql_query, user_response = result[:4]
        updated_ctx = None
        md = {}
        for x in result[4:]:
            if isinstance(x, list):
                updated_ctx = x
            if isinstance(x, dict) and ("lead" in x or "location" in x or "directives" in x):
                md = x
        return {
            "category": category,
            "normalized_input": normalized_input or "",
            "sql_query": sql_query,
            "user_response": user_response,
            "metadata": md,
            "updated_context": updated_ctx,
        }

    # Fallback minimal
    return {
        "category": "greeting_clarification",
        "normalized_input": "",
        "sql_query": None,
        "user_response": "Hello! I’m your Apollo Tyres assistant. How can I help you with sizes, prices, specs, recommendations, or nearby dealers today?",
        "metadata": {},
        "updated_context": None,
    }


# --------- Main WebSocket endpoint ---------

async def chat_endpoint(websocket: WebSocket):
    """
    Real-time chat handler:
    1) Normalize & categorize (uses recent conversation context)
    2) Route by category
    3) Optional SQL/dealer lookup
    4) LLM streaming
    5) Persist + analytics (for ALL users, including guests)
    """
    user_id = None

    try:
        apollo_logger.info("WebSocket handler started.")
        while True:
            raw = await websocket.receive_text()
            apollo_logger.info(f"Received raw message: {raw}")
            message = json.loads(raw or "{}")

            # Essentials
            user_id = message.get("user_id") or "guest"
            user_input = (message.get("user_input") or "").strip()
            device_type = (message.get("device") or "").lower()
            apollo_logger.info(f"UserID: {user_id} | Device: {device_type} | UserInput: {user_input}")

            # Location: pass None if not available (futuristic, as requested)
            user_location = message.get("user_location", None)
            if not user_location:
                user_location = None  # ensure exactly None
            apollo_logger.info(f"User location: {user_location}")

            # Build normalization context from recent conversation + any stored normalized context
            history_for_norm = _history_for_normalizer(user_id, k=5)
            prior_context = user_contexts.get(user_id, [])
            normalizer_context = {
                "recent_history": history_for_norm,
                "prior_context": prior_context
            }
            apollo_logger.info(f"Normalizer context built for user {user_id}.")

            # --- Normalize the query (category-first pipeline) ---
            try:
                norm_result = llm_query_normalization.normalize_query_with_llm(
                    user_input, normalizer_context, "gemini"
                )
                apollo_logger.info(f"Query normalized for user {user_id}.")
            except Exception as e:
                apollo_logger.error(f"Normalization failed for user {user_id}: {e}", exc_info=True)
                await _safe_json_send(websocket, {
                    "chunk": "Hello! I’m your Apollo Tyres assistant. How can I help you with tyre sizes, prices, specs, recommendations, or nearby dealers today?",
                    "end": True
                })
                _update_history(user_id, user_input, "")
                await _persist_history(user_id, user_input, "")
                continue

            normalized = _normalize_output_to_dict(norm_result)
            apollo_logger.info(f"Normalized output: {normalized}")

            # If the normalizer also provides an updated_context, update our memory
            if normalized.get("updated_context") is not None:
                user_contexts[user_id] = normalized["updated_context"]
                apollo_logger.info(f"Updated context for user {user_id}.")
            else:
                user_contexts.setdefault(user_id, [])

            category = (normalized.get("category") or "greeting_clarification").strip().lower()
            normalized_input = normalized.get("normalized_input") or user_input
            sql_query = normalized.get("sql_query")
            user_response = normalized.get("user_response")
            metadata = normalized.get("metadata") or {}
            apollo_logger.info(f"Routing category: {category}")

            # --- Category routing ---

            # 1) Lead Capture — instant response + persist lead; no LLM
            if category == "lead_capture":
                if user_response:
                    await _safe_json_send(websocket, {"chunk": user_response})
                lead = (metadata.get("lead") if isinstance(metadata, dict) else None) or {}
                apollo_logger.info(f"Lead data for user {user_id}: {lead}")
                if lead:
                    try:
                        db_functions.save_lead(user_id, lead)
                        apollo_logger.info(f"Lead saved for user {user_id}.")
                    except Exception as e:
                        apollo_logger.error(f"Failed to save lead for user {user_id}: {e}", exc_info=True)
                _update_history(user_id, user_input, user_response or "")
                await _persist_history(user_id, user_input, user_response or "")
                apollo_logger.info(f"Lead capture history updated for user {user_id}.")
                await _safe_json_send(websocket, {"end": True, "full_response": user_response or ""})
                continue

            # 2) Contact Support — instant response; no LLM
            if category == "contact_support":
                msg = user_response or "You can reach Apollo Tyres Customer Care at 1800-102-1838 or apolloquickservice@apollotyres.com."
                await _safe_json_send(websocket, {"chunk": msg})
                apollo_logger.info(f"Contact support message sent to user {user_id}.")
                _update_history(user_id, user_input, msg)
                await _persist_history(user_id, user_input, msg)
                apollo_logger.info(f"Contact support history updated for user {user_id}.")
                await _safe_json_send(websocket, {"end": True, "full_response": msg})
                continue

            # 3) Dealer Locator — call your dealer service if location present, else ask for pincode/city
            if category == "dealer_locator":
                dealer_reply = ""
                loc = (metadata.get("location") if isinstance(metadata, dict) else None) or {}
                effective_loc = user_location or loc or None
                apollo_logger.info(f"Dealer locator effective location for user {user_id}: {effective_loc}")

                if effective_loc and (effective_loc.get("pincode") or effective_loc.get("city") or (
                    effective_loc.get("latitude") and effective_loc.get("longitude")
                )):
                    try:
                        dealers = db_functions.find_dealers(effective_loc)
                        apollo_logger.info(f"Dealers found for user {user_id}: {dealers}")
                        if not dealers:
                            dealer_reply = (
                                "I couldn’t find dealers with the given location. "
                                "Please share your pincode or city, and I’ll try again. "
                                "You can also call 1800-102-1838 for immediate help."
                            )
                        else:
                            dealer_reply = _render_dealers_list(dealers)
                    except Exception as e:
                        dealer_reply = (
                            "I couldn’t fetch dealer details right now. "
                            "Please share your pincode or city and I’ll try again, "
                            "or call 1800-102-1838 for immediate assistance."
                        )
                        apollo_logger.error(f"Dealer lookup failed for user {user_id}: {e}", exc_info=True)
                    await _safe_json_send(websocket, {"chunk": dealer_reply})
                    _update_history(user_id, user_input, dealer_reply)
                    await _persist_history(user_id, user_input, dealer_reply)
                    apollo_logger.info(f"Dealer locator history updated for user {user_id}.")
                    await _safe_json_send(websocket, {"end": True, "full_response": dealer_reply})
                    continue
                else:
                    apollo_logger.info(f"Dealer locator missing location for user {user_id}, requesting pincode/city via LLM.")
                    chain = llm_handler.create_chain(llm_flag="gemini", query_category="dealer_locator")
                    await _stream_chain(
                        websocket,
                        chain,
                        question=normalized_input,
                        context="",
                        chat_history=_short_history(user_id),
                        user_location=None,   # pass None explicitly
                        category="dealer_locator",
                        user_id=user_id,
                        original_input=user_input
                    )
                    continue

            # 4) Product Info — optional SQL; pass results to LLM as context
            context_text = ""
            if category == "product_info" and sql_query:
                try:
                    rows = db_functions.run_select(sql_query)
                    apollo_logger.info(f"Product info rows for user {user_id}: {rows}")
                    context_text = _format_rows_for_context(rows)
                except Exception as e:
                    apollo_logger.error(f"Product info SQL failed for user {user_id}: {e}", exc_info=True)
                    context_text = ""

            # 5) All other categories → LLM
            apollo_logger.info(f"Routing to LLM for user {user_id}, category: {category}")
            chain = llm_handler.create_chain(llm_flag="gemini", query_category=category)
            await _stream_chain(
                websocket,
                chain,
                question=normalized_input,
                context=context_text,
                chat_history=_short_history(user_id),
                user_location=None if user_location in (None, "", {}) else user_location,
                category=category,
                user_id=user_id,
                original_input=user_input
            )

    except WebSocketDisconnect:
        apollo_logger.info(f"WebSocket disconnected for user {user_id}.")
        pass


# --------- Helpers used by the endpoint ---------

async def _stream_chain(
    websocket: WebSocket,
    chain,
    question: str,
    context: str,
    chat_history: str,
    user_location,
    category: str,
    user_id: str,
    original_input: str
):
    """
    Run the chain and stream chunks to the client; update memory & DB at the end.
    """
    full_response = ""
    apollo_logger.info(f"Starting LLM chain for user {user_id}, category: {category}")
    try:
        inputs = {
            "context": context or "",
            "question": question or "",
            "chat_history": chat_history or "",
            "user_location": user_location,
            "category": category or "",
        }
        apollo_logger.info(f"LLM chain inputs for user {user_id}: {inputs}")
        for piece in chain.stream(inputs):
            clean_piece = _strip_triple_ticks(piece)
            full_response += clean_piece
            await _safe_json_send(websocket, {"chunk": clean_piece})
            await asyncio.sleep(0.05)
    except Exception as e:
        err = f"⚠️ AI response error: {str(e)}"
        apollo_logger.error(f"LLM chain error for user {user_id}: {e}", exc_info=True)
        await _safe_json_send(websocket, {"error": err})
    _update_history(user_id, original_input, full_response)
    await _persist_history(user_id, original_input, full_response)
    apollo_logger.info(f"LLM chain completed for user {user_id}. Response: {full_response[:200]}")
    await _safe_json_send(websocket, {"end": True, "full_response": full_response})
