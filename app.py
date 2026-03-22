import streamlit as st
import pandas as pd
import os
import json
import plotly.express as px

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. [디자인] CSS ---
st.markdown("""
    <style>
    [data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"] div { text-align: center !important; font-size: 13px !important; }
    
    /* Record 헤더 색상 */
    div[data-testid="stDataFrameResizable"] th:nth-child(1), div[data-testid="stDataFrameResizable"] th:nth-child(2),
    div[data-testid="stDataFrameResizable"] th:nth-child(3), div[data-testid="stDataFrameResizable"] th:nth-child(4),
    div[data-testid="stDataFrameResizable"] th:nth-child(5) { background-color: #a2d5c6 !important; color: #31333F !important; }
    div[data-testid="stDataFrameResizable"] th:nth-child(6), div[data-testid="stDataFrameResizable"] th:nth-child(7),
    div[data-testid="stDataFrameResizable"] th:nth-child(8), div[data-testid="stDataFrameResizable"] th:nth-child(9),
    div[data-testid="stDataFrameResizable"] th:nth-child(10), div[data-testid="stDataFrameResizable"] th:nth-child(11) { background-color: #f9cb9c !important; }
    div[data-testid="stDataFrameResizable"] th:nth-child(12), div[data-testid="stDataFrameResizable"] th:nth-child(13) { background-color: #ffe599 !important; }

    .styled-table { width: 100%; font-size: 12px; border-collapse: collapse; margin-bottom: 20px; table-layout: fixed; border: 1px solid #dee2e6; }
    .styled-table th, .styled-table td { text-align: center !important; border: 1px solid #dee2e6 !important; padding: 4px !important; }
    .styled-table th { background-color: #f9cb9c !important; color: #31333F !important; font-weight: bold !important; }
    .win-val { color: #0000ff !important; font-weight: bold; }
    .loss-val { color: #ff0000 !important; font-weight: bold; }
    
    textarea, input { spellcheck: false !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 로직 ---
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
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE, dtype=str).fillna("")
        for col in ["브릭", "실수"]:
            if col in df.columns: df[col] = df[col].apply(lambda x: str(x).lower() in ['true', '1'])
        return df
    return pd.DataFrame(columns=["NO.", "날짜", "선후공", "결과", "세트", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"])

def save_records(df):
    df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
    st.session_state.df = df.reset_index(drop=True)

def render_summary_table(title, target_df):
    calc = target_df[target_df['결과'].isin(['승', '패'])]
    if len(calc) == 0: return f'<table class="styled-table"><tr><th>{title}</th></tr><tr><td>데이터 없음</td></tr></table>'
    w, l = len(calc[calc['결과']=='승']), len(calc[calc['결과']=='패'])
    f_df, s_df = calc[calc['선후공']=='선'], calc[calc['선후공']=='후']
    f_t, s_t = len(f_df), len(s_df)
    f_w, s_w = len(f_df[f_df['결과']=='승']), len(s_df[s_df['결과']=='승'])
    return f"""
        <table class="styled-table">
            <tr><th colspan="5">{title}</th></tr>
            <tr><th>Overall</th><th>Games</th><th>Win Rate</th><th>W</th><th>L</th></tr>
            <tr><td>Result</td><td>{len(calc)}</td><td>{(w/len(calc)*100):.2f}%</td><td class="win-val">{w}</td><td class="loss-val">{l}</td></tr>
            <tr><th>Coin</th><th>1st</th><th>2nd</th><th>1st Rate</th><th>2nd Rate</th></tr>
            <tr><td>Result</td><td class="win-val">{f_t}</td><td class="loss-val">{s_t}</td><td class="win-val">{(f_t/len(calc)*100):.1f}%</td><td class="loss-val">{(s_t/len(calc)*100):.1f}%</td></tr>
            <tr><th>1st</th><th>1st Win</th><th>1st Lose</th><th>1st W%</th><th>1st L%</th></tr>
            <tr><td>Result</td><td class="win-val">{f_w}</td><td class="loss-val">{f_t-f_w}</td><td class="win-val">{(f_w/f_t*100 if f_t>0 else 0):.1f}%</td><td class="loss-val">{(100-(f_w/f_t*100) if f_t>0 else 0):.1f}%</td></tr>
            <tr><th>2nd</th><th>2nd Win</th><th>2nd Lose</th><th>2nd W%</th><th>2nd L%</th></tr>
            <tr><td>Result</td><td class="win-val">{s_w}</td><td class="loss-val">{s_t-s_w}</td><td class="win-val">{(s_w/s_t*100 if s_t>0 else 0):.1f}%</td><td class="loss-val">{(100-(s_w/s_t*100) if s_t>0 else 0):.1f}%</td></tr>
        </table>
    """

# --- 4. 앱 실행 ---
if 'metadata' not in st.session_state: st.session_state.metadata = load_metadata()
if 'df' not in st.session_state: st.session_state.df = load_records()

page = st.sidebar.radio("메뉴", ["📊 Record", "📈 Analysis", "🖼️ Graph", "⚙️ Setting"])

if page == "📊 Record":
    st.title("📊 Match Record")
    if st.button("➕ 새로운 경기 추가"):
        m = st.session_state.metadata
        new_row = pd.DataFrame([{"NO.": str(len(st.session_state.df)+1), "날짜": pd.Timestamp.now().strftime("%m.%d"), "선후공": "선", "결과": "승", "세트": "OO", "점수": "0", "내 덱": m["my_decks"][0], "상대 덱": m["opp_decks"][0], "아키타입": "", "승패 요인": m["win_loss_reasons"][0], "특정 카드": "", "브릭": False, "실수": False, "비고": ""}])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        save_records(st.session_state.df)
        st.rerun()

    edited = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic", hide_index=True, key="editor_v3",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width=40), "날짜": st.column_config.TextColumn("날짜", width=60),
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"], width=60),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"], width=60),
            "세트": st.column_config.SelectboxColumn("세트", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"], width=80),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata["my_decks"], width=100),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata["opp_decks"], width=100),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.metadata["archetypes"], width=100),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.metadata["win_loss_reasons"], width=100),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.metadata["target_cards"], width=100),
            "브릭": st.column_config.CheckboxColumn("브릭", width=50), "실수": st.column_config.CheckboxColumn("실수", width=50), "비고": st.column_config.TextColumn("비고", width=350)
        })
    if not edited.equals(st.session_state.df): save_records(edited); st.rerun()

elif page == "📈 Analysis":
    st.title("📈 Rating Analysis")
    df_ana = load_records()
    if not df_ana.empty:
        calc_df = df_ana[df_ana['결과'].isin(['승', '패'])].copy()
        # (중략: 기존 Analysis 계산 로직과 동일)
        col_left, col_right = st.columns([1, 2.2])
        with col_left:
            st.markdown(render_summary_table("Overall Data", calc_df), unsafe_allow_html=True)
            sel_my = st.selectbox("내 덱 선택", st.session_state.metadata["my_decks"])
            st.markdown(render_summary_table(f"Result: {sel_my}", calc_df[calc_df['내 덱']==sel_my]), unsafe_allow_html=True)
        with col_right:
            st.subheader("📊 Opponent Deck Statistics")
            # (중략: 기존 테이블 렌더링 로직)

elif page == "🖼️ Graph":
    st.title("🖼️ Deck Distribution Graph")
    df_graph = load_records()
    if not df_graph.empty:
        calc_df = df_graph[df_graph['결과'].isin(['승', '패'])]
        st.subheader("🃏 상대 덱 점유율 (Overall)")
        opp_counts = calc_df['상대 덱'].value_counts().reset_index()
        opp_counts.columns = ['Deck', 'Count']
        
        fig = px.pie(opp_counts, values='Count', names='Deck', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("그래프를 표시할 데이터가 없습니다.")

elif page == "⚙️ Setting":
    st.title("⚙️ Auto-Save Setting")
    st.caption("항목을 수정한 후 입력창 바깥을 클릭하면 자동으로 저장됩니다.")
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
