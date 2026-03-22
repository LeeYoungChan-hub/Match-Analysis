import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Match Tracker", layout="wide")

# --- 2. [핵심 수정] 기록 페이지 전용 이미지 박멸 및 색상 적용 CSS ---
st.markdown("""
    <style>
    /* 1. 시스템 인덱스 열(0,1,2...) 및 편집 아이콘 완전 숨김 (박멸 유지) */
    [data-testid="stTableIdxColumn"] { display: none !important; width: 0px !important; }
    
    /* 2. NO. 칸의 연필 아이콘과 줄 3개 핸들 투명화 */
    [data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"] div:first-child svg {
        display: none !important;
    }

    /* 3. 컬럼별 글자/배경 색상 정의 (핵심 로직 - 이미지 완벽 재현) */
    
    /* [기록 페이지 헤더] 글자 굵게 */
    div.row-widget.stDataFrame [data-testid="stTableIdxColumn"]+th {
        font-weight: bold;
    }

    /* [NO. (B열) - 기본(검은색) 정렬 최적화] */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(1) {
        text-align: center !important;
        color: #31333F !important;
    }

    /* [날짜 (C열) - 연한 회색 배경] */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(2) {
        background-color: #f4f4f4 !important;
        text-align: center !important;
    }

    /* [선후공 (D열) - 선:파란색, 후:빨간색] */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(3):contains("선") { color: #0000ff !important; font-weight: bold; text-align: center !important; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(3):contains("후") { color: #ff0000 !important; font-weight: bold; text-align: center !important; }

    /* [결과 (E열) - 승:파란색, 패:빨간색] */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(4):contains("승") { color: #0000ff !important; font-weight: bold; text-align: center !important; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(4):contains("패") { color: #ff0000 !important; font-weight: bold; text-align: center !important; }

    /* [세트 전적 (F열) - 승리케이스:파란색, 패배케이스:빨간색] */
    /* 승리 케이스 */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("OO") { color: #0000ff !important; font-weight: bold; text-align: center !important; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("OXO") { color: #0000ff !important; font-weight: bold; text-align: center !important; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("XOO") { color: #0000ff !important; font-weight: bold; text-align: center !important; }
    /* 패배 케이스 */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("XX") { color: #ff0000 !important; font-weight: bold; text-align: center !important; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("XOX") { color: #ff0000 !important; font-weight: bold; text-align: center !important; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("OXX") { color: #ff0000 !important; font-weight: bold; text-align: center !important; }

    /* [나머지 정보 (G~J열) - 검은색 정렬] */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(n+6):nth-child(-n+10) {
        text-align: center !important;
        color: #31333F !important;
    }

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
        color: #31333F !important;
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
def load_metadata():
    default_meta = {
        "my_decks": ["KT", "Ennea", "Maliss", "Tenpai"],
        "opp_decks": ["KT", "Ennea", "Maliss", "Tenpai", "Labrynth", "Branded"],
        "archetypes": ["운영", "전개", "미드레인지", "함떡", "기타"],
        "win_loss_reasons": ["상대 패", "자신 실력", "특정 카드", "핸드 말림", "기타"],
        "target_cards": ["증식의 G", "하루 우라라", "무한포영", "니비루", "드롤"]
    }
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            try:
                saved = json.load(f)
                for key in default_meta:
                    if key not in saved: saved[key] = default_meta[key]
                return saved
            except: pass
    return default_meta

def load_records():
    # 이미지와 동일한 순서의 컬럼 정의
    cols = ["NO.", "날짜", "선후공", "결과", "세트 전적", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        try:
            df = pd.read_csv(RECORD_FILE, dtype=str).fillna("")
            for col in cols:
                if col not in df.columns: df[col] = ""
            for col in ["브릭", "실수"]:
                df[col] = df[col].apply(lambda x: True if str(x).lower() in ['true', '1'] else False)
            return df[cols].reset_index(drop=True)
        except: pass
    return pd.DataFrame(columns=cols)

def save_data(df):
    # 인덱스 없이 저장
    df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
    st.session_state.df = df.reset_index(drop=True)

# 분석 표 렌더링 함수 (기존 유지)
def render_styled_table(title, target_df):
    calc_df = target_df[target_df['결과'].isin(['승', '패'])]
    total = len(calc_df)
    if total == 0:
        return f'<table class="styled-table"><tr><th>{title}</th></tr><tr><td>데이터 없음</td></tr></table>'
    wins = len(calc_df[calc_df['결과'] == '승'])
    losses = len(calc_df[calc_df['결과'] == '패'])
    win_rate = (wins / total * 100)
    f_df, s_df = calc_df[calc_df['선후공'] == '선'], calc_df[calc_df['선후공'] == '후']
    f_wins = len(f_df[f_df['결과'] == '승'])
    s_wins = len(s_df[s_df['결과'] == '승'])
    return f"""
        <table class="styled-table">
            <tr><th colspan="5">{title}</th></tr>
            <tr><th>Overall</th><th>Games</th><th>Win Rate</th><th>W</th><th>L</th></tr>
            <tr><td>Result</td><td>{total}</td><td>{win_rate:.2f}%</td><td class="win-val">{wins}</td><td class="loss-val">{losses}</td></tr>
            <tr><th>Coin</th><th>1st</th><th>2nd</th><th>1st Rate</th><th>2nd Rate</th></tr>
            <tr><td>Result</td><td class="win-val">{len(f_df)}</td><td class="loss-val">{len(s_df)}</td><td class="win-val">{(len(f_df)/total*100):.1f}%</td><td class="loss-val">{(len(s_df)/total*100):.1f}%</td></tr>
            <tr><th>1st</th><th>1st Win</th><th>1st Lose</th><th>1st W%</th><th>1st L%</th></tr>
            <tr><td>Result</td><td class="win-val">{f_wins}</td><td class="loss-val">{len(f_df)-f_wins}</td><td class="win-val">{(f_wins/len(f_df)*100 if len(f_df)>0 else 0):.1f}%</td><td class="loss-val">{(100-(f_wins/len(f_df)*100) if len(f_df)>0 else 0):.1f}%</td></tr>
            <tr><th>2nd</th><th>2nd Win</th><th>2nd Lose</th><th>2nd W%</th><th>2nd L%</th></tr>
            <tr><td>Result</td><td class="win-val">{s_wins}</td><td class="loss-val">{len(s_df)-s_wins}</td><td class="win-val">{(s_wins/len(s_df)*100 if len(s_df)>0 else 0):.1f}%</td><td class="loss-val">{(100-(s_wins/len(s_df)*100) if len(s_df)>0 else 0):.1f}%</td></tr>
        </table>
    """

# --- 4. 메인 로직 ---
if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()
if 'df' not in st.session_state:
    st.session_state.df = load_records()

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

    # 데이터 에디터 실행 (디자인 및 색상 CSS 적용)
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
