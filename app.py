import streamlit as st
import pandas as pd
import os
import json

# --- 1. 파일 경로 및 기본 설정 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating System", layout="wide")

# 표 디자인 (중앙 정렬 및 헤더 스타일)
st.markdown("""
    <style>
    [data-testid="stTableIdxColumn"] { display: none; }
    th { text-align: center !important; background-color: #f0f2f6 !important; }
    td { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 데이터 처리 함수 ---
def load_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except: pass
    # 파일이 없거나 에러 시 기본값
    return {"my_decks": ["KT", "Ennea", "Maliss", "Tenpai"], "opp_decks": [], "archetypes": [], "target_cards": [], "win_loss_reasons": []}

def load_records():
    if os.path.exists(RECORD_FILE):
        try:
            df = pd.read_csv(RECORD_FILE)
            # '결과'와 '선후공' 데이터가 있는 행만 필터링 (분석용)
            return df[df['결과'].isin(['승', '패']) & df['선후공'].isin(['선', '후'])]
        except: pass
    return pd.DataFrame()

# --- 3. 세션 상태 초기화 (에러 방지 핵심) ---
if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()

if 'df' not in st.session_state:
    st.session_state.df = load_records()

# --- 4. 분석 로직 함수 (4줄 표 생성) ---
def create_analysis_report(target_df):
    total = len(target_df)
    if total == 0:
        return pd.DataFrame(["데이터 없음"], columns=["상태"])

    wins = len(target_df[target_df['결과'] == '승'])
    losses = len(target_df[target_df['결과'] == '패'])
    win_rate = (wins / total * 100)

    first_df = target_df[target_df['선후공'] == '선']
    second_df = target_df[target_df['선후공'] == '후']
    
    f_count, s_count = len(first_df), len(second_df)
    f_prob, s_prob = (f_count / total * 100), (s_count / total * 100)

    f_wins = len(first_df[first_df['결과'] == '승'])
    f_losses = len(first_df[first_df['결과'] == '패'])
    f_win_rate = (f_wins / f_count * 100) if f_count > 0 else 0
    
    s_wins = len(second_df[second_df['결과'] == '승'])
    s_losses = len(second_df[second_df['결과'] == '패'])
    s_win_rate = (s_wins / s_count * 100) if s_count > 0 else 0

    # 요청하신 4줄 구성 데이터 생성
    data = [
        ["게임 수", f"{total}회", "전체 승률", f"{win_rate:.2f}%", "전체 승리 수", f"{wins}승", "전체 패배 수", f"{losses}패"],
        ["선공 수", f"{f_count}회", "후공 수", f"{s_count}회", "선공 확률", f"{f_prob:.1f}%", "후공 확률", f"{s_prob:.1f}%"],
        ["선공 승리 수", f"{f_wins}회", "선공 패배 수", f"{f_losses}회", "선공 승률", f"{f_win_rate:.1f}%", "선공 패배율", f"{(100-f_win_rate) if f_count > 0 else 0:.1f}%"],
        ["후공 승리 수", f"{s_wins}회", "후공 패배 수", f"{s_losses}회", "후공 승률", f"{s_win_rate:.1f}%", "후공 패배율", f"{(100-s_win_rate) if s_count > 0 else 0:.1f}%"]
    ]
    # 표 형식으로 리턴 (컬럼명 없이 내용만 표시되도록 구성)
    return pd.DataFrame(data)

# --- 5. 사이드바 및 페이지 구성 ---
page = st.sidebar.radio("페이지 선택", ["📈 Analysis (분석)", "📊 Rating (기록)", "⚙️ 설정"])

if page == "📈 Analysis (분석)":
    st.title("📈 Match Analysis")
    df = st.session_state.df

    if df.empty:
        st.warning("분석할 전적 데이터가 없습니다. 먼저 기록을 추가해주세요.")
    else:
        # 1. Overall Data
        st.subheader("1. Overall Data")
        overall_table = create_analysis_report(df)
        st.table(overall_table)

        st.divider()

        # 2. 내 덱별 승률
        st.subheader("2. 내 덱별 승률")
        # 메타데이터에 등록된 내 덱 리스트 사용
        my_decks = st.session_state.metadata.get("my_decks", [])
        selected_deck = st.selectbox("분석할 내 덱 선택", my_decks)
        
        deck_df = df[df['내 덱'] == selected_deck]
        
        if deck_df.empty:
            st.info(f"'{selected_deck}' 덱으로 플레이한 기록이 없습니다.")
        else:
            deck_table = create_analysis_report(deck_df)
            st.table(deck_table)
# ---------------------------------------------------------
# [페이지 3] Rating (설정)
# ---------------------------------------------------------
else:
    st.title("⚙️ Rating 목록 설정")
    meta = st.session_state.metadata
    
    col1, col2 = st.columns(2)
    with col1:
        new_my = st.text_area("내 덱 (쉼표 구분)", ", ".join(meta["my_decks"]))
        new_opp = st.text_area("상대 덱 (쉼표 구분)", ", ".join(meta["opp_decks"]))
    with col2:
        new_arche = st.text_area("아키타입", ", ".join(meta["archetypes"]))
        new_reasons = st.text_area("승패 요인", ", ".join(meta["win_loss_reasons"]))
        new_cards = st.text_area("특정 카드", ", ".join(meta["target_cards"]))
        
    if st.button("✅ 설정 저장", type="primary"):
        st.session_state.metadata = {
            "my_decks": [x.strip() for x in new_my.split(",") if x.strip()],
            "opp_decks": [x.strip() for x in new_opp.split(",") if x.strip()],
            "archetypes": [x.strip() for x in new_arche.split(",") if x.strip()],
            "win_loss_reasons": [x.strip() for x in new_reasons.split(",") if x.strip()],
            "target_cards": [x.strip() for x in new_cards.split(",") if x.strip()]
        }
        save_metadata(st.session_state.metadata)
        st.success("드롭다운 목록이 업데이트되었습니다!")
        st.rerun()
