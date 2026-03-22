import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. [디자인 설정] 분석 레이아웃 (1/3 너비) ---
st.markdown(f"""
    <style>
    [data-testid="stTableIdxColumn"] {{ display: none; }}
    th {{ display: none; }} 
    .analysis-wrapper {{ width: 33%; margin-left: 0; }}
    .styled-table {{ width: 100%; font-size: 14px; border-collapse: collapse; margin-bottom: 30px; table-layout: fixed; }}
    .styled-table td {{ text-align: center !important; border: 1px solid #dee2e6 !important; padding: 10px !important; }}
    .styled-table tr:nth-child(odd) {{ background-color: #f0f2f6 !important; font-weight: bold; color: #31333F; }}
    div[data-testid="stSelectbox"] {{ width: 100% !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 처리 함수 (에러 방어막) ---
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
            try: return json.load(f)
            except: pass
    return default_meta

def load_records():
    cols = ["NO.", "날짜", "선후공", "결과", "세트 전적", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        try:
            # 🔥 [해결책 1] 불러올 때 모든 값을 문자열로 일단 읽고 NaN 제거
            df = pd.read_csv(RECORD_FILE, dtype=str).fillna("")
            
            # 🔥 [해결책 2] 필수 컬럼 강제 생성 및 타입 교정
            # 체크박스용 컬럼 (bool)
            for col in ["브릭", "실수"]:
                if col not in df.columns: df[col] = False
                else: df[col] = df[col].apply(lambda x: True if str(x).lower() == 'true' else False)
            
            # 숫자용 컬럼 (int)
            df["NO."] = range(1, len(df) + 1)
            
            # 나머지 모든 컬럼 (str)
            for col in cols:
                if col not in ["브릭", "실수", "NO."]:
                    if col not in df.columns: df[col] = ""
                    df[col] = df[col].astype(str)
            
            return df[cols] # 컬럼 순서 고정
        except: pass
    return pd.DataFrame(columns=cols)

# --- 4. 분석 표 렌더링 함수 ---
def render_analysis_table(target_df):
    calc_df = target_df[target_df['결과'].isin(['승', '패'])]
    total = len(calc_df)
    if total == 0: return "<p style='color:gray;'>데이터가 없습니다.</p>"
    wins = len(calc_df[calc_df['결과'] == '승'])
    losses = len(calc_df[calc_df['결과'] == '패'])
    win_rate = (wins / total * 100)
    f_df, s_df = calc_df[calc_df['선후공'] == '선'], calc_df[calc_df['선후공'] == '후']
    f_win = len(f_df[f_df['결과'] == '승'])
    s_win = len(s_df[s_df['결과'] == '승'])
    return f"""
        <table class="styled-table">
            <tr><td>게임 수</td><td>전체 승률</td><td>승리</td><td>패배</td></tr>
            <tr><td>{total}</td><td>{win_rate:.1f}%</td><td>{wins}</td><td>{losses}</td></tr>
            <tr><td>선공 승률</td><td>후공 승률</td><td>선공 수</td><td>후공 수</td></tr>
            <tr><td>{(f_win/len(f_df)*100 if len(f_df)>0 else 0):.1f}%</td><td>{(s_win/len(s_df)*100 if len(s_df)>0 else 0):.1f}%</td><td>{len(f_df)}</td><td>{len(s_df)}</td></tr>
        </table>
    """

# --- 5. 메인 로직 ---
if 'df' not in st.session_state:
    st.session_state.df = load_records()
if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()

page = st.sidebar.radio("메뉴", ["📊 기록", "📈 분석", "⚙️ 설정"])

if page == "📊 기록":
    st.title("📊 전적 기록")
    
    # 🔥 [중요] 새로운 경기 추가
    if st.button("➕ 새로운 경기 추가"):
        new_data = {col: "" for col in st.session_state.df.columns}
        new_data.update({
            "날짜": pd.Timestamp.now().strftime("%m.%d"),
            "선후공": "선", "결과": "승", "세트 전적": "OO",
            "내 덱": st.session_state.metadata["my_decks"][0],
            "상대 덱": st.session_state.metadata["opp_decks"][0],
            "브릭": False, "실수": False
        })
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_data])], ignore_index=True)
        st.session_state.df["NO."] = range(1, len(st.session_state.df) + 1)
        st.session_state.df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.rerun()

    # 🔥 [해결책 3] 에디터 반환값을 변수에 저장하고 변경 시에만 파일 쓰기
    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "NO.": st.column_config.NumberColumn("NO.", disabled=True, format="%d"),
            "날짜": st.column_config.TextColumn("날짜"),
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"]),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"]),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata["my_decks"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata["opp_decks"]),
            "브릭": st.column_config.CheckboxColumn("브릭"),
            "실수": st.column_config.CheckboxColumn("실수")
        }
    )

    if not edited_df.equals(st.session_state.df):
        edited_df["NO."] = range(1, len(edited_df) + 1)
        edited_df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.session_state.df = edited_df

elif page == "📈 분석":
    st.title("📈 분석 결과")
    df = load_records()
    st.markdown('<div class="analysis-wrapper">', unsafe_allow_html=True)
    st.subheader("전체 통계")
    st.markdown(render_analysis_table(df), unsafe_allow_html=True)
    
    st.subheader("덱별 상세")
    sel_deck = st.selectbox("덱 선택", st.session_state.metadata["my_decks"], label_visibility="collapsed")
    st.markdown(render_analysis_table(df[df['내 덱'] == sel_deck]), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title("⚙️ 설정")
    # (설정 저장 로직 생략 없이 그대로 유지...)
    new_my = st.text_area("내 덱 리스트", ", ".join(st.session_state.metadata["my_decks"]))
    if st.button("설정 저장"):
        st.session_state.metadata["my_decks"] = [x.strip() for x in new_my.split(",")]
        with open(META_FILE, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.metadata, f, ensure_ascii=False)
        st.success("저장되었습니다.")
