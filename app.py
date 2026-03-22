import streamlit as st
import pandas as pd
import os
import json

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

# 2. 파일 경로 설정
RECORD_FILE = "2026.03 레이팅 - Record.csv"
SETTINGS_FILE = "settings.json"

# --- 데이터 로드 함수 ---
def load_data():
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE)
        # 체크박스 데이터 타입 보정
        df['브릭'] = df['브릭'].map({'TRUE': True, 'FALSE': False, True: True, False: False}).fillna(False)
        df['실수'] = df['실수'].map({'TRUE': True, 'FALSE': False, True: True, False: False}).fillna(False)
        return df
    else:
        columns = ["NO.", "날짜", "선후공", "결과", "세트 전적", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        sub_label_row = {col: "" for col in columns}
        sub_label_row.update({"NO.": "0판", "선후공": "0.00%", "결과": "0.00%", "세트 전적": "Result", "브릭": "0", "실수": "0"})
        return pd.DataFrame([sub_label_row], columns=columns)

# --- 설정 로드 함수 ---
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {
        "내 덱": ["KT", "SwoS", "Synchron"],
        "상대 덱": ["Mitsu", "Ennea", "DD", "Red Dra", "Branded", "Maliss"],
        "특정 카드": ["TT Talent", "Droll", "Nibiru"],
        "승패 요인": ["자신 실력", "상대 패", "특정 카드", "운"],
        "아키타입": ["60", "Arch"],
        "table_height": 500
    }

# 세션 초기화
if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'options' not in st.session_state:
    st.session_state.options = load_settings()

# 3. 상단 탭 구성
tab1, tab2 = st.tabs(["📊 Record", "⚙️ Setting"])

# ---------------------------------------------------------
# TAB 1: Record (알림 없는 실시간 자동 저장)
# ---------------------------------------------------------
with tab1:
    st.title("📊 Rating Dashboard")
    guide_df = st.session_state.df.iloc[[0]].copy()
    data_df = st.session_state.df.iloc[1:].copy()

    st.subheader("📋 가이드 및 통계")
    edited_guide = st.data_editor(guide_df, use_container_width=True, key="guide_editor")

    st.subheader("📝 경기 기록")
    edited_data = st.data_editor(
        data_df,
        num_rows="dynamic",
        use_container_width=True,
        height=st.session_state.options.get("table_height", 20000),
        key="data_editor",
        column_config={
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"]),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"]),
            "세트 전적": st.column_config.SelectboxColumn("세트 전적", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"]),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.options["내 덱"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.options["상대 덱"]),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.options["특정 카드"]),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.options["승패 요인"]),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.options["아키타입"]),
            "브릭": st.column_config.CheckboxColumn("브릭", default=False),
            "실수": st.column_config.CheckboxColumn("실수", default=False),
        }
    )

    # 통계 자동 계산
    total_games = len(edited_data)
    if total_games > 0:
        win_rate = (len(edited_data[edited_data["결과"] == "승"]) / total_games) * 100
        first_rate = (len(edited_data[edited_data["선후공"] == "선"]) / total_games) * 100
        edited_guide.at[0, "결과"], edited_guide.at[0, "선후공"] = f"{win_rate:.2f}%", f"{first_rate:.2f}%"
        edited_guide.at[0, "브릭"], edited_guide.at[0, "실수"] = str(edited_data["브릭"].sum()), str(edited_data["실수"].sum())
        edited_guide.at[0, "NO."] = f"{total_games}판"

    # 기록 자동 저장 (알림 제거됨)
    new_df = pd.concat([edited_guide, edited_data], ignore_index=True)
    if not new_df.equals(st.session_state.df):
        st.session_state.df = new_df
        new_df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')

# ---------------------------------------------------------
# TAB 2: Setting (알림 없는 설정 자동 저장)
# ---------------------------------------------------------
with tab2:
    st.title("⚙️ Setting")
    
    st.subheader("📏 UI 설정")
    new_height = st.slider("표 높이 (Pixel)", 200, 1200, st.session_state.options.get("table_height", 500), 50)
    
    st.divider()
    st.subheader("📂 드롭다운 리스트 설정")
    col1, col2, col3 = st.columns(3)
    with col1:
        my_decks_raw = st.text_area("내 덱", "\n".join(st.session_state.options["내 덱"]), height=200)
    with col2:
        opp_decks_raw = st.text_area("상대 덱", "\n".join(st.session_state.options["상대 덱"]), height=200)
    with col3:
        cards_raw = st.text_area("특정 카드", "\n".join(st.session_state.options["특정 카드"]), height=200)
    
    col4, col5 = st.columns(2)
    with col4:
        factors_raw = st.text_area("승패 요인", "\n".join(st.session_state.options["승패 요인"]), height=150)
    with col5:
        arch_raw = st.text_area("아키타입", "\n".join(st.session_state.options["아키타입"]), height=150)

    # 새로운 설정값 구성
    new_options = {
        "내 덱": [x.strip() for x in my_decks_raw.split("\n") if x.strip()],
        "상대 덱": [x.strip() for x in opp_decks_raw.split("\n") if x.strip()],
        "특정 카드": [x.strip() for x in cards_raw.split("\n") if x.strip()],
        "승패 요인": [x.strip() for x in factors_raw.split("\n") if x.strip()],
        "아키타입": [x.strip() for x in arch_raw.split("\n") if x.strip()],
        "table_height": new_height
    }

    # 설정 자동 저장 (알림 제거됨)
    if new_options != st.session_state.options:
        st.session_state.options = new_options
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_options, f, ensure_ascii=False, indent=4)
        
        # 높이 변경 시 즉시 리런
        if new_height != load_settings().get("table_height"):
            st.rerun()
