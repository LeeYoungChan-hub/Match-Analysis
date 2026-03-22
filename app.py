import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# --- 1. 파일 경로 설정 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating System", layout="wide")

# 🔥 [UI 최적화] 중앙 정렬 및 불필요 요소 제거 CSS
st.markdown("""
    <style>
    [data-testid="stTableIdxColumn"] { display: none; }
    .st-ae svg { display: none !important; }
    [data-testid="stDataEditorToolbar"] { display: none; }
    div[data-testid="stDataFrame"] div[role="gridcell"] > div {
        justify-content: center !important;
        text-align: center !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 데이터 처리 함수 (메타데이터 보존 핵심) ---
def load_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # 누락된 필드가 있을 경우 기본값으로 채움
                default = {
                    "my_decks": ["KT", "Ennea", "Maliss", "Tenpai"],
                    "opp_decks": ["KT", "Ennea", "Maliss", "Tenpai", "Labrynth", "Branded"],
                    "archetypes": ["운영", "전개", "미드레인지", "함떡", "기타"],
                    "target_cards": ["증식의 G", "하루 우라라", "무한포영", "니비루", "드롤"],
                    "win_loss_reasons": ["자신 실력", "상대 패", "특정 카드", "핸드 말림", "기타"]
                }
                for key, val in default.items():
                    if key not in data: data[key] = val
                return data
            except: pass
    return {
        "my_decks": ["KT", "Ennea", "Maliss", "Tenpai"],
        "opp_decks": ["KT", "Ennea", "Maliss", "Tenpai", "Labrynth", "Branded"],
        "archetypes": ["운영", "전개", "미드레인지", "함떡", "기타"],
        "target_cards": ["증식의 G", "하루 우라라", "무한포영", "니비루", "드롤"],
        "win_loss_reasons": ["자신 실력", "상대 패", "특정 카드", "핸드 말림", "기타"]
    }

def save_metadata(data):
    with open(META_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_records():
    # 사용자가 업로드한 CSV의 컬럼명 규격에 맞춤
    cols = ["NO.", "날짜", "선후공", "결과", "세트 전적", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        try:
            df = pd.read_csv(RECORD_FILE)
            # 기존 '매치 상세'가 있다면 '세트 전적'으로 통일
            if '매치 상세' in df.columns: df = df.rename(columns={'매치 상세': '세트 전적'})
            for col in cols:
                if col not in df.columns:
                    df[col] = "미지정" if col not in ["브릭", "실수"] else False
            return df.reindex(columns=cols)
        except: pass
    return pd.DataFrame(columns=cols)

# 세션 상태 초기화
if 'metadata' not in st.session_state: st.session_state.metadata = load_metadata()
if 'df' not in st.session_state: st.session_state.df = load_records()

# --- 3. 사이드바 메뉴 ---
st.sidebar.title("🎮 Rating 메뉴")
page = st.sidebar.radio("이동할 페이지", ["📊 Rating (기록)", "📈 Rating (분석)", "⚙️ Rating (설정)"])

# ---------------------------------------------------------
# [페이지 1] Rating (기록)
# ---------------------------------------------------------
if page == "📊 Rating (기록)":
    st.title("📊 Rating: 전적 기록")
    df = st.session_state.df
    
    if st.button("➕ 새로운 경기 추가"):
        new_no = int(df["NO."].max() + 1) if not df.empty and pd.to_numeric(df["NO."], errors='coerce').notnull().any() else 1
        new_row = pd.DataFrame([{
            "NO.": new_no, "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"), 
            "선후공": "선", "결과": "승", "세트 전적": "OO",
            "내 덱": st.session_state.metadata["my_decks"][0], 
            "상대 덱": st.session_state.metadata["opp_decks"][0],
            "아키타입": st.session_state.metadata["archetypes"][0], 
            "특정 카드": st.session_state.metadata["target_cards"][0], 
            "승패 요인": st.session_state.metadata["win_loss_reasons"][0],
            "실수": False, "브릭": False, "비고": ""
        }])
        st.session_state.df = pd.concat([df, new_row], ignore_index=True)
        st.rerun()

    # 메타데이터를 기반으로 한 드롭다운 설정
    edited_df = st.data_editor(
        st.session_state.df, 
        use_container_width=True, 
        num_rows="dynamic",
        hide_index=True,
        key="rating_editor_v7",
        column_config={
            "NO.": st.column_config.NumberColumn("No.", disabled=True, width="small"),
            "선후공": st.column_config.SelectboxColumn("선/후", options=["선", "후"], width="small"),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"], width="small"),
            "세트 전적": st.column_config.SelectboxColumn("세트", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"]),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata["my_decks"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata["opp_decks"]),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.metadata["archetypes"]),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.metadata["target_cards"]),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.metadata["win_loss_reasons"]),
            "브릭": st.column_config.CheckboxColumn("브릭"),
            "실수": st.column_config.CheckboxColumn("실수")
        }
    )

    if st.button("💾 Rating 데이터 저장", type="primary"):
        st.session_state.df = edited_df
        st.session_state.df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.success("데이터가 안전하게 저장되었습니다!")

# ---------------------------------------------------------
# [페이지 2] Rating (분석)
# ---------------------------------------------------------
elif page == "📈 Rating (분석)":
    st.title("📈 Rating Analysis")
    df = st.session_state.df
    
    if df.empty or len(df) < 1:
        st.warning("분석할 데이터가 없습니다.")
    else:
        # 지표 계산 (문자열 등이 섞여있을 경우 대비)
        df['결과_val'] = df['결과'].apply(lambda x: 1 if x == '승' else 0)
        total_games = len(df)
        win_rate = (df['결과_val'].mean() * 100)
        brick_count = pd.to_numeric(df['브릭'], errors='coerce').fillna(0).sum()
        mistake_count = pd.to_numeric(df['실수'], errors='coerce').fillna(0).sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 매치", f"{total_games}회")
        m2.metric("전체 승률", f"{win_rate:.1f}%")
        m3.metric("누적 브릭", f"{int(brick_count)}회")
        m4.metric("누적 실수", f"{int(mistake_count)}회")

        st.divider()
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 내 덱별 성능")
            my_stats = df.groupby('내 덱')['결과_val'].mean().reset_index()
            fig_my = px.bar(my_stats, x='내 덱', y='결과_val', labels={'결과_val':'승률'}, color='결과_val', color_continuous_scale='Blues')
            st.plotly_chart(fig_my, use_container_width=True)
            
        with c2:
            st.subheader("🚩 승패 요인 비중")
            reason_data = df['승패 요인'].value_counts().reset_index()
            fig_pie = px.pie(reason_data, values='count', names='승패 요인', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("⚔️ 상대 덱별 상성 (Top 10)")
        opp_summary = df.groupby('상대 덱').agg(
            경기수=('결과', 'count'),
            승률=('결과_val', lambda x: f"{x.mean()*100:.1f}%")
        ).sort_values(by='경기수', ascending=False).head(10)
        st.table(opp_summary)

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
