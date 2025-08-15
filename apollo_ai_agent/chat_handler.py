import json
import time
import asyncio
import re
from fastapi import WebSocket, WebSocketDisconnect
from retrieve_vdb_policy import retrieve_from_vector_db
from helpers import load_heavy_modules

# Load heavy modules (retrieval, LLM handler, query normalization, DB functions)
retrieval_func, llm_handler, llm_query_normalization, db_functions = load_heavy_modules()

# In-memory stores for user conversation context, instructions, and chat history
user_contexts = {}
user_instructions = {}
user_chat_history = {}  # Each key is a user_id and value is a list of conversation exchanges

async def chat_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat interactions."""
    user_id = None  # Ensure user_id is defined

    try:
        while True:
            # Wait for a JSON message containing user_id and user_input
            data = await websocket.receive_text()
            message = json.loads(data)
            print("Received message:", message)
            user_id = message.get("user_id", "guest")
            user_input = message.get("user_input", "")
            # Determine if device is mobile from the message
            device_type = message.get("device", "").lower()

            print(f"Received message from user: {user_id} with input: {user_input}")

            # Determine if the user is a guest based on the format:
            # if user_id starts with "guest" or if it matches "guest" followed by 10 digits.
            is_guest = user_id.lower().startswith("guest") or bool(re.match(r'^guest\d{10}$', user_id.lower()))

            # Retrieve stored conversation context for this user
            conversation_context = user_contexts.get(user_id, [])
            start_time = time.time()

            # --- Normalize the query ---
            try:
                category, normalized_input, sql_query, user_response, updated_context = llm_query_normalization.normalize_query_with_llm(
                    user_input, conversation_context, "gemini"
                )
            except Exception as e:
                print(f"⚠️ Normalization error: {str(e)}")
                await websocket.send_text(json.dumps({
                    "error": "Sorry, ⚠️ We're facing some issues at the moment. Please try again after some time."
                }))
                continue

            # Update conversation context
            user_contexts[user_id] = updated_context

            # --- Handle Instruction Queries ---
            if category == "instruction_query":
                user_instructions[user_id] = normalized_input
                instruction_response = f"**Thank you. Your instruction recorded:** {normalized_input}"
                await websocket.send_text(json.dumps({"chunk": instruction_response, "end": True}))
                continue  
            
            # --- Handle Mobile Number submission ---
            elif category == "phone_submission" and user_response is not None:
                phone_submission_query_response = f"{user_response}"
                await websocket.send_text(json.dumps({"chunk": phone_submission_query_response, "end": True}))
                continue
            
            # --- Handle unclear_query ---
            elif category == "unclear_query" and user_response is not None:
                unclear_query_response = f"{user_response}"
                await websocket.send_text(json.dumps({"chunk": unclear_query_response, "end": True}))
                continue  
                   
            elif category == "irrelevant_query" or category == "inquiry_query":
                context = []
            else:
                context = retrieval_func.retrieve_and_rank(
                    normalized_input, sql_query, category, bm25_top_n=5, vdb_top_k=5
                )

            # --- Append Stored Instruction ---
            if user_instructions.get(user_id):
                normalized_input += f" ({user_instructions[user_id]})"

            print(f"Final User Query to process: {normalized_input}")

            # --- Prepare Chat History for the Conversation ---
            # Retrieve the last three exchanges from the user's chat history.
            chat_history = user_chat_history.get(user_id, [])[-3:]

            # Create a conversation chain for LLM response generation
            if device_type == 'mobile':
                conversation_chain = llm_handler.create_chain(llm_flag="gemini", query_category=category, mobile=True)
            else:
                conversation_chain = llm_handler.create_chain(llm_flag="gemini", query_category=category)

            full_response = ""
            try:
                for chunk in conversation_chain.stream({
                    "context": context,
                    "question": normalized_input,
                    "chat_history": chat_history
                }):
                    # Clean chunk by removing code block markers
                    clean_chunk = re.sub(r"```structured|```markdown|```", "", chunk, flags=re.DOTALL)
                    full_response += clean_chunk
                    await websocket.send_text(json.dumps({"chunk": clean_chunk}))
                    await asyncio.sleep(0.1)
            except Exception as e:
                await websocket.send_text(json.dumps({"error": f"⚠️ AI response error: {str(e)}"}))
            
            # Update in-memory chat history with the latest conversation exchange.
            # Each exchange is stored as a dict containing the user's input and the assistant's response.
            new_exchange = {"user": user_input, "assistant": full_response}
            if user_id in user_chat_history:
                user_chat_history[user_id].append(new_exchange)
            else:
                user_chat_history[user_id] = [new_exchange]

            # Save chat history for non-guest users only (logged-in users)
            if not is_guest:
                try:
                    db_functions.save_chat_history_to_db(user_id, "user", user_input)
                    db_functions.save_chat_history_to_db(user_id, "assistant", full_response)
                except Exception as e:
                    print("DB save failed:", e)

            # --- Save user query into user_tracking table for all users ---
            try:
                # Optionally, extract additional fields from the message if provided;
                # otherwise, default to empty strings.
                name_field = message.get("name", "")
                mobile_field = message.get("mobile", "")
                db_functions.save_user_tracking(user_id, name_field, mobile_field, user_input, category, normalized_input)
            except Exception as e:
                print("User tracking save failed:", e)

            await websocket.send_text(json.dumps({"end": True, "full_response": full_response}))

    except WebSocketDisconnect:
        print(f"User {user_id} disconnected")
