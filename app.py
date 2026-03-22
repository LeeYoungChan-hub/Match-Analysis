import streamlit as st
import pandas as pd
import os
import json
import plotly.express as px

# --- 1. [수정] 파일 경로 변경 (새 파일로 시작) ---
# 기존 파일 이름이 아닌 새로운 이름을 사용하면 깨끗하게 시작됩니다.
RECORD_FILE = 'ygo_data.csv' 
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. [디자인] CSS (깔끔한 헤더 유지) ---
st.markdown("""
    <style>
    [data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"] div { 
        text-align: center !important; 
        font-size: 13px !important; 
    }
    thead tr th {
        background-color: #f2f2f2 !important;
        font-weight: bold !important;
        text-align: center !important;
    }
    textarea, input { spellcheck: false !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 관리 함수 ---
def load_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "my_decks": ["KT", "Ennea"], "opp_decks": ["Mitsu", "Branded", "Tenpai"],
        "archetypes": ["운영", "전개"], "win_loss_reasons": ["실력", "패사고"], "target_cards": ["Nibiru"]
    }

def save_metadata(meta):
    with open(META_FILE, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=4)

def load_records():
    cols = ["NO.", "날짜", "선후공", "결과", "세트", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE, dtype=str).fillna("")
        # 불러올 때 가짜 요약 데이터(경기, Date 등)가 포함된 행은 무조건 제외
        df = df[~df['NO.'].astype(str).str.contains("경기|Date", na=False)]
        for col in ["브릭", "실수"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(x).lower() in ['true', '1'])
        return df.reset_index(drop=True)
    return pd.DataFrame(columns=cols)

def save_records(df):
    df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
    st.session_state.df = df.reset_index(drop=True)

# --- 4. 앱 메인 ---
if 'metadata' not in st.session_state: st.session_state.metadata = load_metadata()
if 'df' not in st.session_state: st.session_state.df = load_records()

page = st.sidebar.radio("메뉴", ["📊 Record", "📈 Analysis", "🖼️ Graph", "⚙️ Setting"])

# --- PAGE: Record ---
if page == "📊 Record":
    st.title("📊 Match Record")
    
    # 1. 추가 버튼
    if st.button("➕ 새로운 경기 추가"):
        new_no = str(len(st.session_state.df) + 1)
        new_row = pd.DataFrame([{
            "NO.": new_no, "날짜": "", "선후공": "", "결과": "", "세트": "", "점수": "", 
            "내 덱": "", "상대 덱": "", "아키타입": "", "승패 요인": "", "특정 카드": "", 
            "브릭": False, "실수": False, "비고": ""
        }])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        save_records(st.session_state.df)
        st.rerun()

    # 2. [클린 버전] 데이터 에디터 (요약 행 일절 없음)
    edited = st.data_editor(
        st.session_state.df, 
        use_container_width=True, 
        num_rows="dynamic", 
        hide_index=True, 
        key="clean_ygo_editor",
        height=800,
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width=50),
            "날짜": st.column_config.TextColumn("날짜", width=90),
            "선후공": st.column_config.SelectboxColumn("선후공", options=["", "선", "후"], width=70),
            "결과": st.column_config.SelectboxColumn("결과", options=["", "승", "패"], width=70),
            "세트": st.column_config.SelectboxColumn("세트", options=["", "OO", "OXO", "XOO", "XX", "XOX", "OXX"], width=90),
            "점수": st.column_config.TextColumn("점수", width=60),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=[""] + st.session_state.metadata["my_decks"], width=120),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=[""] + st.session_state.metadata["opp_decks"], width=130),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=[""] + st.session_state.metadata["archetypes"], width=110),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=[""] + st.session_state.metadata["win_loss_reasons"], width=110),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=[""] + st.session_state.metadata["target_cards"], width=110),
            "브릭": st.column_config.CheckboxColumn("브릭", width=60), 
            "실수": st.column_config.CheckboxColumn("실수", width=60),
            "비고": st.column_config.TextColumn("비고", width=400)
        }
    )

    # 3. 실시간 저장
    if not edited.equals(st.session_state.df):
        save_records(edited)
        st.rerun()

# --- Analysis, Graph, Setting (기존 로직 유지) ---
elif page == "📈 Analysis":
    st.title("📈 Rating Analysis")
    df_ana = load_records()
    # 기존 코드 내용 유지...
    st.info("기존 분석 페이지의 테이블 렌더링 함수들을 호출하세요.")

elif page == "🖼️ Graph":
    st.title("🖼️ Graph")
    # 기존 그래프 로직 유지...

elif page == "⚙️ Setting":
    st.title("⚙️ Setting")
    # 기존 설정 로직 유지...

elif page == "📈 Analysis":
    st.title("📈 Rating Analysis")
    df_ana = load_records()
    if not df_ana.empty:
        st.markdown('<div class="analysis-wrapper">', unsafe_allow_html=True)
        st.markdown(render_styled_table("Overall Data", df_ana), unsafe_allow_html=True)
        
        st.subheader("덱별 승률")
        sel_my = st.selectbox("내 덱 선택", st.session_state.metadata["my_decks"], label_visibility="collapsed")
        st.markdown(render_styled_table(sel_my, df_ana[df_ana['내 덱'] == sel_my]), unsafe_allow_html=True)
        
        st.subheader("상대 덱별 승률")
        c1, c2 = st.columns(2)
        with c1: m_my = st.selectbox("Use.Deck", st.session_state.metadata["my_decks"], label_visibility="collapsed", key="m_my")
        with c2: m_opp = st.selectbox("Opp.Deck", st.session_state.metadata["opp_decks"], label_visibility="collapsed", key="m_opp")
        st.markdown(render_styled_table("결과", df_ana[(df_ana['내 덱']==m_my) & (df_ana['상대 덱']==m_opp)]), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title("⚙️ Setting")
    meta = st.session_state.metadata
    c1, c2 = st.columns(2)
    with c1: new_my = st.text_area("내 덱 (쉼표 구분)", ", ".join(meta.get("my_decks", [])))
    with c2: new_opp = st.text_area("상대 덱 (쉼표 구분)", ", ".join(meta.get("opp_decks", [])))
    c3, c4 = st.columns(2)
    with c3: new_reasons = st.text_area("승패 요인 (쉼표 구분)", ", ".join(meta.get("win_loss_reasons", [])))
    with c4: new_arche = st.text_area("아키타입 (쉼표 구분)", ", ".join(meta.get("archetypes", [])))
    c5, _ = st.columns(2)
    with c5: new_cards = st.text_area("특정 카드 (쉼표 구분)", ", ".join(meta.get("target_cards", [])))
    
    if st.button("✅ 설정 저장"):
        st.session_state.metadata = {
            "my_decks": [x.strip() for x in new_my.split(",") if x.strip()],
            "opp_decks": [x.strip() for x in new_opp.split(",") if x.strip()],
            "win_loss_reasons": [x.strip() for x in new_reasons.split(",") if x.strip()],
            "archetypes": [x.strip() for x in new_arche.split(",") if x.strip()],
            "target_cards": [x.strip() for x in new_cards.split(",") if x.strip()]
        }
        with open(META_FILE, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.metadata, f, ensure_ascii=False, indent=4)
        st.success("설정 저장 완료!")
        st.rerun()
