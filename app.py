import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. [디자인] 엑셀 스타일 헤더 및 테이블 커스텀 ---
st.markdown("""
    <style>
    /* 공통: 데이터 에디터 중앙 정렬 및 폰트 크기 */
    [data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"] div {
        text-align: center !important;
        font-size: 13px !important;
    }

    /* Record 페이지 헤더 색상 */
    div[data-testid="stDataFrameResizable"] th:nth-child(1),
    div[data-testid="stDataFrameResizable"] th:nth-child(2),
    div[data-testid="stDataFrameResizable"] th:nth-child(3),
    div[data-testid="stDataFrameResizable"] th:nth-child(4),
    div[data-testid="stDataFrameResizable"] th:nth-child(5) {
        background-color: #a2d5c6 !important;
        color: #31333F !important;
    }
    div[data-testid="stDataFrameResizable"] th:nth-child(6),
    div[data-testid="stDataFrameResizable"] th:nth-child(7),
    div[data-testid="stDataFrameResizable"] th:nth-child(8),
    div[data-testid="stDataFrameResizable"] th:nth-child(9),
    div[data-testid="stDataFrameResizable"] th:nth-child(10),
    div[data-testid="stDataFrameResizable"] th:nth-child(11) {
        background-color: #f9cb9c !important;
    }
    div[data-testid="stDataFrameResizable"] th:nth-child(12),
    div[data-testid="stDataFrameResizable"] th:nth-child(13) {
        background-color: #ffe599 !important;
    }

    /* 분석 페이지 요약 표 스타일 */
    .styled-table { 
        width: 100%; font-size: 12px; border-collapse: collapse; 
        margin-bottom: 20px; table-layout: fixed; border: 1px solid #dee2e6;
    }
    .styled-table th, .styled-table td { 
        text-align: center !important; border: 1px solid #dee2e6 !important; padding: 4px !important; 
    }
    .styled-table th { background-color: #f9cb9c !important; color: #31333F !important; font-weight: bold !important; }
    .win-val { color: #0000ff !important; font-weight: bold; }
    .loss-val { color: #ff0000 !important; font-weight: bold; }
    
    .analysis-left-wrapper { max-width: 450px; }

    /* 맞춤법 빨간줄 제거를 위한 속성 강제 적용 */
    textarea, input {
        spellcheck: false !important;
    }
    </style>
    
    <script>
    // 브라우저 레벨에서 맞춤법 검사 비활성화
    document.querySelectorAll('textarea, input').forEach(el => {
        el.setAttribute('spellcheck', 'false');
    });
    </script>
""", unsafe_allow_html=True)

# --- 3. 데이터 관리 로직 ---
def load_metadata():
    default_meta = {
        "my_decks": ["KT", "Ennea", "Maliss"],
        "opp_decks": ["Mitsu", "Ennea", "Branded", "Striker", "Tenpai"],
        "archetypes": ["운영", "전개", "미드레인지", "기타"],
        "win_loss_reasons": ["자신 실력", "상대 패", "특정 카드", "선후공", "상성"],
        "target_cards": ["TT Talent", "Droll", "Nibiru", "Fuwalos"]
    }
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: pass
    return default_meta

def load_records():
    cols = ["NO.", "날짜", "선후공", "결과", "세트", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE, dtype=str).fillna("")
        for col in ["브릭", "실수"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: True if str(x).lower() in ['true', '1'] else False)
        return df
    return pd.DataFrame(columns=cols)

