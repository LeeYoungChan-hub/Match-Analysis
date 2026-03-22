import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. [디자인 설정] 표의 너비(1/3)와 상하 배치 스타일 ---
STYLE_CONFIG = {
    "table_container_width": "33%",  # 화면의 1/3 너비
    "font_size": "14px",             # 글자 크기
    "label_bg": "#f0f2f6",           # 라벨 행 배경색
    "cell_padding": "10px"           # 셀 높이 여백
}

st.markdown(f"""
    <style>
    [data-testid="stTableIdxColumn"] {{ display: none; }}
    th {{ display: none; }} 
    
    /* 표가 왼쪽 1/3만 차지하도록 제한하는 컨테이너 */
    .analysis-wrapper {{
        width: {STYLE_CONFIG["table_container_width"]};
        margin-left: 0;
    }}

    .styled-table {{
        width: 100%;
        font-size: {STYLE_CONFIG["font_size"]};
        border-collapse: collapse;
        margin-bottom: 20px;
        table-layout: fixed;
    }}
    
    .styled-table td {{
        text-align: center !important;
        border: 1px solid #dee2e6 !important;
        padding: {STYLE_CONFIG["cell_padding"]} !important;
    }}
    
    /* 라벨 행(홀수행) 디자인: 이미지 캡처와 동일하게 상단 배치 */
    .styled-table tr:nth-child(odd) {{
        background-color: {STYLE_CONFIG["label_bg"]} !important;
        font-weight: bold;
        color: #31333F;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 로직 함수 ---
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
            # 분석을 위해 승/패 결과가 있는 데이터만 필터링
            return df[df['결과'].isin(['승', '패'])]
        except: pass
    return pd.DataFrame()

# --- 4. 분석 표 렌더링 함수 (라벨-값 상하 교차 구조) ---
def render_analysis_table(target_df):
    total = len(target_df)
    if total == 0:
        st.info("데이터가 없습니다.")
        return

    # 주요 지표 계산
    wins = len(target_df[target_df['결과'] == '승'])
    losses = len(target_df[target_df['결과'] == '패'])
    win_rate = (wins / total * 100)
    
    f_df = target_df[target_df['선후공'] == '선']
    s_df = target_df[target_df['선후공'] == '후']
    f_count, s_count = len(f_df), len(s_df)
    
    f_win_rate = (len(f_df[f_df['결과'] == '승']) / f_count * 100) if f_count > 0 else 0
    s_win_rate = (len(s_df[s_df['결과'] == '승']) / s_count * 100) if s_count > 0 else 0

    # 8행 구조 (라벨1줄 - 값1줄 반복)
    html_code = f"""
    <div class="analysis-wrapper">
        <table class="styled-table">
            <tr><td>게임 수</td><td>전체 승률</td><td>전체 승리수</td><td>전체 패배 수</td></tr>
            <tr><td>{total}</td><td>{win_rate:.2f}%</td><td>{wins}</td><td>{losses}</td></tr>
            <tr><td>선공 수</td><td>후공 수</td><td>선공 확률</td><td>후공 확률</td></tr>
            <tr><td>{f_count}</td><td>{s_count}</td><td>{(f_count/total*100):.2f}%</td><td>{(s_count/total*100):.2f}%</td></tr>
            <tr><td>선공 승리</td><td>선공 패배</td><td>선공 승률</td><td>선공 패배율</td></tr>
            <tr><td>{len(f_df[f_df['결과'] == '승'])}</td><td>{len(f_df[f_df['결과'] == '패'])}</td><td>{f_win_rate:.2f}%</td><td>{(100-f_win_rate):.2f}%</td></tr>
            <tr><td>후공 승리</td><td>후공 패배</td><td>후공 승률</td><td>후공 패배율</td></tr>
            <tr><td>{len(s_df[s_df['결과'] == '승'])}</td><td>{len(s_df[s_df['결과'] == '패'])}</td><td>{s_win_rate:.2f}%</td><td>{(100-s_win_rate):.2f}%</td></tr>
        </table>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# --- 5. 페이지 구성 ---
if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()

st.sidebar.title("🎮 Rating 메뉴")
page = st.sidebar.radio("이동할 페이지", ["📊 기록", "📈 분석", "⚙️ 설정"])

if page == "📊 기록":
    st.title("📊 전적 기록")
    if 'df' not in st.session_state:
        st.session_state.df = load_records()
    
    # 데이터 에디터 출력
    edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic", hide_index=True)
    
    if st.button("💾 데이터 저장", type="primary"):
        edited_df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.success("저장되었습니다.")

elif page == "📈 분석":
    st.title("📈 Rating Analysis")
    df = load_records()
    
    if df.empty:
        st.warning("분석할 전적 데이터가 없습니다. 먼저 기록을 추가해주세요.")
    else:
        st.subheader("1. Overall Data")
        render_analysis_table(df)
        
        st.divider()
        
        st.subheader("2. 내 덱별 상세 분석")
        selected = st.selectbox("분석할 덱 선택", st.session_state.metadata["my_decks"])
        deck_filtered_df = df[df['내 덱'] == selected]
        render_analysis_table(deck_filtered_df)

else:  # ⚙️ 설정 페이지
    st.title("⚙️ Rating 설정")
    meta = st.session_state.metadata
    new_my = st.text_area("내 덱 리스트 (쉼표 구분)", ", ".join(meta.get("my_decks", [])))
    
    if st.button("✅ 설정 저장", type="primary"):
        st.session_state.metadata["my_decks"] = [x.strip() for x in new_my.split(",") if x.strip()]
        with open(META_FILE, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.metadata, f, ensure_ascii=False, indent=4)
        st.success("설정이 저장되었습니다.")
        st.rerun()
