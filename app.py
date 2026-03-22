import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Match Tracker", layout="wide")

# --- 2. [강력 수정] CSS: 중앙 정렬 및 색상 강제 주입 ---
# 데이터 에디터 내부의 텍스트를 직접 타겟팅합니다.
st.markdown("""
    <style>
    /* 시스템 요소 숨기기 */
    [data-testid="stTableIdxColumn"] { display: none !important; }
    
    /* [핵심] 모든 셀 중앙 정렬 및 폰트 설정 */
    div[data-testid="stDataFrameResizable"] div[role="gridcell"] > div {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
    }

    /* 승리/선공 관련 텍스트 파란색 */
    div[data-testid="stDataFrameResizable"] div[role="gridcell"]:has(div:contains("승")),
    div[data-testid="stDataFrameResizable"] div[role="gridcell"]:has(div:contains("선")),
    div[data-testid="stDataFrameResizable"] div[role="gridcell"]:has(div:contains("OO")),
    div[data-testid="stDataFrameResizable"] div[role="gridcell"]:has(div:contains("OXO")),
    div[data-testid="stDataFrameResizable"] div[role="gridcell"]:has(div:contains("XOO")) {
        color: #0000FF !important;
        font-weight: bold !important;
    }

    /* 패배/후공 관련 텍스트 빨간색 */
    div[data-testid="stDataFrameResizable"] div[role="gridcell"]:has(div:contains("패")),
    div[data-testid="stDataFrameResizable"] div[role="gridcell"]:has(div:contains("후")),
    div[data-testid="stDataFrameResizable"] div[role="gridcell"]:has(div:contains("XX")),
    div[data-testid="stDataFrameResizable"] div[role="gridcell"]:has(div:contains("XOX")),
    div[data-testid="stDataFrameResizable"] div[role="gridcell"]:has(div:contains("OXX")) {
        color: #FF0000 !important;
        font-weight: bold !important;
    }

    /* 분석 페이지 1/3 너비 */
    .analysis-wrapper { width: 33.3%; min-width: 400px; }
    .styled-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    .styled-table th { background-color: #f9cb9c; padding: 8px; border: 1px solid #dee2e6; }
    .styled-table td { padding: 8px; border: 1px solid #dee2e6; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 로직 ---
def load_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"my_decks": ["KT"], "opp_decks": ["KT"], "archetypes": ["운영"], "win_loss_reasons": ["실력"], "target_cards": ["G"]}

def save_metadata(meta):
    with open(META_FILE, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=4)

def load_records():
    cols = ["NO.", "날짜", "선후공", "결과", "세트 전적", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE, dtype=str).fillna("")
        for col in ["브릭", "실수"]:
            df[col] = df[col].apply(lambda x: str(x).lower() == 'true')
        return df[cols]
    return pd.DataFrame(columns=cols)

def save_records(df):
    df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')

# --- 4. 메인 로직 ---
if 'metadata' not in st.session_state: st.session_state.metadata = load_metadata()
if 'df' not in st.session_state: st.session_state.df = load_records()

menu = st.sidebar.radio("메뉴", ["📊 기록", "📈 분석", "⚙️ 설정"])

if menu == "📊 기록":
    st.title("📊 Match Records")
    
    if st.button("➕ 새로운 경기 추가"):
        m = st.session_state.metadata
        new_row = pd.DataFrame([{"NO.": str(len(st.session_state.df)+1), "날짜": pd.Timestamp.now().strftime("%m.%d"), "선후공": "선", "결과": "승", "세트 전적": "OO", "내 덱": m["my_decks"][0], "상대 덱": m["opp_decks"][0], "아키타입": m["archetypes"][0], "승패 요인": m["win_loss_reasons"][0], "특정 카드": m["target_cards"][0], "브릭": False, "실수": False, "비고": ""}])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        save_records(st.session_state.df)
        st.rerun()

    # 에러 방지를 위해 width 설정을 최소화하고 정렬은 CSS에 맡깁니다.
    edited_df = st.data_editor(
        st.session_state.df, 
        use_container_width=True, 
        num_rows="dynamic", 
        hide_index=True, 
        key="main_editor",
        column_config={
            "선후공": st.column_config.SelectboxColumn(options=["선", "후"]),
            "결과": st.column_config.SelectboxColumn(options=["승", "패"]),
            "세트 전적": st.column_config.SelectboxColumn(options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"]),
            "내 덱": st.column_config.SelectboxColumn(options=st.session_state.metadata["my_decks"]),
            "상대 덱": st.column_config.SelectboxColumn(options=st.session_state.metadata["opp_decks"]),
            "아키타입": st.column_config.SelectboxColumn(options=st.session_state.metadata["archetypes"]),
            "승패 요인": st.column_config.SelectboxColumn(options=st.session_state.metadata["win_loss_reasons"]),
            "특정 카드": st.column_config.SelectboxColumn(options=st.session_state.metadata["target_cards"]),
        }
    )
    
    if not edited_df.equals(st.session_state.df):
        st.session_state.df = edited_df
        save_records(edited_df)
        st.rerun()
elif menu == "📈 분석":
    st.title("📈 Rating Analysis")
    df = st.session_state.df
    if not df.empty:
        st.markdown('<div class="analysis-wrapper">', unsafe_allow_html=True)
        st.markdown(render_styled_table("Overall Data", df), unsafe_allow_html=True)
        
        st.subheader("덱별 승률")
        sel_my = st.selectbox("내 덱 선택", st.session_state.metadata["my_decks"], label_visibility="collapsed")
        st.markdown(render_styled_table(sel_my, df[df['내 덱'] == sel_my]), unsafe_allow_html=True)
        
        st.subheader("상대 덱별 승률")
        c1, c2 = st.columns(2)
        with c1: m_my = st.selectbox("Use.Deck", st.session_state.metadata["my_decks"], key="m1", label_visibility="collapsed")
        with c2: m_opp = st.selectbox("Opp.Deck", st.session_state.metadata["opp_decks"], key="m2", label_visibility="collapsed")
        st.markdown(render_styled_table(f"{m_my} vs {m_opp}", df[(df['내 덱']==m_my) & (df['상대 덱']==m_opp)]), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title("⚙️ Rating 설정")
    st.info("내용을 수정하면 자동으로 저장됩니다.")
    m = st.session_state.metadata
    
    # 텍스트 에어리어에서 변경 시 세션 및 파일 즉시 업데이트
    col1, col2 = st.columns(2)
    with col1:
        u_my = st.text_area("내 덱 리스트 (쉼표 구분)", ", ".join(m["my_decks"]))
        u_opp = st.text_area("상대 덱 리스트 (쉼표 구분)", ", ".join(m["opp_decks"]))
    with col2:
        u_re = st.text_area("승패 요인 리스트 (쉼표 구분)", ", ".join(m["win_loss_reasons"]))
        u_ar = st.text_area("아키타입 리스트 (쉼표 구분)", ", ".join(m["archetypes"]))
    
    u_ca = st.text_area("특정 카드 리스트 (쉼표 구분)", ", ".join(m["target_cards"]))

    new_meta = {
        "my_decks": [x.strip() for x in u_my.split(",") if x.strip()],
        "opp_decks": [x.strip() for x in u_opp.split(",") if x.strip()],
        "win_loss_reasons": [x.strip() for x in u_re.split(",") if x.strip()],
        "archetypes": [x.strip() for x in u_ar.split(",") if x.strip()],
        "target_cards": [x.strip() for x in u_ca.split(",") if x.strip()]
    }

    if new_meta != st.session_state.metadata:
        st.session_state.metadata = new_meta
        save_metadata(new_meta)
        st.toast("설정이 자동 저장되었습니다!")
