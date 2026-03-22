import streamlit as st
import pandas as pd
import os
import json

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

RECORD_FILE = "2026.03 레이팅 - Record.csv"
SETTINGS_FILE = "settings.json"

# --- 데이터 로드 및 초기화 ---
def load_data():
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE)
        df['브릭'] = df['브릭'].map({'TRUE': True, 'FALSE': False, True: True, False: False}).fillna(False)
        df['실수'] = df['실수'].map({'TRUE': True, 'FALSE': False, True: True, False: False}).fillna(False)
        return df
    else:
        columns = ["NO.", "날짜", "선후공", "결과", "세트 전적", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
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
    return {"내 덱": ["KT"], "상대 덱": ["DD"], "특정 카드": ["Droll"], "승패 요인": ["운"], "아키타입": ["60"], "table_height": 20000}

# 세션 초기화
if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'options' not in st.session_state:
    st.session_state.options = load_settings()

# --- 자동 저장 핵심 콜백 함수 ---
def sync_and_save():
    # 에디터의 변경사항을 세션 데이터프레임에 즉시 반영
    if "data_editor" in st.session_state:
        # 가이드 행(0번)과 데이터 행 분리 처리
        data_df = st.session_state.df.iloc[1:].copy()
        guide_df = st.session_state.df.iloc[[0]].copy()
        
        # 실제 데이터 업데이트
        edited_rows = st.session_state["data_editor"]["edited_rows"]
        added_rows = st.session_state["data_editor"]["added_rows"]
        deleted_rows = st.session_state["data_editor"]["deleted_rows"]
        
        # (중략된 내부 로직은 streamlit이 자동으로 처리하도록 df를 직접 갱신)
        # 0번 가이드 행을 제외한 데이터만 다시 합쳐서 저장
        updated_df = st.session_state.df
        updated_df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')

tab1, tab2 = st.tabs(["📊 Record", "⚙️ Setting"])

with tab1:
    st.title("📊 Rating Dashboard")

    @st.fragment
    def render_record_table():
        # 데이터 분리
        current_all_df = st.session_state.df
        guide_df = current_all_df.iloc[[0]].copy()
        data_df = current_all_df.iloc[1:].copy()

        # 1. 하단 경기 기록 편집기 (on_change 추가)
        st.subheader("📝 경기 기록")
        edited_data = st.data_editor(
            data_df,
            num_rows="dynamic",
            use_container_width=True,
            height=20000, 
            key="data_editor",
            on_change=None, # 아래에서 처리
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

        # 2. 통계 실시간 계산 (수정 즉시 반영)
        if len(edited_data) > 0:
            total = len(edited_data)
            win_rate = (edited_data["결과"] == "승").sum() / total * 100
            first_rate = (edited_data["선후공"] == "선").sum() / total * 100
            last_row = edited_data.iloc[-1]
            
            guide_df.at[0, "결과"] = f"{win_rate:.2f}%"
            guide_df.at[0, "선후공"] = f"{first_rate:.2f}%"
            guide_df.at[0, "NO."] = str(last_row["NO."]) if pd.notna(last_row["NO."]) else "경기"
            guide_df.at[0, "점수"] = str(last_row["점수"]) if pd.notna(last_row["점수"]) else "0"
            guide_df.at[0, "브릭"] = str(edited_data["브릭"].sum())
            guide_df.at[0, "실수"] = str(edited_data["실수"].sum())
            
            # 레이블 고정
            for col, val in {"날짜": "Date", "세트 전적": "Result", "내 덱": "Use.deck", "상대 덱": "Opp. deck", "아키타입": "Plus Arch.", "승패 요인": "W/L Factor", "특정 카드": "Certain Card", "비고": "Detail"}.items():
                guide_df.at[0, col] = val

        # 3. 상단 가이드 출력
        st.subheader("📋 가이드 및 통계")
        st.data_editor(guide_df, use_container_width=True, key="guide_editor")

        # 4. 강제 저장 로직 (데이터 변경 감지 시)
        final_combined = pd.concat([guide_df, edited_data], ignore_index=True)
        if not final_combined.equals(st.session_state.df):
            st.session_state.df = final_combined
            final_combined.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')

    render_record_table()

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
        "승패 요인": [x.strip() for x in factors_raw.split("\n") if x.strip()],
        "아키타입": [x.strip() for x in arch_raw.split("\n") if x.strip()],
        "table_height": 20000
    }

    if new_options != st.session_state.options:
        st.session_state.options = new_options
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_options, f, ensure_ascii=False, indent=4)
