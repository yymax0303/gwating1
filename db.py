import sqlite3
import json
from datetime import datetime

DB_PATH = "gwating.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            dept       TEXT NOT NULL,
            gender     TEXT NOT NULL,
            mbti       TEXT NOT NULL,
            interests  TEXT NOT NULL,
            ideal      TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            id_a  INTEGER,
            id_b  INTEGER,
            score REAL
        )
    """)
    conn.commit()
    conn.close()

def save_participant(name, dept, gender, mbti, interests, ideal):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO participants (name, dept, gender, mbti, interests, ideal, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name, dept, gender, mbti,
        json.dumps(interests, ensure_ascii=False),
        json.dumps(ideal,     ensure_ascii=False),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def already_registered(name, dept):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM participants WHERE name=? AND dept=?", (name, dept))
    row = c.fetchone()
    conn.close()
    return row is not None

def get_all_participants():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, dept, gender, mbti, interests, ideal FROM participants")
    rows = c.fetchall()
    conn.close()
    return [{
        "id":        r[0],
        "name":      r[1],
        "dept":      r[2],
        "gender":    r[3],
        "mbti":      r[4],
        "interests": json.loads(r[5]),
        "ideal":     json.loads(r[6]),
    } for r in rows]

def save_matches(results):
    """results: [(person_a, person_b, score), ...]"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM matches")
    for a, b, s in results:
        c.execute(
            "INSERT INTO matches (id_a, id_b, score) VALUES (?, ?, ?)",
            (a["id"], b["id"], s)
        )
    conn.commit()
    conn.close()

def get_matches():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT p1.name, p1.dept, p1.mbti, p1.interests,
               p2.name, p2.dept, p2.mbti, p2.interests,
               m.score
        FROM matches m
        JOIN participants p1 ON m.id_a = p1.id
        JOIN participants p2 ON m.id_b = p2.id
    """)
    rows = c.fetchall()
    conn.close()
    return [{
        "male":   {"name": r[0], "dept": r[1], "mbti": r[2], "interests": json.loads(r[3])},
        "female": {"name": r[4], "dept": r[5], "mbti": r[6], "interests": json.loads(r[7])},
        "score":  r[8],
    } for r in rows]