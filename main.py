from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import sqlite3
from datetime import datetime
from typing import List, Optional

app = FastAPI(title="Reviews Sentiment Service")

DB_PATH = "reviews.db"

class ReviewCreate(BaseModel):
    text: str

class Review(ReviewCreate):
    id: int
    sentiment: str
    created_at: str

# Словарь для простой сентимент-аналитики
POSITIVE_KEYWORDS = ["хорош", "люблю"]
NEGATIVE_KEYWORDS = ["плохо", "ненавиж"]

def init_db():
    """Создаём таблицу, если её нет."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def get_sentiment(text: str) -> str:
    txt = text.lower()
    if any(tok in txt for tok in POSITIVE_KEYWORDS):
        return "positive"
    if any(tok in txt for tok in NEGATIVE_KEYWORDS):
        return "negative"
    return "neutral"

# Инициализация БД при старте приложения
@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/reviews", response_model=Review, status_code=201)
def create_review(payload: ReviewCreate):
    sentiment = get_sentiment(payload.text)
    created_at = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reviews (text, sentiment, created_at)
        VALUES (?, ?, ?)
    """, (payload.text, sentiment, created_at))
    conn.commit()
    review_id = cursor.lastrowid
    conn.close()
    return Review(
        id=review_id,
        text=payload.text,
        sentiment=sentiment,
        created_at=created_at
    )


@app.get("/reviews", response_model=List[Review])
def list_reviews(sentiment: Optional[str] = Query(None, description="Фильтр по настроению")):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if sentiment:
        cursor.execute(
            "SELECT id, text, sentiment, created_at FROM reviews WHERE sentiment = ? ORDER BY id",
            (sentiment,)
        )
    else:
        cursor.execute(
            "SELECT id, text, sentiment, created_at FROM reviews ORDER BY id"
        )
    rows = cursor.fetchall()
    conn.close()
    return [
        Review(id=r[0], text=r[1], sentiment=r[2], created_at=r[3])
        for r in rows
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)