import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Match Tracker", layout="wide")

# --- 2. [디자인] 기록 페이지 색상/정렬 및 분석 레이아웃 CSS ---
st.markdown("""
    <style>
    /* [기록 페이지] 시스템 요소 숨기기 */
    [data-testid="stTableIdxColumn"] { display: none !important; width: 0px !important; }
    [data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"] div:first-child svg { display: none !important; }

    /* [기록 페이지] 전체 중앙 정렬 및 기본 색상 */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div {
        text-align: center !important;
        color: #31333F !important;
    }

    /* 날짜 컬럼 배경색 (2번째 칸) */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(2) {
        background-color: #f4f4f4 !important;
    }

    /* 선(파랑) / 후(빨강) 색상 */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(3):contains("선") { color: #0000ff !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(3):contains("후") { color: #ff0000 !important; font-weight: bold; }

    /* 승(파랑) / 패(빨강) 색상 */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(4):contains("승") { color: #0000ff !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(4):contains("패") { color: #ff0000 !important; font-weight: bold; }

    /* 세트 전적 상세 색상 (승리 조합: 파랑, 패배 조합: 빨강) */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("OO") { color: #0000ff !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("OXO") { color: #0000ff !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("XOO") { color: #0000ff !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("XX") { color: #ff0000 !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("XOX") { color: #ff0000 !important; font-weight: bold; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(5):contains("OXX") { color: #ff0000 !important; font-weight: bold; }

    /* 브릭(회색) / 실수(빨강) 체크박스 색상 */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(11) input[type="checkbox"] { accent-color: #999999 !important; }
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(12) input[type="checkbox"] { accent-color: #ff0000 !important; }

    /* 비고 컬럼 왼쪽 정렬 */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div:nth-child(13) { text-align: left !important; }

    /* [분석 페이지] 1/3 너비 및 테이블 디자인 */
    .analysis-wrapper { width: 33.3%; min-width: 400px; margin-left: 0; }
    .styled-table { 
        width: 100%; font-size: 14px; border-collapse: collapse; 
        margin-bottom: 30px; table-layout: fixed; border: 1px solid #dee2e6;
    }
    .styled-table th, .styled-table td { 
        text-align: center !important; border: 1px solid #dee2e6 !important; padding: 8px !important; 
    }
    .styled-table th { background-color: #f9cb9c !important; color: #31333F !important; font-weight: bold !important; }
    .win-val { color: #0000ff !important; font-weight: bold; }
    .loss-val { color: #ff0000 !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 로직 ---
def load_metadata():
    default_meta = {
        "my_decks": ["KT", "Ennea", "Maliss", "Tenpai"],
        "opp_decks": ["KT", "Ennea", "Maliss", "Tenpai", "Labrynth", "Branded"],
        "archetypes": ["운영", "전개", "미드레인지", "함떡", "기타"],
        "win_loss_reasons": ["상대 패", "자신 실력", "특정 카드", "핸드 말림", "상성"],
        "target_cards": ["증식의 G", "하루 우라라", "무한포영", "니비루", "드롤"]
    }
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: pass
    return default_meta

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

# 분석 테이블 생성 함수
def render_styled_table(title, target_df):
    calc_df = target_df[target_df['결과'].isin(['승', '패'])]
    total = len(calc_df)
    if total == 0: return f'<table class="styled-table"><tr><th>{title}</th></tr><tr><td>데이터 없음</td></tr></table>'
    
    wins = len(calc_df[calc_df['결과'] == '승'])
    losses = total - wins
    f_df = calc_df[calc_df['선후공'] == '선']
    s_df = calc_df[calc_df['선후공'] == '후']
    
    def get_rate(a, b): return (a/b*100) if b > 0 else 0

    return f"""
    <table class="styled-table">
        <tr><th colspan="5">{title}</th></tr>
        <tr><th>Overall</th><th>Games</th><th>Win Rate</th><th>W</th><th>L</th></tr>
        <tr><td>Result</td><td>{total}</td><td>{get_rate(wins, total):.2f}%</td><td class="win-val">{wins}</td><td class="loss-val">{losses}</td></tr>
        <tr><th>Coin</th><th>1st</th><th>2nd</th><th>1st Rate</th><th>2nd Rate</th></tr>
        <tr><td>Result</td><td class="win-val">{len(f_df)}</td><td class="loss-val">{len(s_df)}</td><td class="win-val">{get_rate(len(f_df), total):.1f}%</td><td class="loss-val">{get_rate(len(s_df), total):.1f}%</td></tr>
        <tr><th>1st</th><th>1st Win</th><th>1st Lose</th><th>1st W%</th><th>1st L%</th></tr>
        <tr><td>Result</td><td class="win-val">{len(f_df[f_df['결과']=='승'])}</td><td class="loss-val">{len(f_df[f_df['결과']=='패'])}</td><td class="win-val">{get_rate(len(f_df[f_df['결과']=='승']), len(f_df)):.1f}%</td><td class="loss-val">{100-get_rate(len(f_df[f_df['결과']=='승']), len(f_df)):.1f}%</td></tr>
        <tr><th>2nd</th><th>2nd Win</th><th>2nd Lose</th><th>2nd W%</th><th>2nd L%</th></tr>
        <tr><td>Result</td><td class="win-val">{len(s_df[s_df['결과']=='승'])}</td><td class="loss-val">{len(s_df[s_df['결과']=='패'])}</td><td class="win-val">{get_rate(len(s_df[s_df['결과']=='승']), len(s_df)):.1f}%</td><td class="loss-val">{100-get_rate(len(s_df[s_df['결과']=='승']), len(s_df)):.1f}%</td></tr>
    </table>
    """

# --- 4. 메인 로직 ---
if 'metadata' not in st.session_state: st.session_state.metadata = load_metadata()
if 'df' not in st.session_state: st.session_state.df = load_records()

menu = st.sidebar.radio("메뉴", ["📊 기록", "📈 분석", "⚙️ 설정"])

if menu == "📊 기록":
    st.title("📊 Match Records")
    if st.button("➕ 새로운 경기 추가"):
        new_row = pd.DataFrame([{"NO.": str(len(st.session_state.df)+1), "날짜": pd.Timestamp.now().strftime("%m.%d"), "선후공": "선", "결과": "승", "세트 전적": "OO", "내 덱": st.session_state.metadata["my_decks"][0], "상대 덱": st.session_state.metadata["opp_decks"][0], "아키타입": st.session_state.metadata["archetypes"][0], "승패 요인": st.session_state.metadata["win_loss_reasons"][0], "특정 카드": st.session_state.metadata["target_cards"][0], "브릭": False, "실수": False, "비고": ""}])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        save_records(st.session_state.df)
        st.rerun()

    edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic", hide_index=True, key="main_editor",
        column_config={
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"]),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"]),
            "세트 전적": st.column_config.SelectboxColumn("세트 전적", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"]),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata["my_decks"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata["opp_decks"]),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.metadata["archetypes"]),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.metadata["win_loss_reasons"]),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.metadata["target_cards"]),
        })
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