def save_data(df):
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
            <tr><td>Result</td><td class="win-val">{f_t}</td><td class="loss-val">{s_t}</td><td class="win-val">{(f_t/total*100 if total>0 else 0):.1f}%</td><td class="loss-val">{(s_t/total*100 if total>0 else 0):.1f}%</td></tr>
            <tr><th>1st</th><th>1st Win</th><th>1st Lose</th><th>1st W%</th><th>1st L%</th></tr>
            <tr><td>Result</td><td class="win-val">{f_w}</td><td class="loss-val">{f_t-f_w}</td><td class="win-val">{(f_w/f_t*100 if f_t>0 else 0):.1f}%</td><td class="loss-val">{(100-(f_w/f_t*100) if f_t>0 else 0):.1f}%</td></tr>
            <tr><th>2nd</th><th>2nd Win</th><th>2nd Lose</th><th>2nd W%</th><th>2nd L%</th></tr>
            <tr><td>Result</td><td class="win-val">{s_w}</td><td class="loss-val">{s_t-s_w}</td><td class="win-val">{(s_w/s_t*100 if s_t>0 else 0):.1f}%</td><td class="loss-val">{(100-(s_w/s_t*100) if s_t>0 else 0):.1f}%</td></tr>
        </table>
    """

# --- 4. 앱 메인 ---
if 'metadata' not in st.session_state: st.session_state.metadata = load_metadata()
if 'df' not in st.session_state: st.session_state.df = load_records()

page = st.sidebar.radio("메뉴", ["📊 Record", "📈 Analysis", "⚙️ Setting"])

# --- PAGE: Record ---
if page == "📊 Record":
    st.title("📊 Match Record")
    if st.button("➕ 새로운 경기 추가"):
        m = st.session_state.metadata
        new_row = pd.DataFrame([{"NO.": str(len(st.session_state.df)+1), "날짜": pd.Timestamp.now().strftime("%m.%d"), "선후공": "선", "결과": "승", "세트": "OO", "점수": "0", "내 덱": m["my_decks"][0], "상대 덱": m["opp_decks"][0], "아키타입": "", "승패 요인": m["win_loss_reasons"][0], "특정 카드": "", "브릭": False, "실수": False, "비고": ""}])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        save_data(st.session_state.df)
        st.rerun()

    edited = st.data_editor(
        st.session_state.df, use_container_width=True, num_rows="dynamic", hide_index=True, key="editor_final_v2",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width=40),
            "날짜": st.column_config.TextColumn("날짜", width=60),
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"], width=60),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"], width=60),
            "세트": st.column_config.SelectboxColumn("세트", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"], width=80),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata["my_decks"], width=100),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata["opp_decks"], width=100),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.metadata["archetypes"], width=100),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.metadata["win_loss_reasons"], width=100),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.metadata["target_cards"], width=100),
            "브릭": st.column_config.CheckboxColumn("브릭", width=50),
            "실수": st.column_config.CheckboxColumn("실수", width=50),
            "비고": st.column_config.TextColumn("비고", width=350)
        }
    )
    if not edited.equals(st.session_state.df):
        save_data(edited)
        st.rerun()

# --- PAGE: Analysis ---
elif page == "📈 Analysis":
    st.title("📈 Rating Analysis")
    df_ana = load_records()
    if not df_ana.empty:
        calc_df = df_ana[df_ana['결과'].isin(['승', '패'])].copy()
        for c in ['is_win','is_loss','is_1st','is_2nd','win_1st','win_2nd','has_arch']: calc_df[c] = 0
        calc_df.loc[calc_df['결과']=='승', 'is_win'] = 1
        calc_df.loc[calc_df['결과']=='패', 'is_loss'] = 1
        calc_df.loc[calc_df['선후공']=='선', 'is_1st'] = 1
        calc_df.loc[calc_df['선후공']=='후', 'is_2nd'] = 1
        calc_df.loc[(calc_df['is_1st']==1)&(calc_df['is_win']==1), 'win_1st'] = 1
        calc_df.loc[(calc_df['is_2nd']==1)&(calc_df['is_win']==1), 'win_2nd'] = 1
        calc_df.loc[calc_df['아키타입']!="", 'has_arch'] = 1

        col_left, col_right = st.columns([1, 2.2])
        with col_left:
            st.markdown('<div class="analysis-left-wrapper">', unsafe_allow_html=True)
            st.markdown(render_summary_table("Overall Data", calc_df), unsafe_allow_html=True)
            st.write("---")
            st.subheader("내 덱별 승률")
            sel_my = st.selectbox("내 덱 선택", st.session_state.metadata["my_decks"])
            st.markdown(render_summary_table(f"Result: {sel_my}", calc_df[calc_df['내 덱']==sel_my]), unsafe_allow_html=True)
            st.write("---")
            st.subheader("상대 덱별 상세")
            c1, c2 = st.columns(2)
            with c1: m_my = st.selectbox("Use.Deck", st.session_state.metadata["my_decks"], key="m1")
            with c2: m_opp = st.selectbox("Opp.Deck", st.session_state.metadata["opp_decks"], key="m2")
            st.markdown(render_summary_table(f"{m_my} vs {m_opp}", calc_df[(calc_df['내 덱']==m_my)&(calc_df['상대 덱']==m_opp)]), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.subheader("📊 Opponent Deck Statistics")
            target = calc_df[calc_df['내 덱']==sel_my].copy()
            if not target.empty:
                agg = target.groupby('상대 덱').agg({'결과':'count','is_win':'sum','is_loss':'sum','is_1st':'sum','win_1st':'sum','is_2nd':'sum','win_2nd':'sum','has_arch':'sum'}).rename(columns={'결과':'Total','is_win':'W','is_loss':'L'})
                total_m = agg['Total'].sum()
                agg['W%'] = agg['W']/agg['Total']*100
                agg['1st W%'] = agg['win_1st']/agg['is_1st']*100
                agg['2nd W%'] = agg['win_2nd']/agg['is_2nd']*100
                agg['Share'] = agg['Total']/total_m*100
                agg['Plus Arch'] = agg['has_arch']/agg['Total']*100
                agg = agg.sort_values('Total', ascending=False)

                html = '<table class="styled-table"><tr><th>Matchup</th><th>Total</th><th>W</th><th>L</th><th>W%</th><th>1st W%</th><th>2nd W%</th><th>Share</th><th>Plus Arch</th></tr>'
                t_w, t_l, t_1, t_1w, t_2, t_2w, t_a = agg['W'].sum(), agg['L'].sum(), agg['is_1st'].sum(), agg['win_1st'].sum(), agg['is_2nd'].sum(), agg['win_2nd'].sum(), agg['has_arch'].sum()
                html += f'<tr style="background-color:#fff2cc; font-weight:bold;"><td>Total</td><td>{total_m}</td><td class="win-val">{t_w}</td><td class="loss-val">{t_l}</td><td>{(t_w/total_m*100):.2f}%</td><td>{(t_1w/t_1*100 if t_1>0 else 0):.2f}%</td><td>{(t_2w/t_2*100 if t_2>0 else 0):.2f}%</td><td>100%</td><td>{(t_a/total_m*100):.2f}%</td></tr>'
                for d, r in agg.iterrows():
                    html += f'<tr><td>{d}</td><td>{int(r["Total"])}</td><td class="win-val">{int(r["W"])}</td><td class="loss-val">{int(r["L"])}</td><td>{r["W%"]:.2f}%</td><td>{r["1st W%"]:.2f}%</td><td>{r["2nd W%"]:.2f}%</td><td>{r["Share"]:.2f}%</td><td>{r["Plus Arch"]:.2f}%</td></tr>'
                st.markdown(html+'</table>', unsafe_allow_html=True)

# --- PAGE: Setting ---
else:
    st.title("⚙️ Setting")
    st.info("각 항목을 한 줄에 하나씩 입력해 주세요 (Enter로 구분).")
    meta = st.session_state.metadata
    
    c1, c2 = st.columns(2)
    # 줄바꿈(\n)으로 표시되도록 리스트를 문자열로 합침
    with c1: new_my = st.text_area("내 덱 (한 줄에 하나)", "\n".join(meta["my_decks"]), height=200)
    with c2: new_opp = st.text_area("상대 덱 (한 줄에 하나)", "\n".join(meta["opp_decks"]), height=200)
    
    c3, c4 = st.columns(2)
    with c3: new_reasons = st.text_area("승패 요인 (한 줄에 하나)", "\n".join(meta["win_loss_reasons"]), height=150)
    with c4: new_arche = st.text_area("아키타입 (한 줄에 하나)", "\n".join(meta["archetypes"]), height=150)
    
    new_cards = st.text_area("특정 카드 (한 줄에 하나)", "\n".join(meta["target_cards"]), height=150)
    
    if st.button("✅ 설정 저장"):
        # 줄바꿈으로 분리하고 빈 줄은 제거
        st.session_state.metadata = {
            "my_decks": [x.strip() for x in new_my.split("\n") if x.strip()],
            "opp_decks": [x.strip() for x in new_opp.split("\n") if x.strip()],
            "win_loss_reasons": [x.strip() for x in new_reasons.split("\n") if x.strip()],
            "archetypes": [x.strip() for x in new_arche.split("\n") if x.strip()],
            "target_cards": [x.strip() for x in new_cards.split("\n") if x.strip()]
        }
        with open(META_FILE, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.metadata, f, ensure_ascii=False, indent=4)
        st.success("설정이 저장되었습니다!")
        st.rerun()
