import streamlit as st
from pathlib import Path

INTEREST_OPTIONS = [
    "영화/드라마", "음악", "운동/헬스", "게임", "독서",
    "요리", "여행", "카페", "사진/영상", "아이돌/K-POP"
]

MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP",
]

VIBE_LIST = [
    "상관없음", "활발하고 외향적", "조용하고 내향적",
    "유머러스", "다정하고 감성적", "지적이고 대화 잘 통하는"
]

def load_css():
    css_path = Path(__file__).parent / "style.css"
    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)