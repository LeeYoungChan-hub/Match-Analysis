import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# 🔥 [UI 최적화] 표 디자인 (라벨 행 배경색 및 중앙 정렬)
st.markdown("""
    <style>
    [data-testid="stTableIdxColumn"] { display: none; }
    th { display: none; } /* 데이터프레임 자체 헤더는 숨김 */
    td { 
        text-align: center !important; 
        border: 1px solid #dee2e6 !important;
        padding: 10px !important;
    }
    /* 라벨이 들어가는 홀수 번째 행 배경색 설정 */
    tr:nth-child(odd) {
        background-color: #f0f2f6 !important;
        font-weight: bold;
    }
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
        "opp_decks": ["KT", "Ennea", "Maliss", "Tenpai", "Labrynth", "Branded"],
        "archetypes": ["운영", "전개", "미드레인지", "함떡", "기타"],
        "target_cards": ["증식의 G", "하루 우라라", "무한포영", "니비루", "드롤"],
        "win_loss_reasons": ["상대 패", "자신 실력", "특정 카드", "핸드 말림", "기타"]
    }

def load_records():
    if os.path.exists(RECORD_FILE):
        try:
            df = pd.read_csv(RECORD_FILE)
            # 분석용 필터링 (결과값이 있는 데이터만)
            return df[df['결과'].isin(['승', '패'])]
        except: pass
    return pd.DataFrame()

# 세션 초기화
if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()

# --- 3. 분석 표 생성 함수 (라벨-값 상하 배치 8행 구성) ---
def create_analysis_table(target_df):
    total = len(target_df)
    if total == 0:
        return pd.DataFrame([["데이터 없음"] * 4])

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

    # 📸 캡처 이미지 레이아웃: 라벨 행과 값 행을 교차로 배치
    data = [
        ["게임 수", "전체 승률", "전체 승리수", "전체 패배 수"], # 1행: 라벨
        [f"{total}", f"{win_rate:.2f}%", f"{wins}", f"{losses}"], # 2행: 값
        ["선공 수", "후공 수", "선공 확률", "후공 확률"], # 3행: 라벨
        [f"{f_count}", f"{s_count}", f"{(f_count/total*100):.2f}%", f"{(s_count/total*100):.2f}%"], # 4행: 값
        ["선공일 때 승리 수", "패배 수", "선공일 때 승률", "선공일 때 패배율"], # 5행: 라벨
        [f"{f_wins}", f"{f_losses}", f"{f_win_rate:.2f}%", f"{(100-f_win_rate):.2f}%"], # 6행: 값
        ["후공일 때 승리 수", "패배 수", "후공일 때 승률", "후공일 때 패배율"], # 7행: 라벨
        [f"{s_wins}", f"{s_losses}", f"{s_win_rate:.2f}%", f"{(100-s_win_rate):.2f}%"]  # 8행: 값
    ]
    return pd.DataFrame(data)

# --- 4. 메인 로직 및 페이지 분기 ---
st.sidebar.title("🎮 Rating 메뉴")
page = st.sidebar.radio("이동할 페이지", ["📊 기록", "📈 분석", "⚙️ 설정"])

if page == "📊 기록":
    st.title("📊 전적 기록")
    if 'df' not in st.session_state:
        st.session_state.df = load_records()
    
    df = st.session_state.df
    
    if st.button("➕ 새로운 경기 추가"):
        new_no = int(df["NO."].max() + 1) if not df.empty else 1
        new_row = pd.DataFrame([{"NO.": new_no, "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"), "선후공": "선", "결과": "승", "내 덱": st.session_state.metadata["my_decks"][0], "상대 덱": st.session_state.metadata["opp_decks"][0], "브릭": False, "실수": False}])
        st.session_state.df = pd.concat([df, new_row], ignore_index=True)
        st.rerun()

    edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic", hide_index=True, key="rating_editor")

    if st.button("💾 데이터 저장", type="primary"):
        st.session_state.df = edited_df
        st.session_state.df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.success("저장 완료!")

elif page == "📈 분석":
    st.title("📈 Rating Analysis")
    df_for_analysis = load_records()
    
    if df_for_analysis.empty:
        st.warning("분석할 전적 데이터가 없습니다.")
    else:
        st.subheader("1. Overall Data")
        st.table(create_analysis_table(df_for_analysis))

        st.divider()

        st.subheader("2. 내 덱별 상세 분석")
        selected_deck = st.selectbox("분석할 덱 선택", st.session_state.metadata["my_decks"])
        deck_df = df_for_analysis[df_for_analysis['내 덱'] == selected_deck]
        
        if deck_df.empty:
            st.info(f"'{selected_deck}' 덱의 기록이 없습니다.")
        else:
            st.table(create_analysis_table(deck_df))

else: # ⚙️ 설정 페이지
    st.title("⚙️ Rating 설정")
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
