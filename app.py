import streamlit as st
import pandas as pd
import os
import json

# --- 1. 설정 및 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Match Tracker", layout="wide")

# --- 2. [디자인] 분석 페이지 1/3 너비 유지용 CSS ---
st.markdown("""
    <style>
    .analysis-wrapper { width: 33.3%; min-width: 450px; }
    .styled-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 14px; }
    .styled-table th { background-color: #f9cb9c !important; padding: 8px; border: 1px solid #dee2e6; color: black; }
    .styled-table td { padding: 8px; border: 1px solid #dee2e6; text-align: center; }
    .win-text { color: blue; font-weight: bold; }
    .loss-text { color: red; font-weight: bold; }
    
    /* 에디터 높이 최적화 */
    [data-testid="stDataFrameResizable"] { min-height: 600px; }
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

# --- 4. 메인 로직 ---
if 'metadata' not in st.session_state: st.session_state.metadata = load_metadata()
if 'df' not in st.session_state: st.session_state.df = load_records()

menu = st.sidebar.radio("메뉴", ["📊 기록", "📈 분석", "⚙️ 설정"])

if menu == "📊 기록":
    st.title("📊 Match Records")
    
    # [데이터 가공] 출력용 데이터에 이모지 추가 (이미지 양식 재현)
    display_df = st.session_state.df.copy()
    
    if st.button("➕ 새로운 경기 추가"):
        m = st.session_state.metadata
        new_data = {
            "NO.": str(len(st.session_state.df) + 1), "날짜": pd.Timestamp.now().strftime("%m.%d"),
            "선후공": "선", "결과": "승", "세트 전적": "OO",
            "내 덱": m["my_decks"][0], "상대 덱": m["opp_decks"][0],
            "아키타입": m["archetypes"][0], "승패 요인": m["win_loss_reasons"][0],
            "특정 카드": m["target_cards"][0], "브릭": False, "실수": False, "비고": ""
        }
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_data])], ignore_index=True)
        st.session_state.df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.rerun()

    # 에디터 설정
    edited_df = st.data_editor(
        st.session_state.df, 
        use_container_width=True, 
        hide_index=True,
        num_rows="dynamic",
        column_config={
            # alignment="center"를 통해 중앙 정렬 강제 적용
            "NO.": st.column_config.TextColumn(alignment="center"),
            "날짜": st.column_config.TextColumn(alignment="center"),
            "선후공": st.column_config.SelectboxColumn(options=["선", "후"], alignment="center"),
            "결과": st.column_config.SelectboxColumn(options=["승", "패"], alignment="center"),
            "세트 전적": st.column_config.SelectboxColumn(options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"], alignment="center"),
            "내 덱": st.column_config.SelectboxColumn(options=st.session_state.metadata["my_decks"], alignment="center"),
            "상대 덱": st.column_config.SelectboxColumn(options=st.session_state.metadata["opp_decks"], alignment="center"),
            "아키타입": st.column_config.SelectboxColumn(options=st.session_state.metadata["archetypes"], alignment="center"),
            "승패 요인": st.column_config.SelectboxColumn(options=st.session_state.metadata["win_loss_reasons"], alignment="center"),
            "특정 카드": st.column_config.SelectboxColumn(options=st.session_state.metadata["target_cards"], alignment="center"),
            "브릭": st.column_config.CheckboxColumn(alignment="center"),
            "실수": st.column_config.CheckboxColumn(alignment="center"),
            "비고": st.column_config.TextColumn(width="large")
        },
        key="editor"
    )

    if not edited_df.equals(st.session_state.df):
        st.session_state.df = edited_df
        edited_df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.rerun()
elif menu == "📈 분석":
    st.title("📈 Rating Analysis")
    if not st.session_state.df.empty:
        st.markdown('<div class="analysis-wrapper">', unsafe_allow_html=True)
        st.markdown(render_styled_table("Overall Data", st.session_state.df), unsafe_allow_html=True)
        
        sel_deck = st.selectbox("내 덱 선택", st.session_state.metadata["my_decks"])
        st.markdown(render_styled_table(f"Deck: {sel_deck}", st.session_state.df[st.session_state.df['내 덱']==sel_deck]), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title("⚙️ 설정 (자동 저장)")
    m = st.session_state.metadata
    col1, col2 = st.columns(2)
    with col1:
        u_my = st.text_area("내 덱 (쉼표 구분)", ", ".join(m["my_decks"]))
        u_opp = st.text_area("상대 덱 (쉼표 구분)", ", ".join(m["opp_decks"]))
    with col2:
        u_ar = st.text_area("아키타입", ", ".join(m["archetypes"]))
        u_re = st.text_area("승패 요인", ", ".join(m["win_loss_reasons"]))
    
    new_meta = {
        "my_decks": [x.strip() for x in u_my.split(",") if x.strip()],
        "opp_decks": [x.strip() for x in u_opp.split(",") if x.strip()],
        "archetypes": [x.strip() for x in u_ar.split(",") if x.strip()],
        "win_loss_reasons": [x.strip() for x in u_re.split(",") if x.strip()],
        "target_cards": m["target_cards"]
    }
    if new_meta != m:
        st.session_state.metadata = new_meta
        save_metadata(new_meta)
        st.toast("설정이 변경되었습니다.")
