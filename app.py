import streamlit as st
import pandas as pd
import os
import json

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

RECORD_FILE = "2026.03 레이팅 - Record.csv"
SETTINGS_FILE = "settings.json"

# --- 데이터 로드 함수 ---
def load_data():
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE)
        df['브릭'] = df['브릭'].map({'TRUE': True, 'FALSE': False, True: True, False: False}).fillna(False)
        df['실수'] = df['실수'].map({'TRUE': True, 'FALSE': False, True: True, False: False}).fillna(False)
        return df
    else:
        columns = ["NO.", "날짜", "선후공", "결과", "세트 전적", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        # 초기 가이드 행 설정
        sub_label_row = {
            "NO.": "경기", "날짜": "Date", "선후공": "0.00%", "결과": "0.00%", 
            "세트 전적": "Result", "점수": "0", "내 덱": "Use.deck", 
            "상대 덱": "Opp. deck", "아키타입": "Plus Arch.", "승패 요인": "W/L Factor",
            "특정 카드": "Certain Card", "브릭": "0", "실수": "0", "비고": "Detail"
        }
        return pd.DataFrame([sub_label_row], columns=columns)

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
        "table_height": 20000
    }

if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'options' not in st.session_state:
    st.session_state.options = load_settings()

tab1, tab2 = st.tabs(["📊 Record", "⚙️ Setting"])

# ---------------------------------------------------------
# TAB 1: Record (마지막 점수 실시간 반영 최적화)
# ---------------------------------------------------------
with tab1:
    st.title("📊 Rating Dashboard")

    @st.fragment
    def render_record_table():
        current_df = st.session_state.df.copy()
        guide_df = current_df.iloc[[0]].copy()
        data_df = current_df.iloc[1:].copy()

        st.subheader("📋 가이드 및 통계")
        edited_guide = st.data_editor(guide_df, use_container_width=True, key="guide_editor")

        st.subheader("📝 경기 기록")
        edited_data = st.data_editor(
            data_df,
            num_rows="dynamic",
            use_container_width=True,
            height=20000, 
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

        # 통계 및 마지막 데이터 추출
        total_games = len(edited_data)
        if total_games > 0:
            # 1. 승률 및 선공 비율
            win_rate = (edited_data["결과"] == "승").sum() / total_games * 100
            first_rate = (edited_data["선후공"] == "선").sum() / total_games * 100
            
            # 2. 마지막 행 데이터 추출 (NO. 및 점수)
            last_row = edited_data.iloc[-1]
            last_no = str(last_row["NO."]) if pd.notna(last_row["NO."]) and str(last_row["NO."]).strip() != "" else "경기"
            last_score = str(last_row["점수"]) if pd.notna(last_row["점수"]) and str(last_row["점수"]).strip() != "" else "0"
            
            # 3. 가이드 행 업데이트 (점수 칸에 'Rate' 대신 마지막 숫자 반영)
            edited_guide.at[0, "결과"] = f"{win_rate:.2f}%"
            edited_guide.at[0, "선후공"] = f"{first_rate:.2f}%"
            edited_guide.at[0, "브릭"] = str(edited_data["브릭"].sum())
            edited_guide.at[0, "실수"] = str(edited_data["실수"].sum())
            edited_guide.at[0, "NO."] = last_no      
            edited_guide.at[0, "점수"] = last_score   # <--- 'Rate' 대신 실제 마지막 점수 노출
            
            # 나머지 영어 서브 라벨 유지
            edited_guide.at[0, "날짜"] = "Date"
            edited_guide.at[0, "세트 전적"] = "Result"
            edited_guide.at[0, "내 덱"] = "Use.deck"
            edited_guide.at[0, "상대 덱"] = "Opp. deck"
            edited_guide.at[0, "아키타입"] = "Plus Arch."
            edited_guide.at[0, "승패 요인"] = "W/L Factor"
            edited_guide.at[0, "특정 카드"] = "Certain Card"
            edited_guide.at[0, "비고"] = "Detail"

        # 세션 업데이트 및 자동 저장
        new_df = pd.concat([edited_guide, edited_data], ignore_index=True)
        if not new_df.equals(st.session_state.df):
            st.session_state.df = new_df
            new_df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')

    render_record_table()

# ---------------------------------------------------------
# TAB 2: Setting
# ---------------------------------------------------------
with tab2:
    st.title("⚙️ Setting")
    col1, col2, col3 = st.columns(3)
    my_decks_raw = col1.text_area("내 덱", "\n".join(st.session_state.options["내 덱"]), height=200)
    opp_decks_raw = col2.text_area("상대 덱", "\n".join(st.session_state.options["상대 덱"]), height=200)
    cards_raw = col3.text_area("특정 카드", "\n".join(st.session_state.options["특정 카드"]), height=200)
    
    col4, col5 = st.columns(2)
    factors_raw = col4.text_area("승패 요인", "\n".join(st.session_state.options["승패 요인"]), height=150)
    arch_raw = col5.text_area("아키타입", "\n".join(st.session_state.options["아키타입"]), height=150)

    new_options = {
        "내 덱": [x.strip() for x in my_decks_raw.split("\n") if x.strip()],
        "상대 덱": [x.strip() for x in opp_decks_raw.split("\n") if x.strip()],
        "특정 카드": [x.strip() for x in cards_raw.split("\n") if x.strip()],
        "승패 요인": [x.strip() for x in factors_raw.split("\
