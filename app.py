import streamlit as st
import pandas as pd
import os
import json
import numpy as np

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. [디자인 설정] 표 및 드롭다운 너비 조절 (1/3 너비) ---
STYLE_CONFIG = {
    "container_width": "33%",        # 왼쪽 1/3만 차지
    "font_size": "14px",             
    "label_bg": "#f0f2f6",           
    "cell_padding": "10px"           
}

st.markdown(f"""
    <style>
    [data-testid="stTableIdxColumn"] {{ display: none; }}
    th {{ display: none; }} 
    /* 분석 페이지 컨테이너 너비 제한 */
    .analysis-wrapper {{ width: {STYLE_CONFIG["container_width"]}; margin-left: 0; }}
    .styled-table {{ width: 100%; font-size: {STYLE_CONFIG["font_size"]}; border-collapse: collapse; margin-bottom: 30px; table-layout: fixed; }}
    .styled-table td {{ text-align: center !important; border: 1px solid #dee2e6 !important; padding: {STYLE_CONFIG["cell_padding"]} !important; }}
    .styled-table tr:nth-child(odd) {{ background-color: {STYLE_CONFIG["label_bg"]} !important; font-weight: bold; color: #31333F; }}
    
    /* 드롭다운 너비를 분석 wrapper와 일치시킴 */
    div[data-testid="stSelectbox"] {{ width: 100% !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 처리 함수 (타입 충돌 완벽 방어) ---
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
                saved_meta = json.load(f)
                for key, value in default_meta.items():
                    if key not in saved_meta: saved_meta[key] = value
                return saved_meta
            except: pass
    return default_meta

def load_records():
    cols = ["NO.", "날짜", "선후공", "결과", "세트 전적", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        try:
            # 불러올 때 NaN을 빈 문자열로 즉시 치환
            df = pd.read_csv(RECORD_FILE).fillna("")
            
            # 모든 필수 컬럼 존재 확인 및 타입 강제 변환
            for col in cols:
                if col not in df.columns:
                    df[col] = False if col in ["브릭", "실수"] else ""
            
            # 텍스트 컬럼 강제 문자열화 (None/NaN 원천 봉쇄)
            str_cols = ["날짜", "선후공", "결과", "세트 전적", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "비고"]
            for col in str_cols:
                df[col] = df[col].astype(str)
            
            # 체크박스 컬럼 불리언화
            for col in ["브릭", "실수"]:
                df[col] = df[col].apply(lambda x: True if str(x).lower() in ['true', '1.0', '1'] else False)
            
            # NO. 정수화
            df["NO."] = range(1, len(df) + 1)
            return df
        except: pass
    return pd.DataFrame(columns=cols)

def save_data_auto(current_df):
    # 저장 전 넘버링 재정렬
    current_df["NO."] = range(1, len(current_df) + 1)
    # 데이터 깨끗하게 정리 후 저장
    current_df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
    st.session_state.df = current_df

# --- 4. 분석 표 렌더링 함수 ---
def render_analysis_table(target_df):
    calc_df = target_df[target_df['결과'].isin(['승', '패'])]
    total = len(calc_df)
    if total == 0: return "<p style='color:gray;'>분석할 데이터가 없습니다.</p>"
    wins = len(calc_df[calc_df['결과'] == '승'])
    losses = len(calc_df[calc_df['결과'] == '패'])
    win_rate = (wins / total * 100)
    f_df, s_df = calc_df[calc_df['선후공'] == '선'], calc_df[calc_df['선후공'] == '후']
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
            "NO.": 0, "날짜": pd.Timestamp.now().strftime("%m.%d"), 
            "선후공": "선", "결과": "승", "세트 전적": "OO", 
            "내 덱": st.session_state.metadata["my_decks"][0], 
            "상대 덱": st.session_state.metadata["opp_decks"][0],
            "아키타입": st.session_state.metadata["archetypes"][0],
            "승패 요인": st.session_state.metadata["win_loss_reasons"][0],
            "특정 카드": st.session_state.metadata["target_cards"][0],
            "브릭": False, "실수": False, "비고": ""
        }])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        save_data_auto(st.session_state.df)
        st.rerun()

    # 에디터 호출
    edited_df = st.data_editor(
        st.session_state.df, 
        use_container_width=True, 
        num_rows="dynamic", 
        hide_index=True,
        key="rating_editor",
        column_config={
            "NO.": st.column_config.NumberColumn("NO.", disabled=True, format="%d"),
            "날짜": st.column_config.TextColumn("날짜"),
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"], required=True),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"], required=True),
            "세트 전적": st.column_config.SelectboxColumn("세트 전적", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"]),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata["my_decks"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata["opp_decks"]),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.metadata["archetypes"]),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.metadata["win_loss_reasons"]),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.metadata["target_cards"]),
            "브릭": st.column_config.CheckboxColumn("브릭"),
            "실수": st.column_config.CheckboxColumn("실수"),
            "비고": st.column_config.TextColumn("비고")
        }
    )

    if not edited_df.equals(st.session_state.df):
        save_data_auto(edited_df)
        st.rerun()

elif page == "📈 분석":
    st.title("📈 Rating Analysis")
    df_analysis = load_records()
    if not df_analysis.empty:
        # 왼쪽 1/3 너비 컨테이너 시작
        st.markdown('<div class="analysis-wrapper">', unsafe_allow_html=True)
        
        st.subheader("1. Overall Data")
        st.markdown(render_analysis_table(df_analysis), unsafe_allow_html=True)
        
        st.subheader("2. 내 덱별 상세 분석")
        # 드롭다운
        selected = st.selectbox("분석할 덱 선택", st.session_state.metadata["my_decks"], label_visibility="collapsed")
        # 필터링된 표
        st.markdown(render_analysis_table(df_analysis[df_analysis['내 덱'] == selected]), unsafe_allow_html=True)
        
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
