import streamlit as st
import pandas as pd
import os
import json
import plotly.express as px

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. [디자인] CSS (표 상단 2단 느낌 연출) ---
st.markdown("""
    <style>
    /* 1. 기본 회색 헤더 숨기기 */
    thead { display: none !important; }
    
    /* 2. 첫 번째 행(요약/라벨행) 디자인: 초록색 배경 + 높이 확보 */
    [data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"]:nth-child(1) {
        background-color: #d9ead3 !important; 
        font-weight: bold !important;
        color: #000 !important;
        height: 50px !important; /* 두 줄 표현을 위해 높이 증가 */
    }

    /* 3. 텍스트 중앙 정렬 및 줄바꿈 허용 */
    [data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"] div { 
        text-align: center !important; 
        white-space: pre-line !important; /* \n 기호로 줄바꿈 가능하게 설정 */
        line-height: 1.2 !important;
    }
    
    /* 맞춤법 빨간줄 제거 */
    textarea, input { spellcheck: false !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 관리 함수 ---
def load_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "my_decks": ["KT", "Ennea"], "opp_decks": ["Mitsu", "Branded", "Tenpai"],
        "archetypes": ["운영", "전개"], "win_loss_reasons": ["실력", "패사고"], "target_cards": ["Nibiru"]
    }

def save_metadata(meta):
    with open(META_FILE, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=4)

def load_records():
    cols = ["NO.", "날짜", "선후공", "결과", "세트", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE, dtype=str).fillna("")
        return df
    return pd.DataFrame(columns=cols)

def save_records(df):
    df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
    st.session_state.df = df.reset_index(drop=True)

# --- 4. 앱 메인 ---
if 'metadata' not in st.session_state: st.session_state.metadata = load_metadata()
if 'df' not in st.session_state: st.session_state.df = load_records()

page = st.sidebar.radio("메뉴", ["📊 Record", "📈 Analysis", "🖼️ Graph", "⚙️ Setting"])

# --- PAGE: Record ---
if page == "📊 Record":
    st.title("📊 Match Record")
    
    # 순수 경기 데이터 (요약행 제외)
    raw_df = st.session_state.df.copy()
    real_data = raw_df[raw_df['NO.'] != "경기"].copy()
    
    # 1. 실시간 데이터 계산
    total_games = len(real_data[real_data['결과'].isin(['승', '패'])])
    f_rate = f"{(len(real_data[real_data['선후공'] == '선']) / total_games * 100):.1f}%" if total_games > 0 else "0.0%"
    w_rate = f"{(len(real_data[real_data['결과'] == '승']) / total_games * 100):.1f}%" if total_games > 0 else "0.0%"
    b_sum = str(real_data['브릭'].apply(lambda x: 1 if str(x).lower() in ['true', '1', '▣'] else 0).sum())
    m_sum = str(real_data['실수'].apply(lambda x: 1 if str(x).lower() in ['true', '1', '▣'] else 0).sum())

    # 2. [핵심] 2단 구성 요약행 데이터 생성 (\n 사용)
    # 이미지처럼 '라벨'이 위, '값'이 아래로 가도록 구성
    summary_header = {
        "NO.": "경기",
        "날짜": "Date",
        "선후공": f"선공률\n{f_rate}", 
        "결과": f"승률\n{w_rate}", 
        "세트": "Result", 
        "점수": "Score", 
        "내 덱": "Use.deck", 
        "상대 덱": "Opp. deck", 
        "아키타입": "Plus Arch.", 
        "승패 요인": "W/L Factor", 
        "특정 카드": "Certain Card", 
        "브릭": f"Brick\n{b_sum}", 
        "실수": f"Mistake\n{m_sum}", 
        "비고": "Detailed"
    }

    # 표시용 경기 데이터 기호 변환
    temp_display = real_data.copy()
    for col in ["브릭", "실수"]:
        temp_display[col] = temp_display[col].apply(lambda x: "▣" if str(x).lower() in ['true', '1', '▣'] else "□")

    # 요약행 + 실제 데이터 합치기
    display_df = pd.concat([pd.DataFrame([summary_header]), temp_display], ignore_index=True)

    # 3. 데이터 에디터 출력 (상단 바 없이 표만)
    edited = st.data_editor(
        display_df, 
        use_container_width=True, 
        num_rows="dynamic", 
        hide_index=True, 
        key="record_editor_2_layer",
        height=900,
        column_config={
            "NO.": st.column_config.TextColumn("", width=50),
            "날짜": st.column_config.TextColumn("", width=80),
            "선후공": st.column_config.SelectboxColumn("", options=["", "선", "후"], width=80),
            "결과": st.column_config.SelectboxColumn("", options=["", "승", "패"], width=80),
            "세트": st.column_config.SelectboxColumn("", options=["", "OO", "OXO", "XOO", "XX", "XOX", "OXX"], width=90),
            "점수": st.column_config.TextColumn("", width=60),
            "내 덱": st.column_config.SelectboxColumn("", options=[""] + st.session_state.metadata["my_decks"], width=110),
            "상대 덱": st.column_config.SelectboxColumn("", options=[""] + st.session_state.metadata["opp_decks"], width=120),
            "아키타입": st.column_config.SelectboxColumn("", options=[""] + st.session_state.metadata["archetypes"], width=110),
            "승패 요인": st.column_config.SelectboxColumn("", options=[""] + st.session_state.metadata["win_loss_reasons"], width=110),
            "특정 카드": st.column_config.SelectboxColumn("", options=[""] + st.session_state.metadata["target_cards"], width=110),
            "브릭": st.column_config.TextColumn("", width=60), 
            "실수": st.column_config.TextColumn("", width=60),
            "비고": st.column_config.TextColumn("", width=450)
        }
    )

    # 4. 저장 로직 (1행 요약행 제외)
    if not edited.equals(display_df):
        save_df = edited[edited['NO.'] != "경기"].reset_index(drop=True)
        for col in ["브릭", "실수"]:
            save_df[col] = save_df[col].apply(lambda x: str(x) == '▣')
        save_records(save_df)
        st.rerun()

    # 추가 버튼
    if st.button("➕ 새로운 경기 추가"):
        new_row = pd.DataFrame([{
            "NO.": str(len(real_data) + 1), "날짜": "", "선후공": "", "결과": "", "세트": "", "점수": "", 
            "내 덱": "", "상대 덱": "", "아키타입": "", "승패 요인": "", "특정 카드": "", 
            "브릭": False, "실수": False, "비고": ""
        }])
        st.session_state.df = pd.concat([real_data, new_row], ignore_index=True)
        save_records(st.session_state.df)
        st.rerun()

# --- PAGE: Analysis ---
elif page == "📈 Analysis":
    st.title("📈 Rating Analysis")
    df_ana = load_records()
    if not df_ana.empty:
        calc_df = df_ana[df_ana['결과'].isin(['승', '패'])].copy()
        # ... (이하 분석 페이지 코드는 기존과 동일) ...
        st.markdown(render_summary_table("Overall Data", calc_df), unsafe_allow_html=True)
        # (중략)

# --- PAGE: Graph ---
elif page == "🖼️ Graph":
    st.title("🖼️ Deck Distribution Graph")
    df_graph = load_records()
    if not df_graph.empty:
        calc_df = df_graph[df_graph['결과'].isin(['승', '패'])]
        if not calc_df.empty:
            st.subheader("🃏 상대 덱 점유율 (Overall)")
            opp_counts = calc_df['상대 덱'].value_counts().reset_index()
            opp_counts.columns = ['Deck', 'Count']
            fig = px.pie(opp_counts, values='Count', names='Deck', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("분석할 승/패 데이터가 부족합니다.")
    else: st.info("기록된 데이터가 없습니다.")

# --- PAGE: Setting ---
else:
    st.title("⚙️ Setting (Auto-Save)")
    st.info("각 항목을 한 줄에 하나씩 입력하세요. 수정 후 바깥을 클릭하면 자동 저장됩니다.")
    m = st.session_state.metadata
    
    def update_meta():
        st.session_state.metadata = {
            "my_decks": [x.strip() for x in st.session_state.s_my.split("\n") if x.strip()],
            "opp_decks": [x.strip() for x in st.session_state.s_opp.split("\n") if x.strip()],
            "win_loss_reasons": [x.strip() for x in st.session_state.s_reas.split("\n") if x.strip()],
            "archetypes": [x.strip() for x in st.session_state.s_arch.split("\n") if x.strip()],
            "target_cards": [x.strip() for x in st.session_state.s_card.split("\n") if x.strip()]
        }
        save_metadata(st.session_state.metadata)

    c1, c2 = st.columns(2)
    with c1: st.text_area("내 덱", "\n".join(m["my_decks"]), key="s_my", on_change=update_meta, height=150)
    with c2: st.text_area("상대 덱", "\n".join(m["opp_decks"]), key="s_opp", on_change=update_meta, height=150)
    c3, c4 = st.columns(2)
    with c3: st.text_area("승패 요인", "\n".join(m["win_loss_reasons"]), key="s_reas", on_change=update_meta, height=150)
    with c4: st.text_area("아키타입", "\n".join(m["archetypes"]), key="s_arch", on_change=update_meta, height=150)
    st.text_area("특정 카드", "\n".join(m["target_cards"]), key="s_card", on_change=update_meta, height=150)
