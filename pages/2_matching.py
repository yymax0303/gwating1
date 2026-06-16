import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append(str(Path(__file__).parent.parent))

from db import get_all_participants, save_matches
from utils import load_css, INTEREST_OPTIONS

st.set_page_config(page_title="AI 매칭", page_icon="🤖", layout="centered")
load_css()

# ── 매칭 알고리즘 ─────────────────────────────────────────
def interest_vector(interests):
    return np.array([1 if opt in interests else 0 for opt in INTEREST_OPTIONS], dtype=float)

def mbti_score(person, target):
    ideal = target["ideal"]["mbti"]
    if "상관없음" in ideal or not ideal:
        return 0.5
    return 1.0 if person["mbti"] in ideal else 0.0

def vibe_score(person_mbti, ideal_vibe):
    if ideal_vibe == "상관없음":
        return 0.5
    extrovert = person_mbti.startswith("E")
    mapping = {
        "활발하고 외향적":         extrovert,
        "조용하고 내향적":         not extrovert,
        "유머러스":                person_mbti in ["ENTP","ESTP","ENFP","ESFP"],
        "다정하고 감성적":         person_mbti in ["INFP","ENFJ","ISFJ","ESFJ"],
        "지적이고 대화 잘 통하는": person_mbti in ["INTJ","INTP","ENTJ","ENTP","INFJ"],
    }
    return 1.0 if mapping.get(ideal_vibe, False) else 0.2

def calc_score(a, b):
    vec_a = interest_vector(a["interests"])
    vec_b = interest_vector(b["interests"])
    if vec_a.sum() == 0 or vec_b.sum() == 0:
        interest_sim = 0.0
    else:
        interest_sim = float(cosine_similarity([vec_a], [vec_b])[0][0])

    a_fits_b = (mbti_score(a, b) + vibe_score(a["mbti"], b["ideal"]["vibe"])) / 2
    b_fits_a = (mbti_score(b, a) + vibe_score(b["mbti"], a["ideal"]["vibe"])) / 2

    return round(interest_sim * 0.4 + a_fits_b * 0.3 + b_fits_a * 0.3, 4)

def run_matching(participants):
    males   = [p for p in participants if p["gender"] == "남성"]
    females = [p for p in participants if p["gender"] == "여성"]

    pairs = []
    for mi, m in enumerate(males):
        for fi, f in enumerate(females):
            pairs.append((calc_score(m, f), mi, fi, m, f))
    pairs.sort(reverse=True)

    matched_m, matched_f, results = set(), set(), []
    for score, mi, fi, m, f in pairs:
        if mi in matched_m or fi in matched_f:
            continue
        matched_m.add(mi)
        matched_f.add(fi)
        results.append((m, f, score))
    return results

# ── 페이지 ────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🤖 AI 매칭</h1>
    <p>주최자 전용 — 매칭을 실행하고 결과를 확인하세요</p>
</div>
""", unsafe_allow_html=True)

participants = get_all_participants()
males   = [p for p in participants if p["gender"] == "남성"]
females = [p for p in participants if p["gender"] == "여성"]

st.markdown('<p class="section-label">👥 참가자 현황</p>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
c1.metric("전체", f"{len(participants)}명")
c2.metric("남성", f"{len(males)}명")
c3.metric("여성", f"{len(females)}명")

if participants:
    st.markdown('<p class="section-label">📋 등록된 참가자</p>', unsafe_allow_html=True)
    df = pd.DataFrame([{
        "이름": p["name"], "학과": p["dept"],
        "성별": p["gender"], "MBTI": p["mbti"],
        "관심사": ", ".join(p["interests"])
    } for p in participants])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("아직 등록된 참가자가 없어요.")

st.markdown('<p class="section-label">✨ 매칭 실행</p>', unsafe_allow_html=True)

if len(males) == 0 or len(females) == 0:
    st.warning("남성과 여성 참가자가 모두 1명 이상 있어야 매칭할 수 있어요!")
else:
    if st.button("💘 AI 매칭 시작하기"):
        with st.spinner("AI가 최적의 짝을 찾는 중... 💭"):
            results = run_matching(participants)

        save_matches(results)
        st.success("매칭 완료! '💑 매칭 결과' 페이지에서 확인하세요 🎉")

        st.markdown('<p class="section-label">💑 매칭 결과 미리보기</p>', unsafe_allow_html=True)
        for i, (male, female, score) in enumerate(results, 1):
            pct   = int(score * 100)
            color = "#ff6b9d" if pct >= 70 else "#ff8c69" if pct >= 40 else "#aaa"
            st.markdown(f"""
            <div class="match-card">
                <div class="match-rank">#{i}</div>
                <div class="match-names">
                    <span>👨 {male['name']} ({male['dept']})</span>
                    <span class="match-heart">💘</span>
                    <span>👩 {female['name']} ({female['dept']})</span>
                </div>
                <div class="match-score" style="color:{color};">궁합 {pct}점</div>
                <div class="match-bar-bg">
                    <div class="match-bar-fill" style="width:{pct}%; background:{color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)