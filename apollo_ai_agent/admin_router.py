from fastapi import APIRouter, Depends, HTTPException, Query
from db_functions import get_db_connection  # Your function to get a MySQL connection
import mysql.connector

admin_router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])

# Dependency to get a database connection
def get_db():
    try:
        conn = get_db_connection()
        yield conn
    finally:
        conn.close()

@admin_router.get("/user-data")
async def get_user_data(
    username: str = Query(None, description="Filter by username (partial match)"),
    email: str = Query(None, description="Filter by email (partial match)"),
    db: mysql.connector.connection.MySQLConnection = Depends(get_db)
):
    try:
        cursor = db.cursor(dictionary=True)
        base_query = "SELECT * FROM genai.users"
        conditions = []
        params = []
        if username:
            conditions.append("username LIKE %s")
            params.append(f"%{username}%")
        if email:
            conditions.append("email LIKE %s")
            params.append(f"%{email}%")
        query = base_query
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor.execute(query, tuple(params))
        users = cursor.fetchall()
        cursor.close()
        return {"success": True, "data": users}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@admin_router.get("/user-queries")
async def get_user_queries(
    user_id: str = Query(None, description="Filter by user id"),
    category: str = Query(None, description="Filter by query category"),
    db: mysql.connector.connection.MySQLConnection = Depends(get_db)
):
    try:
        cursor = db.cursor(dictionary=True)
        base_query = "SELECT * FROM user_queries"
        conditions = []
        params = []
        if user_id:
            conditions.append("user_id = %s")
            params.append(user_id)
        if category:
            conditions.append("category = %s")
            params.append(category)
        query = base_query
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor.execute(query, tuple(params))
        queries = cursor.fetchall()
        cursor.close()
        return {"success": True, "data": queries}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@admin_router.get("/chat-history")
async def get_chat_history(
    user_id: str = Query(..., description="User ID for which to retrieve chat history"),
    session_id: str = Query(None, description="Filter by session id"),
    db: mysql.connector.connection.MySQLConnection = Depends(get_db)
):
    try:
        cursor = db.cursor(dictionary=True)
        base_query = """
            SELECT role, message, timestamp 
            FROM user_chat_history
            WHERE user_id = %s
        """
        params = [user_id]
        if session_id:
            base_query += " AND session_id = %s"
            params.append(session_id)
        base_query += " ORDER BY timestamp ASC"
        cursor.execute(base_query, tuple(params))
        history = cursor.fetchall()
        cursor.close()
        return {"success": True, "chatHistory": history}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@admin_router.get("/tracking")
async def get_tracking_data(
    user_id: str = Query(None, description="Filter by user id"),
    category: str = Query(None, description="Filter by tracking category"),
    db: mysql.connector.connection.MySQLConnection = Depends(get_db)
):
    try:
        cursor = db.cursor(dictionary=True)
        base_query = "SELECT * FROM user_tracking"
        conditions = []
        params = []
        if user_id:
            conditions.append("user_id = %s")
            params.append(user_id)
        if category:
            conditions.append("category = %s")
            params.append(category)
        query = base_query
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor.execute(query, tuple(params))
        tracking_data = cursor.fetchall()
        cursor.close()
        return {"success": True, "data": tracking_data}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@admin_router.get("/feedback")
async def get_feedback(
    user_id: str = Query(None, description="Filter by user id"),
    feedback_type: str = Query(None, description="Filter by feedback type (like/dislike)"),
    min_rating: float = Query(None, description="Minimum rating filter"),
    max_rating: float = Query(None, description="Maximum rating filter"),
    db: mysql.connector.connection.MySQLConnection = Depends(get_db)
):
    try:
        cursor = db.cursor(dictionary=True)
        base_query = "SELECT * FROM user_feedback"
        conditions = []
        params = []
        if user_id:
            conditions.append("user_id = %s")
            params.append(user_id)
        if feedback_type:
            conditions.append("feedback_type = %s")
            params.append(feedback_type)
        if min_rating is not None:
            conditions.append("rating >= %s")
            params.append(min_rating)
        if max_rating is not None:
            conditions.append("rating <= %s")
            params.append(max_rating)
        query = base_query
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor.execute(query, tuple(params))
        feedback = cursor.fetchall()
        cursor.close()
        return {"success": True, "data": feedback}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
