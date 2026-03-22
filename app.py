import streamlit as st
import pandas as pd
import os
import json

# --- 1. 파일 경로 및 설정 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating", layout="wide")

# 표 중앙 정렬 및 디자인 CSS
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
            try: return json.load(f)
            except: pass
    return {
        "my_decks": ["KT", "Ennea", "Maliss", "Tenpai"],
        "opp_decks": ["KT", "Ennea", "Maliss", "Tenpai"],
        "archetypes": ["운영", "전개"],
        "target_cards": ["증식의 G", "하루 우라라"],
        "win_loss_reasons": ["자신 실력", "상대 패"]
    }

def load_records():
    if os.path.exists(RECORD_FILE):
        try:
            df = pd.read_csv(RECORD_FILE)
            # 분석에 필요한 필수 데이터(승/패, 선/후)가 있는 행만 사용
            return df[df['결과'].isin(['승', '패']) & df['선후공'].isin(['선', '후'])]
        except: pass
    return pd.DataFrame()

# 세션 상태 초기화
if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()

# --- 3. 분석 표 생성 함수 (4줄 규격) ---
def create_analysis_table(target_df):
    total = len(target_df)
    if total == 0:
        return pd.DataFrame([["데이터 없음"] * 8])

    wins = len(target_df[target_df['결과'] == '승'])
    losses = len(target_df[target_df['결과'] == '패'])
    win_rate = (wins / total * 100)

    f_df = target_df[target_df['선후공'] == '선']
    s_df = target_df[target_df['선후공'] == '후']
    f_count, s_count = len(f_df), len(s_df)
    
    f_wins = len(f_df[f_df['결과'] == '승'])
    f_losses = len(f_df[f_df['결과'] == '패'])
    f_win_rate = (f_wins / f_count * 100) if f_count > 0 else 0

    s_wins = len(s_df[s_df['결과'] == '승'])
    s_losses = len(s_df[s_df['결과'] == '패'])
    s_win_rate = (s_wins / s_count * 100) if s_count > 0 else 0

    data = [
        ["게임 수", f"{total}회", "전체 승률", f"{win_rate:.2f}%", "전체 승리수", f"{wins}승", "전체 패배수", f"{losses}패"],
        ["선공 수", f"{f_count}회", "후공 수", f"{s_count}회", "선공 확률", f"{(f_count/total*100):.1f}%", "후공 확률", f"{(s_count/total*100):.1f}%"],
        ["선공 승리 수", f"{f_wins}회", "선공 패배 수", f"{f_losses}회", "선공 승률", f"{f_win_rate:.1f}%", "선공 패배율", f"{(100-f_win_rate):.1f}%"],
        ["후공 승리 수", f"{s_wins}회", "후공 패배 수", f"{s_losses}회", "후공 승률", f"{s_win_rate:.1f}%", "후공 패배율", f"{(100-s_win_rate):.1f}%"]
    ]
    return pd.DataFrame(data)

# --- 4. 메인 로직 (페이지 분기) ---
st.sidebar.title("🎮 메뉴")
# 사이드바 옵션 텍스트를 변수에 담아 정확히 비교
page = st.sidebar.radio("이동할 페이지", ["📊 기록", "📈 분석", "⚙️ 설정"])

# [페이지 1: 기록]
if page == "📊 기록":
    st.title("📊 전적 기록")
    # 기록 관련 코드는 이 블록 안에 작성
    st.info("여기에 기존 기록 관리 코드를 유지하세요.")

# [페이지 2: 분석]
elif page == "📈 분석":
    st.title("📈 상세 분석")
    df = load_records()
    if df.empty:
        st.warning("분석할 전적 데이터가 없습니다.")
    else:
        st.subheader("1. Overall Data")
        st.table(create_analysis_table(df))
        
        st.divider()
        
        st.subheader("2. 내 덱별 상세 분석")
        selected_deck = st.selectbox("분석할 덱 선택", st.session_state.metadata["my_decks"])
        deck_df = df[df['내 덱'] == selected_deck]
        
        if deck_df.empty:
            st.info(f"'{selected_deck}'의 기록이 없습니다.")
        else:
            st.table(create_analysis_table(deck_df))

# [페이지 3: 설정]
elif page == "⚙️ 설정":
    st.title("⚙️ 목록 설정")
    meta = st.session_state.metadata
    
    col1, col2 = st.columns(2)
    with col1:
        new_my = st.text_area("내 덱 (쉼표 구분)", ", ".join(meta.get("my_decks", [])))
        new_opp = st.text_area("상대 덱 (쉼표 구분)", ", ".join(meta.get("opp_decks", [])))
    with col2:
        new_arche = st.text_area("아키타입", ", ".join(meta.get("archetypes", [])))
        new_reasons = st.text_area("승패 요인", ", ".join(meta.get("win_loss_reasons", [])))
        new_cards = st.text_area("특정 카드", ", ".join(meta.get("target_cards", [])))
        
    if st.button("✅ 설정 저장", type="primary"):
        updated_meta = {
            "my_decks": [x.strip() for x in new_my.split(",") if x.strip()],
            "opp_decks": [x.strip() for x in new_opp.split(",") if x.strip()],
            "archetypes": [x.strip() for x in new_arche.split(",") if x.strip()],
            "win_loss_reasons": [x.strip() for x in new_reasons.split(",") if x.strip()],
            "target_cards": [x.strip() for x in new_cards.split(",") if x.strip()]
        }
        st.session_state.metadata = updated_meta
        with open(META_FILE, 'w', encoding='utf-8') as f:
            json.dump(updated_meta, f, ensure_ascii=False, indent=4)
        st.success("설정이 저장되었습니다!")
        st.rerun()
