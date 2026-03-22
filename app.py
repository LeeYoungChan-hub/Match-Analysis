import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="Rating", layout="wide")

# 🔥 [UI 최적화] 중앙 정렬 및 불필요 요소 제거 CSS
st.markdown("""
    <style>
    [data-testid="stTableIdxColumn"] { display: none; }
    .st-ae svg { display: none !important; }
    [data-testid="stDataEditorToolbar"] { display: none; }
    
    /* 표 내부 텍스트 중앙 정렬 시도 */
    div[data-testid="stDataFrame"] div[role="gridcell"] > div {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
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
    cols = ["NO.", "날짜", "선후공", "결과", "세트 전적", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        try:
            df = pd.read_csv(RECORD_FILE)
            # CSV의 '세트 전적' 등 컬럼명 동기화
            df = df.rename(columns={'매치 상세': '세트 전적'})
            for col in cols:
                if col not in df.columns:
                    df[col] = "미지정" if col not in ["브릭", "실수"] else False
            return df.reindex(columns=cols)
        except: pass
    return pd.DataFrame(columns=cols)

# 세션 초기화
if 'metadata' not in st.session_state: st.session_state.metadata = load_metadata()
if 'df' not in st.session_state: st.session_state.df = load_records()

# --- 3. 사이드바 메뉴 (Analysis 추가) ---
st.sidebar.title("🎮 Rating 메뉴")
page = st.sidebar.radio("이동할 페이지", ["📊 Rating (기록)", "📈 Analysis (분석)", "⚙️ Rating (설정)"])

# ---------------------------------------------------------
# [페이지 1] Rating (기록) - 기존과 동일
# ---------------------------------------------------------
if page == "📊 Rating (기록)":
    st.title("📊 Rating: 전적 기록")
    df = st.session_state.df
    
    if st.button("➕ 새로운 경기 추가"):
        new_no = df["NO."].max() + 1 if not df.empty else 1
        new_row = pd.DataFrame([{"NO.": new_no, "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"), "선후공": "선", "결과": "승", "세트 전적": "OO", "내 덱": st.session_state.metadata["my_decks"][0], "상대 덱": st.session_state.metadata["opp_decks"][0], "브릭": False, "실수": False}])
        st.session_state.df = pd.concat([df, new_row], ignore_index=True)
        st.rerun()

    edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic", hide_index=True, key="rating_edit",
                               column_config={"세트 전적": st.column_config.SelectboxColumn("세트", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"])})

    if st.button("💾 데이터 저장", type="primary"):
        st.session_state.df = edited_df
        st.session_state.df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.success("저장 완료!")

# ---------------------------------------------------------
# [페이지 2] Analysis (분석) - 신규 추가
# ---------------------------------------------------------
elif page == "📈 Analysis (분석)":
    st.title("📈 Rating Analysis")
    df = st.session_state.df
    
    if df.empty:
        st.warning("분석할 데이터가 없습니다. 먼저 기록을 추가해주세요.")
    else:
        # 상단 핵심 지표
        total = len(df)
        win_df = df[df['결과'] == '승']
        win_rate = (len(win_df) / total * 100)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("총 경기 수", f"{total}회")
        c2.metric("승률", f"{win_rate:.2f}%")
        c3.metric("브릭 횟수", f"{df['브릭'].sum()}회")
        c4.metric("실수 횟수", f"{df['실수'].sum()}회")

        st.divider()

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("🃏 내 덱별 승률")
            deck_stats = df.groupby('내 덱')['결과'].value_counts(normalize=True).unstack().fillna(0)
            if '승' in deck_stats.columns:
                fig_deck = px.bar(deck_stats, y='승', color_discrete_sequence=['#00CC96'], labels={'승': '승률'})
                st.plotly_chart(fig_deck, use_container_width=True)

        with col_right:
            st.subheader("🚩 승패 요인 분석")
            reason_counts = df['승패 요인'].value_counts().reset_index()
            fig_reason = px.pie(reason_counts, values='count', names='승패 요인', hole=0.4)
            st.plotly_chart(fig_reason, use_container_width=True)

        st.subheader("⚔️ 상대 덱별 상세 전적")
        opp_stats = df.groupby('상대 덱').agg(
            경기수=('NO.', 'count'),
            승리=('결과', lambda x: (x == '승').sum()),
            패배=('결과', lambda x: (x == '패').sum())
        )
        opp_stats['승률'] = (opp_stats['승리'] / opp_stats['경기수'] * 100).map('{:.1f}%'.format)
        st.table(opp_stats.sort_values(by='경기수', ascending=False))
def create_4_row_table(target_df):
    total = len(target_df)
    if total == 0: return pd.DataFrame([["데이터 없음"]], columns=["상태"])

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

    # 요청하신 4줄 레이아웃 데이터
    data = [
        ["게임 수", f"{total}회", "전체 승률", f"{win_rate:.2f}%", "전체 승리수", f"{wins}승", "전체 패배수", f"{losses}패"],
        ["선공 수", f"{f_count}회", "후공 수", f"{s_count}회", "선공 확률", f"{(f_count/total*100):.1f}%", "후공 확률", f"{(s_count/total*100):.1f}%"],
        ["선공 승리 수", f"{f_wins}회", "선공 패배 수", f"{f_losses}회", "선공 승률", f"{f_win_rate:.1f}%", "선공 패배율", f"{(100-f_win_rate):.1f}%"],
        ["후공 승리 수", f"{s_wins}회", "후공 패배 수", f"{s_losses}회", "후공 승률", f"{s_win_rate:.1f}%", "후공 패배율", f"{(100-s_win_rate):.1f}%"]
    ]
    return pd.DataFrame(data)
# ---------------------------------------------------------
# [페이지 3] Rating (설정) - 신규 추가
# ---------------------------------------------------------
else:  # ⚙️ Rating (설정)
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
        st.session_state.metadata = {
            "my_decks": [x.strip() for x in new_my.split(",") if x.strip()],
            "opp_decks": [x.strip() for x in new_opp.split(",") if x.strip()],
            "archetypes": [x.strip() for x in new_arche.split(",") if x.strip()],
            "win_loss_reasons": [x.strip() for x in new_reasons.split(",") if x.strip()],
            "target_cards": [x.strip() for x in new_cards.split(",") if x.strip()]
        }
        with open(META_FILE, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.metadata, f, ensure_ascii=False, indent=4)
        st.success("설정이 저장되었습니다!")
        st.rerun()
