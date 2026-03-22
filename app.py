import streamlit as st
import pandas as pd
import os
import json

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

RECORD_FILE = "2026.03 레이팅 - Record.csv"
SETTINGS_FILE = "settings.json"

# --- 데이터 로드 (캐싱 적용으로 속도 향상) ---
@st.cache_data(show_spinner=False)
def load_data_initial():
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE)
        df['브릭'] = df['브릭'].map({'TRUE': True, 'FALSE': False, True: True, False: False}).fillna(False)
        df['실수'] = df['실수'].map({'TRUE': True, 'FALSE': False, True: True, False: False}).fillna(False)
        return df
    else:
        columns = ["NO.", "날짜", "선후공", "결과", "세트 전적", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        sub_label_row = {col: "" for col in columns}
        sub_label_row.update({"NO.": "0판", "선후공": "0.00%", "결과": "0.00%", "세트 전적": "Result", "브릭": "0", "실수": "0"})
        return pd.DataFrame([sub_label_row], columns=columns)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {"내 덱": [], "상대 덱": [], "특정 카드": [], "승패 요인": [], "아키타입": [], "table_height": 500}

# 세션 초기화 (최초 1회만 실행)
if 'df' not in st.session_state:
    st.session_state.df = load_data_initial()
if 'options' not in st.session_state:
    st.session_state.options = load_settings()

tab1, tab2 = st.tabs(["📊 Record", "⚙️ Setting"])

# ---------------------------------------------------------
# TAB 1: Record (최적화 버전)
# ---------------------------------------------------------
with tab1:
    st.title("📊 Rating Dashboard")
    
    # 뷰 복사본 생성 (원본 훼손 방지)
    current_df = st.session_state.df.copy()
    guide_df = current_df.iloc[[0]]
    data_df = current_df.iloc[1:]

    # 상단 가이드 (수정 빈도가 낮으므로 별도 분리)
    st.subheader("📋 가이드 및 통계")
    edited_guide = st.data_editor(guide_df, use_container_width=True, key="guide_editor")

    # 하단 경기 기록
    st.subheader("📝 경기 기록")
    edited_data = st.data_editor(
        data_df,
        num_rows="dynamic",
        use_container_width=True,
        height=st.session_state.options.get("table_height", 500),
        key="data_editor",
        column_config={
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"]),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"]),
            "세트 전적": st.column_config.SelectboxColumn("세트 전적", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"]),
            "내 덱": st.column_config.SelectboxColumn("내 덱",
