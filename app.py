import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Match Tracker", layout="wide")

# --- 2. [핵심 수정] 기록 페이지 디자인 강화 CSS (색상, 정렬, 체크박스) ---
st.markdown("""
    <style>
    /* 1. 시스템 인덱스 열(0,1,2...) 및 편집 아이콘 완전 숨김 (박멸 유지) */
    [data-testid="stTableIdxColumn"] { display: none !important; width: 0px !important; }
    [data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"] div:first-child svg {
        display: none !important;
    }

    /* 2. [기록 페이지 헤더] 글자 굵게 */
    div.row-widget.stDataFrame [data-testid="stTableIdxColumn"]+th {
        font-weight: bold;
    }

    /* 3. 컬럼별 글자/배경 색상 및 가운데 정렬 정의 (이미지 완벽 재현) */
    
    /* 전체 셀 가운데 정렬 (비고 제외) */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div {
        text-align: center !important;
        color: #31333F !important; /* 기본 검은색 */
    }

    /* [날짜 (B열) - 연한 회색 배경] */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(2) {
        background-color: #f4f4f4 !important;
    }

    /* [선후공 (C열) - 선:파란색, 후:빨간색] */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(3):contains("선") { color: #0000ff !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(3):contains("후") { color: #ff0000 !important; font-weight: bold; }

    /* [결과 (D열) - 승:파란색, 패:빨간색] */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(4):contains("승") { color: #0000ff !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(4):contains("패") { color: #ff0000 !important; font-weight: bold; }

    /* [세트 전적 (E열) - 승리케이스:파란색, 패배케이스:빨간색] */
    /* 승리 케이스 */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("OO") { color: #0000ff !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("OXO") { color: #0000ff !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("XOO") { color: #0000ff !important; font-weight: bold; }
    /* 패배 케이스 */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("XX") { color: #ff0000 !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("XOX") { color: #ff0000 !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("OXX") { color: #ff0000 !important; font-weight: bold; }

    /* [브릭 (K열) - 회색 체크박스] */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(11) input[type="checkbox"] {
        accent-color: #999999 !important; /* 회색 */
    }

    /* [실수 (L열) - 빨간색 체크박스] */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(12) input[type="checkbox"] {
        accent-color: #ff0000 !important; /* 빨간색 */
    }
    
    /* [비고 (M열) - 왼쪽 정렬 및 얇은 글씨] */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(13) {
        text-align: left !important;
        font-weight: normal !important;
    }

    /* [분석 페이지 레이아웃 (기존 유지)] */
    .analysis-wrapper { width: 33%; margin-left: 0; }
    .styled-table { 
        width: 100%; font-size: 14px; border-collapse: collapse; 
        margin-bottom: 30px; table-layout: fixed; border: 1px solid #dee2e6;
    }
    .styled-table th, .styled-table td { 
        text-align: center !important; border: 1px solid #dee2e6 !important; padding: 8px !important; 
    }
    .styled-table th { 
        background-color: #f9cb9c !important; color: #31333F !important; font-weight: bold !important; 
    }
    .win-val { color: #0000ff !important; font-weight: bold; }
    .loss-val { color: #ff0000 !important; font-weight: bold; }
    div[data-testid="stSelectbox"] { width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 로직 (생략 - 기존 코드 유지) ---
# load_metadata(), load_records(), save_data() 등은 그대로 사용합니다.

# --- 4. 메인 로직 ---
# (세션 관리 생략 - 기존 코드 유지)

page = st.sidebar.radio("메뉴", ["📊 기록", "📈 분석", "⚙️ 설정"])

if page == "📊 기록":
    st.title("📊 Match Records")
    if st.button("➕ 새로운 경기 추가"):
        meta = st.session_state.metadata
        new_row = pd.DataFrame([{
            "NO.": "", "날짜": pd.Timestamp.now().strftime("%m.%d"),
            "선후공": "선", "결과": "승", "세트 전적": "OO",
            "내 덱": meta["my_decks"][0], "상대 덱": meta["opp_decks"][0],
            "아키타입": meta["archetypes"][0], "승패 요인": meta["win_loss_reasons"][0],
            "특정 카드": meta["target_cards"][0], "브릭": False, "실수": False, "비고": ""
        }])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True).reset_index(drop=True)
        save_data(st.session_state.df)
        st.rerun()

    # 데이터 에디터 실행 (디자인 및 정렬 CSS 적용)
    edited_df = st.data_editor(
        st.session_state.df, 
        use_container_width=True, 
        num_rows="dynamic", 
        hide_index=True, # 시스템 인덱스 숨김
        key="ygo_editor_styled",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width="small"),
            "날짜": st.column_config.TextColumn("날짜", width="small"),
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"], width="small"),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"], width="small"),
            # 세트 전적 드롭다운 복구 및 옵션 지정
            "세트 전적": st.column_config.SelectboxColumn("세트 전적", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"], width="small"),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata.get("my_decks", [])),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata.get("opp_decks", [])),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.metadata.get("archetypes", [])),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.metadata.get("win_loss_reasons", [])),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.metadata.get("target_cards", [])),
            "브릭": st.column_config.CheckboxColumn("브릭", width="small"),
            "실수": st.column_config.CheckboxColumn("실수", width="small"),
            "비고": st.column_config.TextColumn("비고", width="large")
        }
    )

    if not edited_df.equals(st.session_state.df):
        save_data(edited_df)
        st.rerun()

elif page == "📈 분석":
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
    st.title("⚙️ Rating 설정")
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
