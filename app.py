import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# 파일 경로 (스트림릿 클라우드 내부에 저장됨)
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="유희왕 전적 마스터", layout="wide")

# --- 1. 데이터 로드/저장 함수 ---
def load_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "my_decks": ["KT", "Ennea", "Maliss", "Tenpai"],
        "opp_decks": ["KT", "Ennea", "Maliss", "Tenpai", "Labrynth", "Branded"],
        "target_cards": ["증식의 G", "하루 우라라", "무한포영", "니비루", "드롤"]
    }

def save_metadata(data):
    with open(META_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_records():
    if os.path.exists(RECORD_FILE):
        return pd.read_csv(RECORD_FILE)
    return pd.DataFrame(columns=["NO.", "날짜", "선후공", "결과", "내 덱", "상대 덱", "특정 카드", "브릭", "실수", "비고"])

if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()
if 'df' not in st.session_state:
    st.session_state.df = load_records()

# --- 2. 사이드바 메뉴 ---
st.sidebar.title("📑 시트 선택")
page = st.sidebar.radio("이동할 페이지", ["Record (기록/분석)", "Meta Data (목록 관리)"])

# --- [페이지 1] Record ---
if page == "Record (기록/분석)":
    st.title("📊 Record: 전적 및 분석")
    df = st.session_state.df

    if not df.empty:
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("총 경기", f"{len(df)}판")
        with c2: st.metric("전체 승률", f"{(len(df[df['결과'] == '승']) / len(df) * 100):.1f}%")
        with c3:
            fig = px.bar(df['상대 덱'].value_counts().reset_index(), x='index', y='상대 덱', title="상대 덱 분포", height=300)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("📝 전적 입력 시트")
    if st.button("➕ 새 경기 추가"):
        new_no = df["NO."].max() + 1 if not df.empty else 1
        new_row = pd.DataFrame([{"NO.": new_no, "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"), "선후공": "선", "결과": "승", "내 덱": st.session_state.metadata["my_decks"][0], "상대 덱": st.session_state.metadata["opp_decks"][0], "특정 카드": st.session_state.metadata["target_cards"][0], "실수": False, "브릭": False}])
        st.session_state.df = pd.concat([df, new_row], ignore_index=True)
        st.rerun()

    edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic", hide_index=True,
        column_config={
            "선후공": st.column_config.SelectboxColumn("선/후", options=["선", "후"]),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"]),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata["my_decks"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata["opp_decks"]),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.metadata["target_cards"]),
        })

    if st.button("💾 데이터 저장 및 업데이트", type="primary"):
        st.session_state.df = edited_df
        st.session_state.df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.success("저장되었습니다!")

# --- [페이지 2] Meta Data ---
else:
    st.title("⚙️ Meta Data: 목록 관리")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        my_decks_str = st.text_area("내 덱 리스트 (쉼표 구분)", ", ".join(st.session_state.metadata["my_decks"]))
    with m_col2:
        opp_decks_str = st.text_area("상대 덱 리스트 (쉼표 구분)", ", ".join(st.session_state.metadata["opp_decks"]))
    
    if st.button("✅ 설정 저장", type="primary"):
        st.session_state.metadata["my_decks"] = [x.strip() for x in my_decks_str.split(",") if x.strip()]
        st.session_state.metadata["opp_decks"] = [x.strip() for x in opp_decks_str.split(",") if x.strip()]
        save_metadata(st.session_state.metadata)
        st.success("목록이 저장되었습니다!")
