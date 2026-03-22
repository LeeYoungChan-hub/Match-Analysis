import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. [디자인] 인덱스 열 강제 숨김 CSS ---
st.markdown("""
    <style>
    /* 데이터 에디터 내부의 인덱스 열(맨 왼쪽)을 강제로 숨깁니다 */
    [data-testid="stTableIdxColumn"] { display: none !important; }
    th.col_heading.level0.index_name { display: none !important; }
    
    .analysis-wrapper { width: 33%; margin-left: 0; }
    .styled-table { width: 100%; font-size: 14px; border-collapse: collapse; margin-bottom: 30px; table-layout: fixed; }
    .styled-table td { text-align: center !important; border: 1px solid #dee2e6 !important; padding: 10px !important; }
    .styled-table tr:nth-child(odd) { background-color: #f0f2f6 !important; font-weight: bold; color: #31333F; }
    div[data-testid="stSelectbox"] { width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 처리 로직 ---
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
            df = pd.read_csv(RECORD_FILE, dtype=str).fillna("")
            # NO. 컬럼을 1부터 시작하는 정수로 강제 고정
            df["NO."] = range(1, len(df) + 1)
            # 체크박스 타입 보정
            for col in ["브릭", "실수"]:
                df[col] = df[col].apply(lambda x: True if str(x).lower() in ['true', '1'] else False)
            return df[cols]
        except: pass
    return pd.DataFrame(columns=cols)

def save_data(df):
    # 저장 전 NO. 재정렬
    df["NO."] = range(1, len(df) + 1)
    df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
    st.session_state.df = df

# --- 4. 메인 로직 ---
if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()
if 'df' not in st.session_state:
    st.session_state.df = load_records()

page = st.sidebar.radio("메뉴", ["📊 기록", "📈 분석", "⚙️ 설정"])

if page == "📊 기록":
    st.title("📊 전적 기록")
    
    if st.button("➕ 새로운 경기 추가"):
        # 새 행을 만들 때 NO.를 미리 계산해서 타입 충돌 방지
        next_no = len(st.session_state.df) + 1
        new_row = pd.DataFrame([{
            "NO.": next_no,
            "날짜": pd.Timestamp.now().strftime("%m.%d"),
            "선후공": "선", "결과": "승", "세트 전적": "OO",
            "내 덱": st.session_state.metadata["my_decks"][0],
            "상대 덱": st.session_state.metadata["opp_decks"][0],
            "아키타입": st.session_state.metadata["archetypes"][0],
            "승패 요인": st.session_state.metadata["win_loss_reasons"][0],
            "특정 카드": st.session_state.metadata["target_cards"][0],
            "브릭": False, "실수": False, "비고": ""
        }])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        save_data(st.session_state.df)
        st.rerun()

    # 🔥 hide_index=True를 통해 맨 왼쪽 인덱스 열(0,1,2...) 제거
    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,  # 여기서 인덱스 숨김
        key="rating_editor_v2",
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
        save_data(edited_df)
        st.rerun()

elif page == "📈 분석":
    st.title("📈 Rating Analysis")
    df = load_records()
    if not df.empty:
        st.markdown('<div class="analysis-wrapper">', unsafe_allow_html=True)
        st.subheader("1. Overall Stats")
        # 분석 테이블 로직 (동일)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "📈 분석":
    st.title("📈 Rating Analysis")
    df_analysis = load_records() # 최신 데이터 로드
    if not df_analysis.empty:
        st.markdown('<div class="analysis-wrapper">', unsafe_allow_html=True)
        st.subheader("1. Overall Statistics")
        # (이전과 동일한 분석 테이블 렌더링 로직 사용...)
        wins = len(df_analysis[df_analysis['결과'] == '승'])
        total = len(df_analysis[df_analysis['결과'].isin(['승', '패'])])
        wr = (wins/total*100) if total > 0 else 0
        st.write(f"총 경기 수: {total} | 승률: {wr:.1f}%")
        
        st.subheader("2. 덱별 상세 분석")
        selected = st.selectbox("덱 선택", st.session_state.metadata["my_decks"], label_visibility="collapsed")
        # 필터링 로직...
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "📈 분석":
    st.title("📈 Rating Analysis")
    # 분석 전 최신 데이터 로드 및 정제
    df_analysis = load_records()
    if not df_analysis.empty:
        st.markdown('<div class="analysis-wrapper">', unsafe_allow_html=True)
        st.subheader("1. 전체 데이터 통계")
        st.markdown(render_analysis_table(df_analysis), unsafe_allow_html=True)
        
        st.subheader("2. 내 덱별 상세 분석")
        selected = st.selectbox("분석할 덱 선택", st.session_state.metadata["my_decks"], label_visibility="collapsed")
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
