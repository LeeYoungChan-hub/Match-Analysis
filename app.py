import hashlib
import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 표(data_editor) 스타일 설정
CELL_FONT_PX = "10px"
COL_W_NO_TO_SCORE = "92px"
COL_W_STATUS = "45px" # 색상 칸 너비 최소화

def _compact_layout_css() -> None:
    st.markdown(
        f"""
        <style>
        .block-container {{ padding-top: 0.45rem !important; padding-bottom: 0.3rem !important; padding-left: 0.55rem !important; padding-right: 0.55rem !important; max-width: 100% !important; }}
        [data-testid="stDataFrame"] {{ margin-bottom: 0.15rem !important; font-size: {CELL_FONT_PX} !important; }}
        [data-testid="stDataFrame"] [role="gridcell"], [data-testid="stDataFrame"] [role="columnheader"] {{ text-align: center !important; justify-content: center !important; }}
        /* 드롭다운 내부 텍스트 정렬 */
        div[data-testid="stDataFrame"] select {{ text-align: center !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

_compact_layout_css()

# 2. 데이터 및 설정값 초기화
FILENAME = "2026.03 레이팅 - Record.csv"
# 문자를 제거하고 이모지만 남김
STATUS_OPTS = ["⚪", "🔵", "🟠"]

if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv(FILENAME)
        if "세트 전적" in st.session_state.df.columns:
            st.session_state.df = st.session_state.df.rename(columns={"세트 전적": "세트"})
        if "상태" not in st.session_state.df.columns:
            st.session_state.df.insert(1, "상태", "⚪")
        st.session_state.df['브릭'] = pd.to_numeric(st.session_state.df['브릭'], errors='coerce').fillna(0).astype(bool)
        st.session_state.df['실수'] = pd.to_numeric(st.session_state.df['실수'], errors='coerce').fillna(0).astype(bool)
    except:
        columns = ["NO.", "상태", "날짜", "선후공", "결과", "세트", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        sub_label_row = {
            "NO.": "0", "상태": "⚪", "날짜": "Date", "선후공": "0.00%", "결과": "0.00%",
            "세트": "Result", "점수": "0", "내 덱": "Use.deck", "상대 덱": "Opp. deck", 
            "아키타입": "Plus Arch.", "승패 요인": "W/L Factor", "특정 카드": "Certain Card", 
            "브릭": "0", "실수": "0", "비고": "Detail"
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

# --- 로직 함수들 (기본 구조 유지) ---
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

def _sync_guide_stats_row(guide: pd.DataFrame, stats_src: pd.DataFrame) -> None:
    if len(stats_src) == 0: return
    last = stats_src.iloc[-1]
    guide.iloc[0, guide.columns.get_loc("NO.")] = _display_cell_str(last["NO."])
    guide.iloc[0, guide.columns.get_loc("점수")] = _display_cell_str(last["점수"])
    b_sum, m_sum = _brick_mistake_sums(stats_src)
    guide.iloc[0, guide.columns.get_loc("브릭")] = b_sum
    guide.iloc[0, guide.columns.get_loc("실수")] = m_sum

def _apply_guide_stats_from_records(guide: pd.DataFrame, records: pd.DataFrame) -> pd.DataFrame:
    g = guide.copy()
    if len(records) == 0: return g
    total = len(records)
    wins = len(records[records["결과"] == "승"])
    firsts = len(records[records["선후공"] == "선"])
    b_cnt, m_cnt = _brick_mistake_sums(records)
    g.iloc[0, g.columns.get_loc("NO.")] = _display_cell_str(records.iloc[-1]["NO."])
    g.iloc[0, g.columns.get_loc("점수")] = _display_cell_str(records.iloc[-1]["점수"])
    g.iloc[0, g.columns.get_loc("결과")] = f"{(wins / total) * 100:.2f}%"
    g.iloc[0, g.columns.get_loc("선후공")] = f"{(firsts / total) * 100:.2f}%"
    g.iloc[0, g.columns.get_loc("브릭")] = int(b_cnt)
    g.iloc[0, g.columns.get_loc("실수")] = int(m_cnt)
    return g

def _single_guide_row(guide: pd.DataFrame) -> pd.DataFrame:
    return guide.iloc[[0]].copy().reset_index(drop=True)

def _sanitize_for_editor(df: pd.DataFrame, is_guide=False) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        if c not in ["브릭", "실수"]: out[c] = out[c].map(_display_cell_str)
    if is_guide:
        for c in ["브릭", "실수"]: out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(int)
    else:
        for c in ["브릭", "실수"]: out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(bool)
    return out

# 3. 탭 구성
tab_record, tab_setting = st.tabs(["📊 Record", "⚙️ Setting"])

with tab_record:
    st.title("📊 Rating Dashboard")
    
    guide_df = _single_guide_row(st.session_state.df.iloc[[0]].copy())
    data_df = st.session_state.df.iloc[1:].copy()

    stats_src = st.session_state.get("last_edited_record_data", data_df)
    _sync_guide_stats_row(guide_df, stats_src)

    guide_df = _sanitize_for_editor(guide_df, is_guide=True)
    data_df = _sanitize_for_editor(data_df, is_guide=False)

    st.subheader("📋 가이드 및 통계")
    edited_guide = st.data_editor(
        guide_df, use_container_width=True, height=96, num_rows="fixed", hide_index=True, key="guide_stats_one_row",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", disabled=True, width="50px"),
            "상태": st.column_config.TextColumn(" ", disabled=True, width=COL_W_STATUS), # 헤더 이름 비움
            "점수": st.column_config.TextColumn("점수", disabled=True, width=COL_W_NO_TO_SCORE),
            "브릭": st.column_config.NumberColumn("브릭", format="%d", disabled=True),
            "실수": st.column_config.NumberColumn("실수", format="%d", disabled=True),
        }
    )

    st.subheader("📝 경기 기록")
    edited_data = st.data_editor(
        data_df, num_rows="dynamic", use_container_width=True, height=500, key="data_editor",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width="50px"),
            "상태": st.column_config.SelectboxColumn(" ", options=STATUS_OPTS, width=COL_W_STATUS), # 텍스트 없이 색상만
            "선후공": st.column_config.SelectboxColumn("선후공", options=["", "선", "후"], width="65px"),
            "결과": st.column_config.SelectboxColumn("결과", options=["", "승", "패"], width="65px"),
            "브릭": st.column_config.CheckboxColumn("브릭", default=False),
            "실수": st.column_config.CheckboxColumn("실수", default=False),
        }
    )
    st.session_state.last_edited_record_data = edited_data.copy()

    if st.button("💾 저장", type="primary", use_container_width=True):
        guide_to_save = _apply_guide_stats_from_records(_single_guide_row(edited_guide), edited_data)
        # 병합 전 상태 값 보정 (공백 제거 등)
        edited_data["상태"] = edited_data["상태"].fillna("⚪")
        merged = pd.concat([guide_to_save, edited_data], ignore_index=True)
        st.session_state.df = merged
        merged.to_csv(FILENAME, index=False, encoding="utf-8-sig")
        st.success("저장되었습니다.")
        st.rerun()
