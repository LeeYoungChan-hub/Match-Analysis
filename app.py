import streamlit as st
import pandas as pd
import os
import json

# --- 기본 설정 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating System", layout="wide")

# 표 중앙 정렬을 위한 스타일
st.markdown("""
    <style>
    [data-testid="stTableIdxColumn"] { display: none; }
    th { text-align: center !important; background-color: #f0f2f6; }
    td { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

def load_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: pass
    return {"my_decks": ["KT", "Ennea", "Maliss", "Tenpai"]}

def load_records():
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE)
        # 분석에 방해되는 빈 행이나 헤더 행(문자열 포함된 행) 제외
        df = df[df['결과'].isin(['승', '패'])]
        return df
    return pd.DataFrame()

# 데이터 준비
metadata = load_metadata()
df = load_records()

# 페이지 메뉴
st.sidebar.title("🎮 Rating 메뉴")
page = st.sidebar.radio("이동할 페이지", ["📊 Rating (기록)", "📈 Analysis (분석)", "⚙️ Rating (설정)"])

if page == "📈 Analysis (분석)":
    st.title("📈 Analysis")

    if df.empty:
        st.warning("분석할 데이터가 없습니다.")
    else:
        # 공통 분석 로직 함수
        def create_analysis_df(target_df):
            total = len(target_df)
            wins = len(target_df[target_df['결과'] == '승'])
            losses = len(target_df[target_df['결과'] == '패'])
            win_rate = (wins / total * 100) if total > 0 else 0

            first_df = target_df[target_df['선후공'] == '선']
            second_df = target_df[target_df['선후공'] == '후']
            
            f_count = len(first_df)
            s_count = len(second_df)
            f_prob = (f_count / total * 100) if total > 0 else 0
            s_prob = (s_count / total * 100) if total > 0 else 0

            f_wins = len(first_df[first_df['결과'] == '승'])
            f_losses = len(first_df[first_df['결과'] == '패'])
            f_win_rate = (f_wins / f_count * 100) if f_count > 0 else 0
            f_loss_rate = 100 - f_win_rate if f_count > 0 else 0

            s_wins = len(second_df[second_df['결과'] == '승'])
            s_losses = len(second_df[second_df['결과'] == '패'])
            s_win_rate = (s_wins / s_count * 100) if s_count > 0 else 0
            s_loss_rate = 100 - s_win_rate if s_count > 0 else 0

            # 4줄 표 구성
            data = [
                ["게임 수", f"{total}", "전체 승률", f"{win_rate:.2f}%", "전체 승리수", f"{wins}", "전체 패배수", f"{losses}"],
                ["선공 수", f"{f_count}", "후공 수", f"{s_count}", "선공 확률", f"{f_prob:.1f}%", "후공 확률", f"{s_prob:.1f}%"],
                ["선공 승리 수", f"{f_wins}", "선공 패배 수", f"{f_losses}", "선공 승률", f"{f_win_rate:.1f}%", "선공 패배율", f"{f_loss_rate:.1f}%"],
                ["후공 승리 수", f"{s_wins}", "후공 패배 수", f"{s_losses}", "후공 승률", f"{s_win_rate:.1f}%", "후공 패배율", f"{s_loss_rate:.1f}%"]
            ]
            return pd.DataFrame(data)

        # 1. Overall Data
        st.subheader("1. Overall Data")
        overall_table = create_analysis_df(df)
        st.table(overall_table)

        st.divider()

        # 2. 내 덱별 승률
        st.subheader("2. 내 덱별 승률")
        selected_deck = st.selectbox("덱 선택", metadata["my_decks"])
        deck_df = df[df['내 덱'] == selected_deck]

        if deck_df.empty:
            st.info(f"'{selected_deck}'의 기록이 없습니다.")
        else:
            deck_table = create_analysis_df(deck_df)
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
