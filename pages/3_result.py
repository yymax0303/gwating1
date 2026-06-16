import streamlit as st
import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from db import get_matches, DB_PATH
from utils import load_css

st.set_page_config(page_title="매칭 결과", page_icon="💑", layout="centered")
load_css()

# ── 채팅 DB 초기화 ─────────────────────────────────────────
def init_chat_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            room       TEXT NOT NULL,
            sender     TEXT NOT NULL,
            content    TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def send_message(room, sender, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (room, sender, content, created_at) VALUES (?, ?, ?, ?)",
        (room, sender, content, datetime.now().strftime("%H:%M"))
    )
    conn.commit()
    conn.close()

def get_messages(room):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT sender, content, created_at FROM messages WHERE room=? ORDER BY id ASC",
        (room,)
    )
    rows = c.fetchall()
    conn.close()
    return [{"sender": r[0], "content": r[1], "time": r[2]} for r in rows]

init_chat_db()

# ── 헤더 ──────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>💑 매칭 결과</h1>
    <p>AI가 찾아준 나의 짝을 확인하고 대화를 시작해보세요!</p>
</div>
""", unsafe_allow_html=True)

# ── 매칭 결과 불러오기 ─────────────────────────────────────
matches = get_matches()

if not matches:
    st.info("아직 매칭 결과가 없어요. 주최자가 AI 매칭을 실행하면 여기에 결과가 나타나요!")
    st.stop()

# ── 내 이름으로 결과 찾기 ──────────────────────────────────
st.markdown('<p class="section-label">🔍 내 매칭 결과 찾기</p>', unsafe_allow_html=True)

my_name = st.text_input("이름을 입력하세요", placeholder="홍길동")

my_match = None
my_gender = None

if my_name.strip():
    for m in matches:
        if m["male"]["name"] == my_name.strip():
            my_match  = m
            my_gender = "male"
            break
        if m["female"]["name"] == my_name.strip():
            my_match  = m
            my_gender = "female"
            break

    if not my_match:
        st.warning("해당 이름으로 등록된 매칭 결과가 없어요. 이름을 다시 확인해주세요!")
    else:
        partner  = my_match["female"] if my_gender == "male" else my_match["male"]
        pct      = int(my_match["score"] * 100)
        color    = "#ff6b9d" if pct >= 70 else "#ff8c69" if pct >= 40 else "#aaa"
        emoji_me = "👨" if my_gender == "male" else "👩"
        emoji_pt = "👩" if my_gender == "male" else "👨"

        # 매칭 결과 카드
        st.markdown(f"""
        <div class="match-card" style="margin-top:1rem;">
            <div class="match-names" style="font-size:1.1rem;">
                <span>{emoji_me} {my_name.strip()}</span>
                <span class="match-heart">💘</span>
                <span>{emoji_pt} {partner['name']} ({partner['dept']})</span>
            </div>
            <div class="match-score" style="color:{color}; font-size:1rem;">
                궁합 {pct}점
            </div>
            <div class="match-bar-bg">
                <div class="match-bar-fill" style="width:{pct}%; background:{color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 공통 관심사
        common = list(set(my_match["male"]["interests"]) & set(my_match["female"]["interests"]))
        if common:
            st.markdown('<p class="section-label">🎯 공통 관심사</p>', unsafe_allow_html=True)
            st.markdown(" ".join([f"`{i}`" for i in common]))

        # ── 채팅 ──────────────────────────────────────────
        st.markdown('<p class="section-label">💬 1:1 채팅</p>', unsafe_allow_html=True)

        # 채팅방 ID: 두 사람 이름을 정렬해서 고정된 방 이름 생성
        room_id = "_".join(sorted([my_match["male"]["name"], my_match["female"]["name"]]))
        messages = get_messages(room_id)

        # 채팅 메시지 출력
        chat_html = '<div class="chat-box">'
        if not messages:
            chat_html += '<p class="chat-empty">아직 메시지가 없어요. 먼저 인사해보세요 👋</p>'
        for msg in messages:
            is_me    = msg["sender"] == my_name.strip()
            side     = "right" if is_me else "left"
            bg       = "#ff6b9d" if is_me else "#f0f0f0"
            txt_col  = "white" if is_me else "#333"
            chat_html += f"""
            <div class="chat-row {side}">
                <div class="chat-sender">{'' if is_me else msg['sender']}</div>
                <div class="chat-bubble" style="background:{bg}; color:{txt_col};">
                    {msg['content']}
                </div>
                <div class="chat-time">{msg['time']}</div>
            </div>
            """
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

        # 메시지 입력
        with st.form("chat_form", clear_on_submit=True):
            col_input, col_btn = st.columns([5, 1])
            with col_input:
                msg_input = st.text_input("메시지를 입력하세요", placeholder="안녕하세요!", label_visibility="collapsed")
            with col_btn:
                send = st.form_submit_button("전송")

        if send and msg_input.strip():
            send_message(room_id, my_name.strip(), msg_input.strip())
            st.rerun()

# ── 전체 매칭 결과 (접기) ──────────────────────────────────
with st.expander("📋 전체 매칭 결과 보기"):
    for i, m in enumerate(matches, 1):
        pct   = int(m["score"] * 100)
        color = "#ff6b9d" if pct >= 70 else "#ff8c69" if pct >= 40 else "#aaa"
        st.markdown(f"""
        <div class="match-card">
            <div class="match-rank">#{i}</div>
            <div class="match-names">
                <span>👨 {m['male']['name']} ({m['male']['dept']})</span>
                <span class="match-heart">💘</span>
                <span>👩 {m['female']['name']} ({m['female']['dept']})</span>
            </div>
            <div class="match-score" style="color:{color};">궁합 {pct}점</div>
            <div class="match-bar-bg">
                <div class="match-bar-fill" style="width:{pct}%; background:{color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)