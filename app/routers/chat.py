import json
import uuid
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Body
from langchain.chains import ConversationalRetrievalChain
from .. import database, vector_store, llm_setup, analytics
from ..geocoding import geocoding_service
from ..schemas import QueryRequest

router = APIRouter()
chat_histories = {}

def get_location_context(latitude: float, longitude: float) -> str:
    """Get location context based on coordinates with city name"""
    # Get comprehensive location info including city name
    location_info = geocoding_service.get_location_info(latitude, longitude)
    
    # Build location string with city name
    if location_info["city"]:
        location_string = f"{location_info['city']}, {location_info['region']}"
    else:
        # Fallback to coordinates if city not found
        location_string = f"{location_info['region']} ({latitude:.4f}, {longitude:.4f})"
    
    return location_string

@router.post("/query")
async def query_qa(req: QueryRequest):
    retriever = vector_store.get_vector_store().as_retriever(search_kwargs={"k": 5})
    session_id = req.session_id or "default"
    
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm_setup.get_llm(),
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": llm_setup.SYSTEM_PROMPT}
    )
    
    try:
        # Get location from request if available
        user_location = getattr(req, 'user_location', None)
        location_info = "Unknown"
        
        if user_location and user_location.get('latitude') and user_location.get('longitude'):
            lat = user_location['latitude']
            lng = user_location['longitude']
            location_info = get_location_context(lat, lng)
        
        result = qa.invoke({
            "question": req.question,
            "chat_history": chat_histories[session_id],
            "user_location": location_info
        })
        answer = result["answer"]
        chat_histories[session_id].append((req.question, answer))
        
        if len(chat_histories[session_id]) > 10:
            chat_histories[session_id] = chat_histories[session_id][-10:]
        
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-questions")
async def generate_suggested_questions(data: dict = Body(...)):
    """Generate dynamic suggested questions based on conversation context"""
    try:
        conversation_history = data.get("conversation_history", [])
        current_topic = data.get("current_topic", "")
        
        print(f"Generating questions for topic: {current_topic}")
        print(f"Conversation history length: {len(conversation_history)}")
        
        # Format conversation history for better context
        formatted_history = ""
        if conversation_history:
            for i, message in enumerate(conversation_history):
                if message.get("role") == "user":
                    content = message.get('content', message.get('text', ''))
                    formatted_history += f"User: {content}\n"
                elif message.get("role") == "assistant":
                    content = message.get('content', message.get('text', ''))
                    formatted_history += f"Bot: {content}\n"
        
        print(f"Formatted history: {formatted_history[:200]}...")
        
        # Create a prompt for generating relevant questions
        prompt = f"""
Based on the following conversation about Apollo Tyres, generate 5 relevant follow-up questions that a user might ask about Apollo Tyres products and services.

Conversation History:
{formatted_history}

Current Topic: {current_topic}

Generate 5 questions that users would naturally ask about Apollo Tyres, such as:
1. Questions about specific Apollo tyre models and their features
2. Questions about warranty, pricing, and availability
3. Questions about tyre performance, durability, and specifications
4. Questions about finding dealers, installation, and services
5. Questions about tyre maintenance, care, and best practices

Focus on user questions about:
- Specific Apollo tyre models (Amazer, Alnac, Apterra, etc.)
- Warranty information and coverage
- Pricing and budget options
- Performance features and benefits
- Dealer locations and services
- Tyre maintenance and care
- Installation and fitting services
- Product comparisons and recommendations

Make sure the questions are:
- From the user's perspective (what users would ask)
- Specific to Apollo Tyres products and services
- Natural and conversational
- Relevant to the current conversation context
- Helpful for users to get more information

Return only the questions, one per line, without numbering or bullet points.
"""
        
        # Use the LLM to generate questions
        llm = llm_setup.get_llm()
        response = llm.invoke(prompt)
        
        # Extract questions from the response
        questions_text = response.content.strip()
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
        print(f"Generated questions: {questions}")
        
        # Ensure we have exactly 5 questions
        if len(questions) > 5:
            questions = questions[:5]
        elif len(questions) < 5:
            # Add some fallback questions if not enough were generated
            fallback_questions = [
                "What is the warranty period for Apollo tyres?",
                "How do I find a nearby Apollo dealer?",
                "What are the different types of Apollo tyres?",
                "How to maintain my tyres properly?",
                "What is the recommended tyre pressure?"
            ]
            questions.extend(fallback_questions[:5-len(questions)])
        
        print(f"Final questions to return: {questions}")
        return {"questions": questions}
        
    except Exception as e:
        print(f"Error generating questions: {e}")
        # Return fallback questions if generation fails
        fallback_questions = [
            "What is the warranty period for Apollo tyres?",
            "How do I find a nearby Apollo dealer?",
            "What are the different types of Apollo tyres?",
            "How to maintain my tyres properly?",
            "What is the recommended tyre pressure?"
        ]
        return {"questions": fallback_questions}

