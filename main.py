import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "postgres-service")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "dbuser")
DB_PASS = os.getenv("DB_PASSWORD", "securepassword123")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.on_event("startup")
def setup_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

class Message(BaseModel):
    content: str

@app.get("/api/messages")
def read_messages():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM messages ORDER BY id DESC;")
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    return messages

@app.post("/api/messages")
def create_message(msg: Message):
    if not msg.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (content) VALUES (%s) RETURNING id;", (msg.content,))
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": new_id, "content": msg.content}
    print("Uzair)")