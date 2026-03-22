import hashlib
import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 열 너비 설정 (사용자 요청 반영)
CELL_FONT_PX = "10px"
COL_W_STATUS = 30  # 색상 셀 30
COL_W_NO = 80      # NO. 셀 확대
COL_W_SMALL = 55   # 선후공, 결과 셀 축소
COL_W_FIXED = "92px"

def _compact_layout_css() -> None:
    st.markdown(
        f"""
        <style>
        .block-container {{ padding-top: 0.45rem !important; padding-bottom: 0.5rem !important; padding-left: 0.55rem !important; padding-right: 0.55rem !important; max-width: 100% !important; }}
        [data-testid="stDataFrame"] {{ margin-bottom: 0.15rem !important; font-size: {CELL_FONT_PX} !important; }}
        
        /* 중앙 정렬 및 여백 최적화 */
        [data-testid="stDataFrame"] [role="gridcell"], 
        [data-testid="stDataFrame"] [role="columnheader"] {{ 
            text-align: center !important; 
            justify-content: center !important; 
            padding: 0px !important;
        }}
        
        /* 하단 탭 스타일 강조 */
        .stTabs [data-baseweb="tab-list"] {{
            justify-content: center !important;
            border-top: 1px solid #ddd;
            padding-top: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

_compact_layout_css()

# 2. 데이터 초기화
FILENAME = "2026.03 레이팅 - Record.csv"
STATUS_OPTS = ["⚪", "🔵", "🟠"]

if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv(FILENAME)
        if "상태" not in st.session_state.df.columns:
            st.session_state.df.insert(1, "상태", "⚪")
        st.session_state.df['브릭'] = pd.to_numeric(st.session_state.df['브릭'], errors='coerce').fillna(0).astype(bool)
        st.session_state.df['실수'] = pd.to_numeric(st.session_state.df['실수'], errors='coerce').fillna(0).astype(bool)
    except:
        columns = ["NO.", "상태", "날짜", "선후공", "결과", "세트", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        sub_label_row = {
            "NO.": "Game No.", "상태": "⚪", "날짜": "Date", "선후공": "0%", "결과": "0%",
            "세트": "Res", "점수": "0", "내 덱": "My", "상대 덱": "Opp", "아키타입": "Arch",
            "승패 요인": "Factor", "특정 카드": "Card", "브릭": 0, "실수": 0, "비고": "Note"
        }
        st.session_state.df = pd.DataFrame([sub_label_row], columns=columns)

if 'options' not in st.session_state:
    st.session_state.options = {
        "내 덱": ["KT", "SwoS", "Synchron"],
        "상대 덱": ["Mitsu", "Ennea", "DD", "Red Dra", "Branded", "Maliss"],
        "특정 카드": ["TT Talent", "Droll", "Nibiru"],
        "승패 요인": ["자신 실력", "상대 패", "특정 카드", "운"],
        "아키타입": ["60", "Arch"]
    }

# --- 필수 헬퍼 함수 ---
def _brick_mistake_sums(df: pd.DataFrame) -> tuple[int, int]:
    b = pd.to_numeric(df["브릭"], errors="coerce").fillna(0).astype(bool)
    m = pd.to_numeric(df["실수"], errors="coerce").fillna(0).astype(bool)
    return int(b.sum()), int(m.sum())

def _display_cell_str(v) -> str:
    if v is None or pd.isna(v): return ""
    try:
        fv = float(v)
        if fv.is_integer(): return str(int(fv))
    except (TypeError, ValueError): pass
    return str(v)

def _sanitize_for_editor(df: pd.DataFrame, is_guide=False) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        if c not in ["브릭", "실수"]: out[c] = out[c].map(_display_cell_str)
    if is_guide:
        for c in ["브릭", "실수"]: out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(int)
    else:
        for c in ["브릭", "실수"]: out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(bool)
    return out

# ---------------------------------------------------------
# 메인 레이아웃 (상단 기록 -> 하단 탭 메뉴)
# ---------------------------------------------------------
st.title("📊 Rating Dashboard")

# 가이드와 데이터 분리
guide_df = _sanitize_for_editor(st.session_state.df.iloc[[0]], is_guide=True)
data_df = _sanitize_for_editor(st.session_state.df.iloc[1:], is_guide=False)

# 하단 탭으로 페이지 분리
tab_record, tab_setting = st.tabs(["🎮 Game Record", "⚙️ Dashboard Settings"])

with tab_record:
    st.subheader("📋 가이드 및 통계")
    st.data_editor(
        guide_df, use_container_width=True, height=95, num_rows="fixed", hide_index=True,
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width=COL_W_NO),
            "상태": st.column_config.TextColumn(" ", width=COL_W_STATUS),
            "선후공": st.column_config.TextColumn("선후공", width=COL_W_SMALL),
            "결과": st.column_config.TextColumn("결과", width=COL_W_SMALL),
            "점수": st.column_config.TextColumn("점수", width=COL_W_FIXED),
        }
    )

    st.subheader("📝 경기 기록")
    edited_data = st.data_editor(
        data_df, num_rows="dynamic", use_container_width=True, height=550, key="main_editor",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width=COL_W_NO),
            "상태": st.column_config.SelectboxColumn(" ", options=STATUS_OPTS, width=COL_W_STATUS),
            "선후공": st.column_config.SelectboxColumn("선/후", options=["", "선", "후"], width=COL_W_SMALL),
            "결과": st.column_config.SelectboxColumn("결과", options=["", "승", "패"], width=COL_W_SMALL),
            "점수": st.column_config.TextColumn("점수", width=COL_W_FIXED),
            "브릭": st.column_config.CheckboxColumn("브릭"),
            "실수": st.column_config.CheckboxColumn("실수"),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=[""] + st.session_state.options["내 덱"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=[""] + st.session_state.options["상대 덱"]),
        }
    )

    if st.button("💾 데이터 저장", type="primary", use_container_width=True):
        # 통계 재계산 로직
        total = len(edited_data)
        wins = len(edited_data[edited_data["결과"] == "승"])
        firsts = len(edited_data[edited_data["선후공"] == "선"])
        b_sum, m_sum = _brick_mistake_sums(edited_data)
        
        # 가이드 행 업데이트
        if total > 0:
            guide_df.iloc[0, guide_df.columns.get_loc("결과")] = f"{(wins/total)*100:.1f}%"
            guide_df.iloc[0, guide_df.columns.get_loc("선후공")] = f"{(firsts/total)*100:.1f}%"
            guide_df.iloc[0, guide_df.columns.get_loc("NO.")] = str(edited_data.iloc[-1]["NO."])
            guide_df.iloc[0, guide_df.columns.get_loc("점수")] = str(edited_data.iloc[-1]["점수"])
            guide_df.iloc[0, guide_df.columns.get_loc("브릭")] = b_sum
            guide_df.iloc[0, guide_df.columns.get_loc("실수")] = m_sum
        
        merged = pd.concat([guide_df, edited_data], ignore_index=True)
        st.session_state.df = merged
        merged.to_csv(FILENAME, index=False, encoding="utf-8-sig")
        st.success("저장 완료!")
        st.rerun()

with tab_setting:
    st.subheader("⚙️ 덱 및 카드 목록 관리")
    c1, c2, c3 = st.columns(3)
    with c1:
        new_my = st.text_area("내 덱", value="\n".join(st.session_state.options["내 덱"]), height=250)
    with c2:
        new_opp = st.text_area("상대 덱", value="\n".join(st.session_state.options["상대 덱"]), height=250)
    with c3:
        new_card = st.text_area("특정 카드", value="\n".join(st.session_state.options["특정 카드"]), height=250)
    
    if st.button("✅ 변경 사항 적용", use_container_width=True):
        st.session_state.options["내 덱"] = [x.strip() for x in new_my.split("\n") if x.strip()]
        st.session_state.options["상대 덱"] = [x.strip() for x in new_opp.split("\n") if x.strip()]
        st.session_state.options["특정 카드"] = [x.strip() for x in new_card.split("\n") if x.strip()]
        st.success("설정되었습니다.")
