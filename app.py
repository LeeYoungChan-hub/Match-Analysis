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
    "table_container_width": "33%", 
    "font_size": "14px",             
    "label_bg": "#f0f2f6",           
    "cell_padding": "10px"           
}

st.markdown(f"""
    <style>
    [data-testid="stTableIdxColumn"] {{ display: none; }}
    th {{ display: none; }} 
    
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
            return pd.read_csv(RECORD_FILE)
        except: pass
    return pd.DataFrame(columns=["NO.", "날짜", "선후공", "결과", "세트 전적", "내 덱", "상대 덱", "비고"])

# --- 4. 분석 표 렌더링 함수 ---
def render_analysis_table(target_df):
    # 실제 승/패 데이터가 있는 것만 필터링하여 계산
    calc_df = target_df[target_df['결과'].isin(['승', '패'])]
    total = len(calc_df)
    if total == 0:
        st.info("분석할 승/패 데이터가 없습니다.")
        return

    wins = len(calc_df[calc_df['결과'] == '승'])
    losses = len(calc_df[calc_df['결과'] == '패'])
    win_rate = (wins / total * 100)
    
    f_df = calc_df[calc_df['선후공'] == '선']
    s_df = calc_df[calc_df['선후공'] == '후']
    f_count, s_count = len(f_df), len(s_df)
    
    f_win_rate = (len(f_df[f_df['결과'] == '승']) / f_count * 100) if f_count > 0 else 0
    s_win_rate = (len(s_df[s_df['결과'] == '승']) / s_count * 100) if s_count > 0 else 0

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

# --- 5. 세션 관리 및 메인 로직 ---
if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()
if 'df' not in st.session_state:
    st.session_state.df = load_records()

st.sidebar.title("🎮 Rating 메뉴")
page = st.sidebar.radio("이동할 페이지", ["📊 기록", "📈 분석", "⚙️ 설정"])

# [페이지 1: 기록] 드롭다운 설정 포함
if page == "📊 기록":
    st.title("📊 전적 기록")
    
    if st.button("➕ 새로운 경기 추가"):
        new_no = int(st.session_state.df["NO."].max() + 1) if not st.session_state.df.empty else 1
        new_row = pd.DataFrame([{
            "NO.": new_no, "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"), 
            "선후공": "선", "결과": "승", "세트 전적": "OO", 
            "내 덱": st.session_state.metadata["my_decks"][0], 
            "상대 덱": st.session_state.metadata["opp_decks"][0]
        }])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        st.rerun()

    # 🔥 중요: column_config를 사용하여 드롭다운(Selectbox) 복구
    edited_df = st.data_editor(
        st.session_state.df, 
        use_container_width=True, 
        num_rows="dynamic", 
        hide_index=True,
        column_config={
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"], required=True),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"], required=True),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata["my_decks"], required=True),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata["opp_decks"], required=True),
            "세트 전적": st.column_config.SelectboxColumn("세트 전적", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"])
        }
    )
    
    if st.button("💾 데이터 저장", type="primary"):
        st.session_state.df = edited_df
        st.session_state.df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.success("데이터가 저장되었습니다.")

# [페이지 2: 분석]
elif page == "📈 분석":
    st.title("📈 Rating Analysis")
    df_analysis = load_records()
    
    if df_analysis.empty:
        st.warning("분석할 전적 데이터가 없습니다.")
    else:
        st.subheader("1. Overall Data")
        render_analysis_table(df_analysis)
        st.divider()
        st.subheader("2. 내 덱별 상세 분석")
        selected = st.selectbox("분석할 덱 선택", st.session_state.metadata["my_decks"])
        render_analysis_table(df_analysis[df_analysis['내 덱'] == selected])

# [페이지 3: 설정]
else:
    st.title("⚙️ Rating 설정")
    meta = st.session_state.metadata
    
    col1, col2 = st.columns(2)
    with col1:
        new_my = st.text_area("내 덱 리스트 (쉼표 구분)", ", ".join(meta.get("my_decks", [])))
        new_opp = st.text_area("상대 덱 리스트 (쉼표 구분)", ", ".join(meta.get("opp_decks", [])))
    with col2:
        new_arche = st.text_area("아키타입", ", ".join(meta.get("archetypes", [])))
        new_reasons = st.text_area("승패 요인", ", ".join(meta.get("win_loss_reasons", [])))
    
    if st.button("✅ 설정 저장", type="primary"):
        updated_meta = {
            "my_decks": [x.strip() for x in new_my.split(",") if x.strip()],
            "opp_decks": [x.strip() for x in new_opp.split(",") if x.strip()],
            "archetypes": [x.strip() for x in new_arche.split(",") if x.strip()],
            "win_loss_reasons": [x.strip() for x in new_reasons.split(",") if x.strip()],
            "target_cards": meta.get("target_cards", []) # 기존 데이터 유지
        }
        st.session_state.metadata = updated_meta
        with open(META_FILE, 'w', encoding='utf-8') as f:
            json.dump(updated_meta, f, ensure_ascii=False, indent=4)
        st.success("설정이 저장되었습니다. 기록 페이지의 드롭다운이 업데이트됩니다.")
        st.rerun()
