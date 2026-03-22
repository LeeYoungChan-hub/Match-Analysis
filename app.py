import streamlit as st
import pandas as pd
import os
import json

# --- 1. 파일 및 설정 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating System", layout="wide")

# UI 스타일 (중앙 정렬 및 불필요 요소 제거)
st.markdown("""
    <style>
    [data-testid="stTableIdxColumn"] { display: none; }
    .st-ae svg { display: none !important; }
    [data-testid="stDataEditorToolbar"] { display: none; }
    th { text-align: center !important; }
    td { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 데이터 로드 함수 ---
def load_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: pass
    return {"my_decks": ["KT", "Ennea", "Maliss", "Tenpai"], "opp_decks": [], "archetypes": [], "target_cards": [], "win_loss_reasons": []}

def load_records():
    if os.path.exists(RECORD_FILE):
        try:
            df = pd.read_csv(RECORD_FILE)
            # 숫자형 변환 및 에러 방지
            df['NO.'] = pd.to_numeric(df['NO.'], errors='coerce')
            df = df.dropna(subset=['결과', '선후공']) # 분석 불가능한 행 제외
            return df
        except: pass
    return pd.DataFrame()

# 데이터 로드
if 'metadata' not in st.session_state: st.session_state.metadata = load_metadata()
df = load_records()

# --- 3. 사이드바 ---
st.sidebar.title("🎮 Rating 메뉴")
page = st.sidebar.radio("이동할 페이지", ["📊 Rating (기록)", "📈 Analysis (분석)", "⚙️ Rating (설정)"])

# ---------------------------------------------------------
# [기록 & 설정 페이지는 기존 로직 유지 - 생략 가능 부분]
# ---------------------------------------------------------
if page == "📊 Rating (기록)":
    st.title("📊 Rating: 전적 기록")
    # ... (기존 기록 코드 삽입) ...
    st.info("기존 기록 페이지 로직을 유지합니다.")

elif page == "⚙️ Rating (설정)":
    st.title("⚙️ Rating 설정")
    # ... (기존 설정 코드 삽입) ...
    st.info("기존 설정 페이지 로직을 유지합니다.")

# ---------------------------------------------------------
# [핵심] 📈 Analysis (분석) 페이지
# ---------------------------------------------------------
elif page == "📈 Analysis (분석)":
    st.title("📈 Rating Detailed Analysis")
    
    if df.empty:
        st.warning("분석할 데이터가 없습니다. 먼저 기록을 완료해주세요.")
    else:
        # 공통 분석 함수
        def get_analysis_table(target_df):
            total = len(target_df)
            if total == 0: return pd.DataFrame()
            
            wins = len(target_df[target_df['결과'] == '승'])
            losses = len(target_df[target_df['결과'] == '패'])
            win_rate = (wins / total * 100) if total > 0 else 0
            
            first = target_df[target_df['선후공'] == '선']
            second = target_df[target_df['선후공'] == '후']
            f_count, s_count = len(first), len(second)
            f_prob, s_prob = (f_count/total*100), (s_count/total*100)
            
            f_wins = len(first[first['결과'] == '승'])
            f_losses = len(first[first['결과'] == '패'])
            f_win_rate = (f_wins/f_count*100) if f_count > 0 else 0
            
            s_wins = len(second[second['결과'] == '승'])
            s_losses = len(second[second['결_val' if '결_val' in second else '결과'] == '패'])
            s_win_rate = (s_wins/s_count*100) if s_count > 0 else 0

            data = [
                ["게임 수", f"{total}회", "전체 승률", f"{win_rate:.2f}%", "승리 수", f"{wins}승", "패배 수", f"{losses}패"],
                ["선공 수", f"{f_count}회", "후공 수", f"{s_count}회", "선공 확률", f"{f_prob:.1f}%", "후공 확률", f"{s_prob:.1f}%"],
                ["선공 승리", f"{f_wins}회", "선공 패배", f"{f_losses}회", "선공 승률", f"{f_win_rate:.1f}%", "선공 패율", f"{100-f_win_rate:.1f}%"],
                ["후공 승리", f"{s_wins}회", "후공 패배", f"{s_losses}회", "후공 승률", f"{s_win_rate:.1f}%", "후공 패율", f"{100-s_win_rate:.1f}%"]
            ]
            return pd.DataFrame(data)

        # 1. Overall Data
        st.subheader("1️⃣ Overall Data")
        overall_table = get_analysis_table(df)
        st.table(overall_table)

        st.divider()

        # 2. 내 덱별 승률
        st.subheader("2️⃣ 내 덱별 상세 분석")
        my_deck_list = st.session_state.metadata["my_decks"]
        selected_deck = st.selectbox("분석할 덱을 선택하세요", my_deck_list)
        
        deck_df = df[df['내 덱'] == selected_deck]
        
        if deck_df.empty:
            st.info(f"'{selected_deck}'으로 플레이한 기록이 없습니다.")
        else:
            deck_table = get_analysis_table(deck_df)
            st.table(deck_table)

        # 추가: 실수/브릭 요약
        st.divider()
        st.subheader("🚩 특이사항 요약")
        c1, c2 = st.columns(2)
        with c1: st.metric("총 브릭 발생", f"{df['브릭'].astype(bool).sum()}회")
        with c2: st.metric("총 실수 발생", f"{df['실수'].astype(bool).sum()}회")

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
