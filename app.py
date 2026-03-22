import streamlit as st
import pandas as pd
import os
import json
import plotly.express as px

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. [디자인] CSS (엑셀 스타일 및 맞춤법 방지) ---
st.markdown("""
    <style>
    [data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"] div { text-align: center !important; font-size: 13px !important; }
    
    /* Record 헤더 색상 커스텀 */
    div[data-testid="stDataFrameResizable"] th:nth-child(1), div[data-testid="stDataFrameResizable"] th:nth-child(2),
    div[data-testid="stDataFrameResizable"] th:nth-child(3), div[data-testid="stDataFrameResizable"] th:nth-child(4),
    div[data-testid="stDataFrameResizable"] th:nth-child(5) { background-color: #a2d5c6 !important; color: #31333F !important; }
    div[data-testid="stDataFrameResizable"] th:nth-child(6), div[data-testid="stDataFrameResizable"] th:nth-child(7),
    div[data-testid="stDataFrameResizable"] th:nth-child(8), div[data-testid="stDataFrameResizable"] th:nth-child(9),
    div[data-testid="stDataFrameResizable"] th:nth-child(10), div[data-testid="stDataFrameResizable"] th:nth-child(11) { background-color: #f9cb9c !important; }
    div[data-testid="stDataFrameResizable"] th:nth-child(12), div[data-testid="stDataFrameResizable"] th:nth-child(13) { background-color: #ffe599 !important; }

    /* 분석 페이지 테이블 스타일 */
    .styled-table { width: 100%; font-size: 12px; border-collapse: collapse; margin-bottom: 20px; table-layout: fixed; border: 1px solid #dee2e6; }
    .styled-table th, .styled-table td { text-align: center !important; border: 1px solid #dee2e6 !important; padding: 4px !important; }
    .styled-table th { background-color: #f9cb9c !important; color: #31333F !important; font-weight: bold !important; }
    .win-val { color: #0000ff !important; font-weight: bold; }
    .loss-val { color: #ff0000 !important; font-weight: bold; }
    
    /* 맞춤법 빨간줄 제거 */
    textarea, input { spellcheck: false !important; }
    .analysis-left-wrapper { max-width: 450px; }
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
        for col in ["브릭", "실수"]:
            if col in df.columns: df[col] = df[col].apply(lambda x: str(x).lower() in ['true', '1'])
        return df
    return pd.DataFrame(columns=cols)

def save_records(df):
    df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
    st.session_state.df = df.reset_index(drop=True)

def render_summary_table(title, target_df):
    calc = target_df[target_df['결과'].isin(['승', '패'])]
    total = len(calc)
    if total == 0: return f'<table class="styled-table"><tr><th>{title}</th></tr><tr><td>데이터 없음</td></tr></table>'
    
    w, l = len(calc[calc['결과']=='승']), len(calc[calc['결과']=='패'])
    f_df, s_df = calc[calc['선후공']=='선'], calc[calc['선후공']=='후']
    f_t, s_t = len(f_df), len(s_df)
    f_w, s_w = len(f_df[f_df['결과']=='승']), len(s_df[s_df['결과']=='승'])

    return f"""
        <table class="styled-table">
            <tr><th colspan="5">{title}</th></tr>
            <tr><th>Overall</th><th>Games</th><th>Win Rate</th><th>W</th><th>L</th></tr>
            <tr><td>Result</td><td>{total}</td><td>{(w/total*100):.2f}%</td><td class="win-val">{w}</td><td class="loss-val">{l}</td></tr>
            <tr><th>Coin</th><th>1st</th><th>2nd</th><th>1st Rate</th><th>2nd Rate</th></tr>
            <tr><td>Result</td><td class="win-val">{f_t}</td><td class="loss-val">{s_t}</td><td class="win-val">{(f_t/total*100):.1f}%</td><td class="loss-val">{(s_t/total*100):.1f}%</td></tr>
            <tr><th>1st</th><th>1st Win</th><th>1st Lose</th><th>1st W%</th><th>1st L%</th></tr>
            <tr><td>Result</td><td class="win-val">{f_w}</td><td class="loss-val">{f_t-f_w}</td><td class="win-val">{(f_w/f_t*100 if f_t>0 else 0):.1f}%</td><td class="loss-val">{(100-(f_w/f_t*100) if f_t>0 else 0):.1f}%</td></tr>
            <tr><th>2nd</th><th>2nd Win</th><th>2nd Lose</th><th>2nd W%</th><th>2nd L%</th></tr>
            <tr><td>Result</td><td class="win-val">{s_w}</td><td class="loss-val">{s_t-s_w}</td><td class="win-val">{(s_w/s_t*100 if s_t>0 else 0):.1f}%</td><td class="loss-val">{(100-(s_w/s_t*100) if s_t>0 else 0):.1f}%</td></tr>
        </table>
    """

# --- 4. 앱 메인 ---
if 'metadata' not in st.session_state: st.session_state.metadata = load_metadata()
if 'df' not in st.session_state: st.session_state.df = load_records()

page = st.sidebar.radio("메뉴", ["📊 Record", "📈 Analysis", "🖼️ Graph", "⚙️ Setting"])

# --- PAGE: Record ---
if page == "📊 Record":
    st.title("📊 Match Record")
    if st.button("➕ 새로운 경기 추가"):
        m = st.session_state.metadata
        new_row = pd.DataFrame([{"NO.": str(len(st.session_state.df)+1), "날짜": pd.Timestamp.now().strftime("%m.%d"), "선후공": "선", "결과": "승", "세트": "OO", "점수": "0", "내 덱": m["my_decks"][0], "상대 덱": m["opp_decks"][0], "아키타입": "", "승패 요인": m["win_loss_reasons"][0], "특정 카드": "", "브릭": False, "실수": False, "비고": ""}])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        save_records(st.session_state.df)
        st.rerun()

    edited = st.data_editor(
        st.session_state.df, use_container_width=True, num_rows="dynamic", hide_index=True, key="editor_vfinal",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width=50),
            "날짜": st.column_config.TextColumn("날짜", width=60),
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"], width=70),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"], width=60),
            "세트": st.column_config.SelectboxColumn("세트", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"], width=60),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata["my_decks"], width=60),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata["opp_decks"], width=80),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.metadata["archetypes"], width=80),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.metadata["win_loss_reasons"], width=80),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.metadata["target_cards"], width=80),
            "브릭": st.column_config.CheckboxColumn("브릭", width=60),
            "실수": st.column_config.CheckboxColumn("실수", width=60),
            "비고": st.column_config.TextColumn("비고", width=350)
        }
    )
    if not edited.equals(st.session_state.df):
        save_records(edited)
        st.rerun()

# --- PAGE: Analysis ---
elif page == "📈 Analysis":
    st.title("📈 Rating Analysis")
    df_ana = load_records()
    if not df_ana.empty:
        calc_df = df_ana[df_ana['결과'].isin(['승', '패'])].copy()
        
        # 분석용 수치 컬럼 생성
        calc_df['is_win'] = calc_df['결과'].apply(lambda x: 1 if x == '승' else 0)
        calc_df['is_loss'] = calc_df['결과'].apply(lambda x: 1 if x == '패' else 0)
        calc_df['is_1st'] = calc_df['선후공'].apply(lambda x: 1 if x == '선' else 0)
        calc_df['is_2nd'] = calc_df['선후공'].apply(lambda x: 1 if x == '후' else 0)
        calc_df['win_1st'] = ((calc_df['is_1st'] == 1) & (calc_df['is_win'] == 1)).astype(int)
        calc_df['win_2nd'] = ((calc_df['is_2nd'] == 1) & (calc_df['is_win'] == 1)).astype(int)
        calc_df['has_arch'] = calc_df['아키타입'].apply(lambda x: 1 if str(x).strip() != "" else 0)

        col_left, col_right = st.columns([1, 2.2])
        
        with col_left:
            st.markdown('<div class="analysis-left-wrapper">', unsafe_allow_html=True)
            # 1. Overall Data
            st.markdown(render_summary_table("Overall Data", calc_df), unsafe_allow_html=True)
            st.write("---")
            
            # 2. 내 덱별 승률
            st.subheader("내 덱별 승률")
            sel_my = st.selectbox("내 덱 선택", st.session_state.metadata["my_decks"], key="sel_my_ana")
            my_deck_df = calc_df[calc_df['내 덱'] == sel_my]
            st.markdown(render_summary_table(f"Result: {sel_my}", my_deck_df), unsafe_allow_html=True)
            st.write("---")
            
            # 3. 특정 매치업 상세
            st.subheader("상대 덱별 상세")
            c1, c2 = st.columns(2)
            with c1: m_my = st.selectbox("Use.Deck", st.session_state.metadata["my_decks"], key="m_my_box")
            with c2: m_opp = st.selectbox("Opp.Deck", st.session_state.metadata["opp_decks"], key="m_opp_box")
            st.markdown(render_summary_table(f"{m_my} vs {m_opp}", calc_df[(calc_df['내 덱']==m_my)&(calc_df['상대 덱']==m_opp)]), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.subheader("📊 Opponent Deck Statistics")
            # 현재 선택된 내 덱(sel_my)을 기준으로 상대 덱 통계 산출
            target_df = calc_df[calc_df['내 덱'] == sel_my].copy()
            if not target_df.empty:
                agg = target_df.groupby('상대 덱').agg({
                    '결과': 'count', 'is_win': 'sum', 'is_loss': 'sum',
                    'is_1st': 'sum', 'win_1st': 'sum', 'is_2nd': 'sum', 'win_2nd': 'sum', 'has_arch': 'sum'
                }).rename(columns={'결과': 'Total', 'is_win': 'W', 'is_loss': 'L'})
                
                total_m = agg['Total'].sum()
                agg['W%'] = agg['W'] / agg['Total'] * 100
                agg['1st W%'] = agg['win_1st'] / agg['is_1st'] * 100
                agg['2nd W%'] = agg['win_2nd'] / agg['is_2nd'] * 100
                agg['Share'] = agg['Total'] / total_m * 100
                agg['Plus Arch'] = agg['has_arch'] / agg['Total'] * 100
                agg = agg.sort_values(by='Total', ascending=False)

                # 큰 통계 표 HTML 생성
                headers = ['Matchup', 'Total', 'W', 'L', 'W%', '1st W%', '2nd W%', 'Share', 'Plus Arch']
                html = '<table class="styled-table"><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr>'
                
                # 합계 행 (Total Row)
                t_w, t_l, t_1, t_1w, t_2, t_2w, t_a = agg['W'].sum(), agg['L'].sum(), agg['is_1st'].sum(), agg['win_1st'].sum(), agg['is_2nd'].sum(), agg['win_2nd'].sum(), agg['has_arch'].sum()
                html += f'<tr style="background-color:#fff2cc; font-weight:bold;"><td>Total</td><td>{total_m}</td><td class="win-val">{t_w}</td><td class="loss-val">{t_l}</td><td>{(t_w/total_m*100):.2f}%</td><td>{(t_1w/t_1*100 if t_1>0 else 0):.2f}%</td><td>{(t_2w/t_2*100 if t_2>0 else 0):.2f}%</td><td>100.00%</td><td>{(t_a/total_m*100):.2f}%</td></tr>'
                
                for deck, row in agg.iterrows():
                    html += f'<tr><td>{deck}</td><td>{int(row["Total"])}</td><td class="win-val">{int(row["W"])}</td><td class="loss-val">{int(row["L"])}</td><td>{row["W%"]:.2f}%</td>'
                    html += f'<td>{row["1st W%"]:.2f}%</td>' if pd.notnull(row["1st W%"]) else '<td>-</td>'
                    html += f'<td>{row["2nd W%"]:.2f}%</td>' if pd.notnull(row["2nd W%"]) else '<td>-</td>'
                    html += f'<td>{row["Share"]:.2f}%</td><td>{row["Plus Arch"]:.2f}%</td></tr>'
                
                st.markdown(html + '</table>', unsafe_allow_html=True)
            else:
                st.info(f"'{sel_my}' 덱의 매치업 데이터가 없습니다.")

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
