import streamlit as st
import sys
from pathlib import Path

# 상위 폴더(gwating/)를 import 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

from db import save_participant, already_registered
from utils import load_css, INTEREST_OPTIONS, MBTI_LIST, VIBE_LIST

st.set_page_config(page_title="참가자 등록", page_icon="👤", layout="centered")
load_css()

st.markdown("""
<div class="hero">
    <h1>👤 참가자 등록</h1>
    <p>설문을 작성하면 AI가 딱 맞는 사람을 찾아드려요!</p>
</div>
""", unsafe_allow_html=True)

with st.form("register_form", clear_on_submit=True):

    st.markdown('<p class="section-label">📋 기본 정보</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("이름", placeholder="홍길동")
    with col2:
        dept = st.text_input("학과", placeholder="컴퓨터공학과")

    col3, col4 = st.columns(2)
    with col3:
        gender = st.selectbox("성별", ["남성", "여성"])
    with col4:
        mbti = st.selectbox("MBTI", MBTI_LIST + ["모름"])

    st.markdown('<p class="section-label">🎯 관심사 (여러 개 선택 가능)</p>', unsafe_allow_html=True)
    interests = st.multiselect("관심사를 선택하세요", INTEREST_OPTIONS, label_visibility="collapsed")

    st.markdown('<p class="section-label">💕 이상형 조건</p>', unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    with col5:
        ideal_mbti = st.multiselect("선호 MBTI (복수 가능)", MBTI_LIST + ["상관없음"], default=["상관없음"])
    with col6:
        ideal_vibe = st.selectbox("선호하는 분위기", VIBE_LIST)

    ideal_interest = st.multiselect("상대방이 좋아했으면 하는 취미", INTEREST_OPTIONS)

    submitted = st.form_submit_button("✨ 매칭 신청하기")

if submitted:
    if not name.strip():
        st.error("이름을 입력해주세요!")
    elif not dept.strip():
        st.error("학과를 입력해주세요!")
    elif len(interests) == 0:
        st.error("관심사를 1개 이상 선택해주세요!")
    elif already_registered(name.strip(), dept.strip()):
        st.warning(f"'{name}' 님은 이미 등록되어 있어요!")
    else:
        ideal = {"mbti": ideal_mbti, "vibe": ideal_vibe, "interest": ideal_interest}
        save_participant(name.strip(), dept.strip(), gender, mbti, interests, ideal)
        st.markdown(f"""
        <div class="success-box">
            <h2>🎉 등록 완료!</h2>
            <p><strong>{name}</strong> 님의 신청이 완료됐어요.<br>
            매칭 결과가 나오면 알려드릴게요 💘</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()