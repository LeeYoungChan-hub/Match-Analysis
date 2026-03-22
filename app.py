import streamlit as st
import pandas as pd
import os
import json

# --- 설정: 새로운 파일명으로 깨끗하게 시작 ---
RECORD_FILE = 'ygo_data.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# CSS: 표 중앙 정렬 및 디자인
st.markdown("""
    <style>
    [data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"] div { text-align: center !important; font-size: 13px !important; }
    thead tr th { background-color: #f0f2f6 !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

def load_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    return {"my_decks": ["KT", "Ennea"], "opp_decks": ["Mitsu", "Tenpai"], "archetypes": ["운영"], "win_loss_reasons": ["실력"], "target_cards": ["Ash"]}

def load_records():
    cols = ["NO.", "날짜", "선후공", "결과", "세트", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE, dtype=str).fillna("")
        for col in ["브릭", "실수"]:
            if col in df.columns: df[col] = df[col].apply(lambda x: str(x).lower() in ['true', '1'])
        return df
    return pd.DataFrame(columns=cols)

def save_records(df):
    df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
    st.session_state.df = df.reset_index(drop=True)

if 'metadata' not in st.session_state: st.session_state.metadata = load_metadata()
if 'df' not in st.session_state: st.session_state.df = load_records()

st.title("📊 Match Record (New)")

if st.button("➕ Add New Match"):
    new_no = str(len(st.session_state.df) + 1)
    new_row = pd.DataFrame([{"NO.": new_no, "날짜": "", "선후공": "", "결과": "", "세트": "", "점수": "", "내 덱": "", "상대 덱": "", "아키타입": "", "승패 요인": "", "특정 카드": "", "브릭": False, "실수": False, "비고": ""}])
    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
    save_records(st.session_state.df)
    st.rerun()

edited = st.data_editor(
    st.session_state.df, 
    use_container_width=True, 
    num_rows="dynamic", 
    hide_index=True, 
    key="editor_v3",
    column_config={
        "선후공": st.column_config.SelectboxColumn(options=["", "선", "후"]),
        "결과": st.column_config.SelectboxColumn(options=["", "승", "패"]),
        "내 덱": st.column_config.SelectboxColumn(options=[""] + st.session_state.metadata["my_decks"]),
        "상대 덱": st.column_config.SelectboxColumn(options=[""] + st.session_state.metadata["opp_decks"]),
        "브릭": st.column_config.CheckboxColumn(),
        "실수": st.column_config.CheckboxColumn(),
    }
)

if not edited.equals(st.session_state.df):
    save_records(edited)
    st.rerun()
