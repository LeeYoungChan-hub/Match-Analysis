import streamlit as st
import pandas as pd
import plotly.express as px # 차트 시각화를 위해 추가

# 1. 페이지 설정
st.set_page_config(page_title="Rating Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 스타일 설정
CELL_FONT_PX = "10px"
COL_W_STATUS = 30  
COL_W_NO = 80      
COL_W_SMALL = 55   
COL_W_FIXED = "92px"

def _compact_layout_css() -> None:
    st.markdown(
        f"""
        <style>
        .block-container {{ padding: 0.5rem 0.6rem !important; max-width: 100% !important; }}
        [data-testid="stDataFrame"] {{ font-size: {CELL_FONT_PX} !important; }}
        [data-testid="stDataFrame"] [role="gridcell"], 
        [data-testid="stDataFrame"] [role="columnheader"] {{ 
            text-align: center !important; justify-content: center !important; padding: 0px !important;
        }}
        [data-testid="stDataFrame"] [role="gridcell"] input,
        [data-testid="stDataFrame"] [role="gridcell"] select {{
            font-size: {CELL_FONT_PX} !important;
        }}
        .stTabs [data-baseweb="tab-list"] {{ justify-content: center !important; border-top: 1px solid #ddd; padding-top: 10px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

_compact_layout_css()

# 2. 데이터 및 옵션 초기화
FILENAME = "2026.03 레이팅 - Record.csv"
STATUS_OPTS = ["⚪", "🔵", "🟠"]

if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv(FILENAME)
        for col in ['브릭', '실수']:
            st.session_state.df[col] = pd.to_numeric(st.session_state.df[col], errors='coerce').fillna(0).astype(bool)
    except:
        columns = ["NO.", "상태", "날짜", "선후공", "결과", "세트", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        st.session_state.df = pd.DataFrame([["0", "⚪", "Date", "0%", "0%", "Res", "0", "My", "Opp", "Arch", "Fact", "Card", False, False, "Note"]], columns=columns)

if 'options' not in st.session_state:
    st.session_state.options = {
        "내 덱": ["KT", "SwoS", "Synchron"],
        "상대 덱": ["Mitsu", "Ennea", "DD", "Red Dra", "Branded", "Maliss"],
        "특정 카드": ["TT Talent", "Droll", "Nibiru"],
        "승패 요인": ["자신 실력", "상대 패", "특정 카드", "운"],
        "아키타입": ["60", "Pure", "Engine"]
    }

# --- 헬퍼 함수 ---
def _sanitize_for_editor(df: pd.DataFrame, is_guide=False) -> pd.DataFrame:
    out = df.copy()
    cols = out.columns.tolist()
    for c in cols:
        if c not in ["브릭", "실수"]: out[c] = out[c].astype(str).replace("nan", "")
    if is_guide:
        for c in ["브릭", "실수"]: out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(int)
    else:
        for c in ["브릭", "실수"]: out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(bool)
    return out

# 3. 메인 레이아웃 (상단 제목)
st.title("📊 Rating Dashboard System")

# 하단 탭 구성
tab_record, tab_analysis, tab_setting = st.tabs(["🎮 Game Record", "📈 Analysis", "⚙️ Settings"])

# --- [TAB 1] RECORD ---
with tab_record:
    guide_df = _sanitize_for_editor(st.session_state.df.iloc[[0]], is_guide=True)
    data_df = _sanitize_for_editor(st.session_state.df.iloc[1:], is_guide=False)

    st.subheader("📋 Statistics Guide")
    st.data_editor(guide_df, use_container_width=True, height=95, num_rows="fixed", hide_index=True,
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width=COL_W_NO),
            "상태": st.column_config.TextColumn(" ", width=COL_W_STATUS),
            "선후공": st.column_config.TextColumn("선후공", width=COL_W_SMALL),
            "결과": st.column_config.TextColumn("결과", width=COL_W_SMALL),
        })

    st.subheader("📝 Record Editor")
    edited_data = st.data_editor(data_df, num_rows="dynamic", use_container_width=True, height=500, key="main_editor",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width=COL_W_NO),
            "상태": st.column_config.SelectboxColumn(" ", options=STATUS_OPTS, width=COL_W_STATUS),
            "선후공": st.column_config.SelectboxColumn("선/후", options=["", "선", "후"], width=COL_W_SMALL),
            "결과": st.column_config.SelectboxColumn("결과", options=["", "승", "패"], width=COL_W_SMALL),
            "세트": st.column_config.SelectboxColumn("세트", options=["", "승", "패"], width=COL_W_SMALL), # 드롭다운 복구
            "브릭": st.column_config.CheckboxColumn("브릭"),
            "실수": st.column_config.CheckboxColumn("실수"),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=[""] + st.session_state.options["내 덱"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=[""] + st.session_state.options["상대 덱"]),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=[""] + st.session_state.options["아키타입"]),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=[""] + st.session_state.options["특정 카드"]),
        })

    if st.button("💾 Save Data", type="primary", use_container_width=True):
        # 통계 계산 및 저장 로직
        total = len(edited_data)
        if total > 0:
            wins = len(edited_data[edited_data["결과"] == "승"])
            firsts = len(edited_data[edited_data["선후공"] == "선"])
            guide_df.iloc[0, guide_df.columns.get_loc("결과")] = f"{(wins/total)*100:.1f}%"
            guide_df.iloc[0, guide_df.columns.get_loc("선후공")] = f"{(firsts/total)*100:.1f}%"
            guide_df.iloc[0, 0] = str(edited_data.iloc[-1]["NO."])
        
        st.session_state.df = pd.concat([guide_df, edited_data], ignore_index=True)
        st.session_state.df.to_csv(FILENAME, index=False, encoding="utf-8-sig")
        st.success("Saved!")
        st.rerun()

# --- [TAB 2] ANALYSIS ---
with tab_analysis:
    st.subheader("📈 Match Performance Analysis")
    analysis_df = st.session_state.df.iloc[1:].copy()
    
    if len(analysis_df) > 0:
        col1, col2, col3, col4 = st.columns(4)
        total_v = len(analysis_df)
        win_v = len(analysis_df[analysis_df["결과"] == "승"])
        col1.metric("Total Games", f"{total_v}")
        col2.metric("Win Rate", f"{(win_v/total_v)*100:.1f}%")
        col3.metric("Bricks", f"{analysis_df['브릭'].sum()}")
        col4.metric("Mistakes", f"{analysis_df['실수'].sum()}")

        c1, c2 = st.columns(2)
        with c1:
            # 내 덱별 승률
            deck_stats = analysis_df.groupby("내 덱")["결과"].apply(lambda x: (x == "승").mean() * 100).reset_index()
            fig1 = px.bar(deck_stats, x="내 덱", y="결과", title="Win Rate by My Decks (%)", labels={'결과':'Win Rate'})
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            # 상대 덱 빈도
            opp_stats = analysis_df["상대 덱"].value_counts().reset_index()
            fig2 = px.pie(opp_stats, names="상대 덱", values="count", title="Opponent Deck Distribution")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data available for analysis. Please record games first.")

# --- [TAB 3] SETTINGS ---
with tab_setting:
    st.subheader("⚙️ List Management")
    c1, c2 = st.columns(2)
    with c1:
        new_my = st.text_area("My Decks", value="\n".join(st.session_state.options["내 덱"]), height=150)
        new_arch = st.text_area("Archetypes", value="\n".join(st.session_state.options["아키타입"]), height=150)
    with c2:
        new_opp = st.text_area("Opponent Decks", value="\n".join(st.session_state.options["상대 덱"]), height=150)
        new_card = st.text_area("Specific Cards", value="\n".join(st.session_state.options["특정 카드"]), height=150)
    
    if st.button("✅ Apply Settings", use_container_width=True):
        st.session_state.options["내 덱"] = [x.strip() for x in new_my.split("\n") if x.strip()]
        st.session_state.options["아키타입"] = [x.strip() for x in new_arch.split("\n") if x.strip()]
        st.session_state.options["상대 덱"] = [x.strip() for x in new_opp.split("\n") if x.strip()]
        st.session_state.options["특정 카드"] = [x.strip() for x in new_card.split("\n") if x.strip()]
        st.success("Settings Updated!")
