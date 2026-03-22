import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. [디자인 설정] ---
STYLE_CONFIG = {
    "container_width": "50%",        
    "font_size": "14px",             
    "label_bg": "#f0f2f6",           
    "cell_padding": "10px"           
}

st.markdown(f"""
    <style>
    [data-testid="stTableIdxColumn"] {{ display: none; }}
    th {{ display: none; }} 
    .analysis-wrapper {{ width: {STYLE_CONFIG["container_width"]}; margin-left: 0; }}
    .styled-table {{ width: 100%; font-size: {STYLE_CONFIG["font_size"]}; border-collapse: collapse; margin-bottom: 30px; table-layout: fixed; }}
    .styled-table td {{ text-align: center !important; border: 1px solid #dee2e6 !important; padding: {STYLE_CONFIG["cell_padding"]} !important; }}
    .styled-table tr:nth-child(odd) {{ background-color: {STYLE_CONFIG["label_bg"]} !important; font-weight: bold; color: #31333F; }}
    div[data-testid="stSelectbox"] {{ width: 100% !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 처리 함수 ---
def load_metadata():
    # 기본값 설정
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
                saved_meta = json.load(f)
                # 🔥 중요: 저장된 파일에 누락된 키가 있으면 기본값으로 채워줌 (KeyError 방지)
                for key, value in default_meta.items():
                    if key not in saved_meta:
                        saved_meta[key] = value
                return saved_meta
            except: pass
    return default_meta

def load_records():
    cols = ["NO.", "날짜", "선후공", "결과", "세트 전적", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        try:
            df = pd.read_csv(RECORD_FILE)
            for col in cols:
                if col not in df.columns:
                    df[col] = False if col in ["브릭", "실수"] else ""
            return df
        except: pass
    return pd.DataFrame(columns=cols)

# 자동 저장 함수
def save_data_auto():
    if "rating_editor" in st.session_state:
        df = st.session_state["rating_editor"]["dataframe"]
        df["NO."] = range(1, len(df) + 1)
        df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.session_state.df = df

# --- 4. 분석 표 렌더링 함수 ---
def render_analysis_table(target_df):
    calc_df = target_df[target_df['결과'].isin(['승', '패'])]
    total = len(calc_df)
    if total == 0: return "<p style='color:gray;'>분석할 데이터가 없습니다.</p>"
    wins = len(calc_df[calc_df['결일'] == '승'])
    losses = len(calc_df[calc_df['결과'] == '패'])
    win_rate = (wins / total * 100)
    f_df = calc_df[calc_df['선후공'] == '선']
    s_df = calc_df[calc_df['선후공'] == '후']
    f_count, s_count = len(f_df), len(s_df)
    f_win_rate = (len(f_df[f_df['결과'] == '승']) / f_count * 100) if f_count > 0 else 0
    s_win_rate = (len(s_df[s_df['결과'] == '승']) / s_count * 100) if s_count > 0 else 0
    return f"""
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
    """

# --- 5. 세션 관리 및 메인 로직 ---
if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()
if 'df' not in st.session_state:
    st.session_state.df = load_records()

page = st.sidebar.radio("메뉴", ["📊 기록", "📈 분석", "⚙️ 설정"])

if page == "📊 기록":
    st.title("📊 전적 기록 (자동 저장)")
    
    if st.button("➕ 새로운 경기 추가"):
        new_row = pd.DataFrame([{
            "NO.": 0, "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"), 
            "선후공": "선", "결과": "승", "세트 전적": "OO", 
            "내 덱": st.session_state.metadata["my_decks"][0], 
            "상대 덱": st.session_state.metadata["opp_decks"][0],
            "아키타입": st.session_state.metadata["archetypes"][0],
            "승패 요인": st.session_state.metadata["win_loss_reasons"][0],
            "특정 카드": st.session_state.metadata["target_cards"][0],
            "브릭": False, "실수": False, "비고": ""
        }])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        st.session_state.df["NO."] = range(1, len(st.session_state.df) + 1)
        st.session_state.df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.rerun()

    st.data_editor(
        st.session_state.df, 
        use_container_width=True, 
        num_rows="dynamic", 
        hide_index=True,
        key="rating_editor",
        on_change=save_data_auto,
        column_config={
            "NO.": st.column_config.NumberColumn("NO.", disabled=True),
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"], required=True),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"], required=True),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata["my_decks"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_