@router.websocket("/ws")
async def websocket_endpoint_ws(websocket: WebSocket):
    try:
        print("New WebSocket connection attempt...")
        await websocket.accept()
        print("WebSocket connection accepted")
        
        # Create a unique session ID for this WebSocket connection
        session_id = analytics.generate_short_id()
        user_id = analytics.generate_user_id()  # Generate a meaningful user ID
        session_start_time = datetime.now()
        chat_histories[session_id] = []
        print(f"Created new session: {session_id} for user: {user_id}")
        
        # Get client info
        client = websocket.client
        page_url = "unknown"  # Default value
        
        # Record session start
        analytics.record_user_event(
            user_id=user_id,
            session_id=session_id,
            event_type="session_start",
            event_data={
                "page_url": page_url,
                "timestamp": session_start_time.isoformat(),
                "connection_type": "websocket",
                "client_info": {
                    "host": client.host if hasattr(client, 'host') else 'unknown',
                    "port": client.port if hasattr(client, 'port') else 'unknown'
                }
            }
        )
        
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                print(f"Received message from client: {data[:100]}...")
                message = json.loads(data)
                
                # Update page URL if provided in the message
                if "page_url" in message:
                    page_url = message["page_url"]
                    # Update session with page URL
                    database.execute_query(
                        """
                        UPDATE sessions 
                        SET page_url = %s 
                        WHERE session_id = %s
                        """,
                        (page_url, session_id),
                        fetch=False
                    )
                
                # Extract user_id from message if provided
                if "user_id" in message and message["user_id"]:
                    new_user_id = message["user_id"]
                    
                    # First ensure the user exists by recording the identification event
                    analytics.record_user_event(
                        new_user_id,
                        session_id,
                        "user_identified",
                        {
                            "timestamp": datetime.now().isoformat(),
                            "previous_id": user_id
                        }
                    )
                    
                    # Now that we know the user exists, update the session
                    database.execute_query(
                        """
                        UPDATE sessions 
                        SET user_id = %s 
                        WHERE session_id = %s
                        """,
                        (new_user_id, session_id),
                        fetch=False
                    )
                    
                    user_id = new_user_id
                
                # Process the message
                if "user_input" in message:
                    message_start_time = datetime.now()
                    print(f"Processing user input: {message['user_input'][:50]}...")
                    
                    # Extract location data if available
                    user_location = message.get("user_location")
                    if user_location:
                        print(f"User location: {user_location}")
                        
                        # Get city name from coordinates if available
                        if user_location.get('latitude') and user_location.get('longitude'):
                            lat = user_location['latitude']
                            lng = user_location['longitude']
                            city_name = geocoding_service.get_city_from_coordinates(lat, lng)
                            if city_name:
                                user_location['city'] = city_name
                                print(f"Detected city: {city_name}")
                        
                        # Store location data in session
                        database.execute_query(
                            """
                            UPDATE sessions 
                            SET location_data = %s 
                            WHERE session_id = %s
                            """,
                            (json.dumps(user_location), session_id),
                            fetch=False
                        )
                    
                    # Record the user's question with location
                    analytics.record_user_event(
                        user_id,
                        session_id,
                        "question_asked",
                        {
                            "question": message["user_input"],
                            "timestamp": message_start_time.isoformat(),
                            "chat_history_length": len(chat_histories[session_id]),
                            "user_location": user_location
                        }
                    )

                    # Check if conversation exists for this session
                    conversation = database.execute_query(
                        """
                        SELECT conversation_id 
                        FROM conversations 
                        WHERE session_id = %s AND status = 'active'
                        """,
                        (session_id,)
                    )

                    if not conversation:
                        # Create new conversation if none exists
                        conversation_id = str(uuid.uuid4())
                        database.execute_query(
                            """
                            INSERT INTO conversations 
                            (conversation_id, session_id, user_id, start_time, status)
                            VALUES (%s, %s, %s, %s, 'active')
                            """,
                            (conversation_id, session_id, user_id, message_start_time.isoformat()),
                            fetch=False
                        )
                    else:
                        conversation_id = conversation[0]['conversation_id']
                    
                    # Get chat history from message
                    chat_history = message.get("chat_history", [])
                    if chat_history:
                        formatted_history = [(msg["content"], "") for msg in chat_history if msg["role"] == "user"]
                        chat_histories[session_id] = formatted_history
                    
                    # Build retriever
                    retriever = vector_store.get_vector_store().as_retriever(search_kwargs={"k": 5})
                    
                    # Use ConversationalRetrievalChain
                    qa = ConversationalRetrievalChain.from_llm(
                        llm=llm_setup.get_llm(),
                        retriever=retriever,
                        combine_docs_chain_kwargs={"prompt": llm_setup.SYSTEM_PROMPT}
                    )
                    
                    try:
                        # Format location information for the LLM
                        location_info = "Unknown"
                        if user_location and user_location.get('latitude') and user_location.get('longitude'):
                            lat = user_location['latitude']
                            lng = user_location['longitude']
                            location_info = get_location_context(lat, lng)
                        
                        # Get answer using chat history and location
                        result = qa.invoke({
                            "question": message["user_input"],
                            "chat_history": chat_histories[session_id],
                            "user_location": location_info
                        })
                        answer = result["answer"]
                        response_time = (datetime.now() - message_start_time).total_seconds()
                        
                        # Record the bot's response
                        analytics.record_user_event(
                            user_id,
                            session_id,
                            "bot_response",
                            {
                                "response": answer,
                                "timestamp": datetime.now().isoformat(),
                                "response_time": response_time
                            }
                        )

                        # Update chat history
                        chat_histories[session_id].append((message["user_input"], answer))
                        
                        # Update message count in sessions table (count each interaction as 1)
                        database.execute_query(
                            """
                            UPDATE sessions 
                            SET message_count = message_count + 1,
                                last_message_time = %s
                            WHERE session_id = %s
                            """,
                            (datetime.now().isoformat(), session_id),
                            fetch=False
                        )
                        
                        # Limit chat history length
                        if len(chat_histories[session_id]) > 10:
                            chat_histories[session_id] = chat_histories[session_id][-10:]
                        
                        # Send response back to client
                        response = {
                            "text": answer,
                            "done": True
                        }
                        await websocket.send_json(response)
                        print(f"Response sent successfully for session {session_id}")
                    except Exception as e:
                        error_msg = f"Error processing request: {str(e)}"
                        print(error_msg)
                        
                        # Record error event
                        analytics.record_user_event(
                            user_id,
                            session_id,
                            "error",
                            {
                                "error": str(e),
                                "timestamp": datetime.now().isoformat(),
                                "question": message["user_input"]
                            }
                        )
                        
                        await websocket.send_json({
                            "error": error_msg,
                            "done": True
                        })
            except WebSocketDisconnect:
                print(f"WebSocket disconnected for session {session_id}")
                session_end_time = datetime.now()
                session_duration = (session_end_time - session_start_time).total_seconds()
                
                # Update session with end time and duration
                database.execute_query(
                    """
                    UPDATE sessions 
                    SET end_time = %s,
                        duration = %s,
                        status = 'completed'
                    WHERE session_id = %s
                    """,
                    (session_end_time.isoformat(), session_duration, session_id),
                    fetch=False
                )
                
                analytics.record_user_event(
                    user_id,
                    session_id,
                    "session_end",
                    {
                        "timestamp": session_end_time.isoformat(),
                        "total_messages": len(chat_histories[session_id]),
                        "duration": session_duration
                    }
                )
                break
            except Exception as e:
                print(f"Error in WebSocket loop: {str(e)}")
                if user_id:
                    analytics.record_user_event(
                        user_id,
                        session_id,
                        "error",
                        {
                            "error": str(e),
                            "timestamp": datetime.now().isoformat(),
                            "type": "websocket_error"
                        }
                    )
                await websocket.send_json({
                    "error": f"Internal server error: {str(e)}",
                    "done": True
                })
                break
    except Exception as e:
        print(f"Fatal WebSocket error: {str(e)}")
    finally:
        print(f"Cleaning up session {session_id}")
        if session_id in chat_histories:
            del chat_histories[session_id]
        try:
            await websocket.close()
        except:
            pass

@router.websocket("/ws/chat")
async def websocket_endpoint_chat(websocket: WebSocket):
    await websocket_endpoint_ws(websocket)