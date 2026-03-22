import hashlib

import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 표(data_editor) 셀 글자 크기 · NO.~점수 열 너비 (제목/캡션은 건드리지 않음)
CELL_FONT_PX = "10px"
COL_W_NO_TO_SCORE = "92px"


# 세로·좁은 화면 레이아웃 + 표만 스프레드시트 스타일
def _compact_layout_css() -> None:
    st.markdown(
        f"""
        <style>
        .block-container {{
            padding-top: 0.45rem !important;
            padding-bottom: 0.3rem !important;
            padding-left: 0.55rem !important;
            padding-right: 0.55rem !important;
            max-width: 100% !important;
        }}
        section[data-testid="stMain"] > div {{ padding-top: 0.3rem !important; padding-bottom: 0.2rem !important; }}
        h1 {{ font-size: clamp(1.1rem, 4vw, 1.5rem) !important; line-height: 1.2 !important; margin: 0 0 0.25rem 0 !important; padding: 0 !important; }}
        h2, h3 {{ font-size: clamp(0.95rem, 3.5vw, 1.15rem) !important; line-height: 1.2 !important; margin: 0.35rem 0 0.15rem 0 !important; padding: 0 !important; }}
        [data-testid="stCaption"] {{ margin-bottom: 0.25rem !important; font-size: 0.85rem !important; line-height: 1.35 !important; }}
        div[data-testid="stRadio"] label, div[data-testid="stRadio"] p {{ font-size: 0.95rem !important; }}
        .stTabs [data-baseweb="tab-list"] {{ min-height: 1.85rem !important; gap: 0.2rem !important; margin-bottom: 0 !important; }}
        .stTabs [data-baseweb="tab"] {{ padding: 0.28rem 0.5rem !important; font-size: 0.82rem !important; }}
        .stTabs [data-baseweb="tab-panel"] {{ padding-top: 0.28rem !important; }}
        div[data-testid="stVerticalBlock"] > div {{ gap: 0.28rem !important; }}
        div[data-testid="stElementContainer"] {{ margin-bottom: 0.25rem !important; }}
        /* 표 안 글자만 {CELL_FONT_PX} — 셀 높이·여백 맞춤 */
        [data-testid="stDataFrame"] {{ margin-bottom: 0.15rem !important; font-size: {CELL_FONT_PX} !important; }}
        [data-testid="stDataFrame"] [role="gridcell"],
        [data-testid="stDataFrame"] [role="columnheader"],
        [data-testid="stDataFrame"] [role="gridcell"] input,
        [data-testid="stDataFrame"] [role="gridcell"] select {{
            line-height: 1.25 !important;
            font-size: {CELL_FONT_PX} !important;
        }}
        [data-testid="stDataFrame"] [role="gridcell"],
        [data-testid="stDataFrame"] [role="columnheader"] {{
            min-height: 32px !important;
            padding-top: 6px !important;
            padding-bottom: 6px !important;
            box-sizing: border-box !important;
        }}
        [data-testid="stDataFrame"] [role="gridcell"],
        [data-testid="stDataFrame"] [role="columnheader"],
        [data-testid="stDataFrame"] [role="gridcell"] *,
        [data-testid="stDataFrame"] [role="columnheader"] * {{
            text-align: center !important;
            vertical-align: middle !important;
            justify-content: center !important;
        }}
        [data-testid="stDataFrame"] [role="gridcell"] label {{ justify-content: center !important; width: 100% !important; }}
        [data-testid="stDataFrame"] [role="columnheader"],
        [data-testid="stDataFrame"] [role="columnheader"] * {{
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        .stTabs [data-baseweb="tab-list"] {{ flex-wrap: nowrap !important; overflow-x: auto !important; width: 100% !important; }}
        .stDownloadButton {{ margin-top: 0.1rem !important; }}
        .stDownloadButton button {{ padding: 0.35rem 0.75rem !important; font-size: 0.9rem !important; min-height: 2.25rem !important; }}
        @media screen and (max-aspect-ratio: 1/1) {{
            .block-container {{ padding-top: 0.3rem !important; padding-bottom: 0.2rem !important; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


_compact_layout_css()

# 2. 데이터 및 설정값 초기화
FILENAME = "2026.03 레이팅 - Record.csv"

if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv(FILENAME)
        if "세트 전적" in st.session_state.df.columns:
            st.session_state.df = st.session_state.df.rename(columns={"세트 전적": "세트"})
        # 데이터 로드 시 체크박스 열을 불리언 타입으로 확실히 변환
        st.session_state.df['브릭'] = pd.to_numeric(st.session_state.df['브릭'], errors='coerce').fillna(0).astype(bool)
        st.session_state.df['실수'] = pd.to_numeric(st.session_state.df['실수'], errors='coerce').fillna(0).astype(bool)
    except:
        columns = ["NO.", "날짜", "선후공", "결과", "세트", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        sub_label_row = {
            "NO.": "0", "날짜": "Date", "선후공": "0.00%", "결과": "0.00%",
            "세트": "Result", "점수": "0", "내 덱": "Use.deck",
            "상대 덱": "Opp. deck", "아키타입": "Plus Arch.", "승패 요인": "W/L Factor",
            "특정 카드": "Certain Card", "브릭": "0", "실수": "0", "비고": "Detail"
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


def _brick_mistake_sums(df: pd.DataFrame) -> tuple[int, int]:
    b = pd.to_numeric(df["브릭"], errors="coerce").fillna(0).astype(bool)
    m = pd.to_numeric(df["실수"], errors="coerce").fillna(0).astype(bool)
    return int(b.sum()), int(m.sum())


def _display_cell_str(v) -> str:
    if v is None or pd.isna(v):
        return ""
    try:
        fv = float(v)
        if fv.is_integer():
            return str(int(fv))
    except (TypeError, ValueError):
        pass
    return str(v)


def _sync_guide_stats_row(guide: pd.DataFrame, stats_src: pd.DataFrame) -> None:
    """가이드 행의 NO., 점수, 브릭(합), 실수(합)를 경기 기록 기준으로 맞춤."""
    if len(stats_src) == 0:
        guide.iloc[0, guide.columns.get_loc("브릭")] = 0
        guide.iloc[0, guide.columns.get_loc("실수")] = 0
        return
    last = stats_src.iloc[-1]
    guide.iloc[0, guide.columns.get_loc("NO.")] = _display_cell_str(last["NO."])
    guide.iloc[0, guide.columns.get_loc("점수")] = _display_cell_str(last["점수"])
    brick_sum, mistake_sum = _brick_mistake_sums(stats_src)
    guide.iloc[0, guide.columns.get_loc("브릭")] = brick_sum
    guide.iloc[0, guide.columns.get_loc("실수")] = mistake_sum


def _apply_guide_stats_from_records(guide: pd.DataFrame, records: pd.DataFrame) -> pd.DataFrame:
    """저장용: 경기 기록으로 가이드 행의 통계 칸을 채운 복사본을 반환."""
    g = guide.copy()
    if len(records) == 0:
        return g
    total_games = len(records)
    win_count = len(records[records["결과"] == "승"])
    first_count = len(records[records["선후공"] == "선"])
    brick_count, mistake_count = _brick_mistake_sums(records)
    last_no = records.iloc[-1]["NO."]
    last_score = records.iloc[-1]["점수"]
    g.iloc[0, g.columns.get_loc("NO.")] = _display_cell_str(last_no)
    g.iloc[0, g.columns.get_loc("점수")] = _display_cell_str(last_score)
    g.iloc[0, g.columns.get_loc("결과")] = f"{(win_count / total_games) * 100:.2f}%"
    g.iloc[0, g.columns.get_loc("선후공")] = f"{(first_count / total_games) * 100:.2f}%"
    g.iloc[0, g.columns.get_loc("브릭")] = int(brick_count)
    g.iloc[0, g.columns.get_loc("실수")] = int(mistake_count)
    return g


def _single_guide_row(guide: pd.DataFrame) -> pd.DataFrame:
    """가이드는 항상 1행만 사용 (위젯/세션에서 빈 행이 붙는 경우 제거)."""
    if guide is None or len(guide) == 0:
        return guide
    return guide.iloc[[0]].copy().reset_index(drop=True)


def _sanitize_guide_for_editor(df: pd.DataFrame) -> pd.DataFrame:
    """data_editor(Text/Number)와 dtype 호환: CSV에서 온 float/int를 문자열·정수로 통일."""
    out = df.copy()
    for c in ["NO.", "날짜", "선후공", "결과", "세트", "점수"]:
        if c in out.columns:
            out[c] = out[c].map(_display_cell_str)
    for c in ["내 덱", "상대 덱", "특정 카드", "승패 요인", "아키타입", "비고"]:
        if c in out.columns:
            out[c] = out[c].map(_display_cell_str)
    for c in ["브릭", "실수"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(int)
    return out


def _sanitize_data_for_editor(df: pd.DataFrame) -> pd.DataFrame:
    """data_editor(Text/Selectbox/Checkbox)와 dtype 호환."""
    out = df.copy()
    for c in ["NO.", "날짜", "점수", "비고"]:
        if c in out.columns:
            out[c] = out[c].map(_display_cell_str)
    for c in ["선후공", "결과", "세트", "내 덱", "상대 덱", "특정 카드", "승패 요인", "아키타입"]:
        if c in out.columns:
            out[c] = out[c].map(_display_cell_str)
    for c in ["브릭", "실수"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(bool)
    return out


def _select_options(core: list[str]) -> list[str]:
    """드롭다운: 맨 앞에 빈 값(미선택) — 새 행은 사용자가 직접 고르게 둠."""
    return [""] + [o for o in core if o != ""]


def _ensure_selectbox_values(df: pd.DataFrame, col: str, options: list[str]) -> None:
    """빈 칸은 비움. 옵션에 없는 값만 빈 문자열로 보정(첫 항목으로 자동 채우지 않음)."""
    if col not in df.columns or not options:
        return
    allowed = set(_select_options(options))

    def _norm(v):
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return ""
        s = str(v).strip()
        if s == "":
            return ""
        return s if s in allowed else ""

    df[col] = df[col].map(_norm)


def _persist_record_csv(guide: pd.DataFrame, records: pd.DataFrame) -> None:
    merged = pd.concat([guide, records], ignore_index=True)
    csv_str = merged.to_csv(index=False, encoding="utf-8-sig")
    sig = hashlib.md5(csv_str.encode("utf-8-sig")).hexdigest()
    if st.session_state.get("_persist_csv_sig") == sig:
        return
    st.session_state._persist_csv_sig = sig
    st.session_state.df = merged
    try:
        with open(FILENAME, "w", encoding="utf-8-sig") as f:
            f.write(csv_str)
    except OSError as e:
        st.error(f"CSV 저장 실패: {e}")


# 3. Record / Setting — 탭으로 고정 (두 페이지 항상 표시)
tab_record, tab_setting = st.tabs(["📊 Record", "⚙️ Setting"])

# ---------------------------------------------------------
# Record (Rating Dashboard)
# ---------------------------------------------------------
with tab_record:
    if "세트 전적" in st.session_state.df.columns:
        st.session_state.df = st.session_state.df.rename(columns={"세트 전적": "세트"})

    st.title("📊 Rating Dashboard")
    st.caption("편집 후 💾 저장을 눌러야 CSV에 반영됩니다. (자동 저장 끔 — 렉 감소)")

    # 1행(가이드)과 나머지(데이터) 분리 — 가이드는 항상 1행만
    guide_df = _single_guide_row(st.session_state.df.iloc[[0]].copy())
    data_df = st.session_state.df.iloc[1:].copy()

    # 가이드가 위에 있어 같은 실행에서 편집 중인 표를 쓸 수 없음 → 직전 실행의 편집본 사용
    stats_src = st.session_state.get("last_edited_record_data", data_df)
    _sync_guide_stats_row(guide_df, stats_src)

    guide_df = _sanitize_guide_for_editor(guide_df)
    data_df = _sanitize_data_for_editor(data_df)
    opt = st.session_state.options
    for col, choices in [
        ("선후공", ["선", "후"]),
        ("결과", ["승", "패"]),
        ("세트", ["OO", "OXO", "XOO", "XX", "XOX", "OXX"]),
        ("내 덱", opt["내 덱"]),
        ("상대 덱", opt["상대 덱"]),
        ("특정 카드", opt["특정 카드"]),
        ("승패 요인", opt["승패 요인"]),
        ("아키타입", opt["아키타입"]),
    ]:
        _ensure_selectbox_values(data_df, col, choices)

    st.subheader("📋 가이드 및 통계")
    # 가이드는 1행만: 이전 실행에서 2행 이상이었으면 위젯 상태만 초기화
    if st.session_state.pop("_guide_reset_widget", False):
        st.session_state.pop("guide_stats_one_row", None)
    edited_guide = st.data_editor(
        _single_guide_row(guide_df),
        use_container_width=True,
        height=96,
        num_rows="fixed",
        hide_index=True,
        key="guide_stats_one_row",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", disabled=True, width=COL_W_NO_TO_SCORE),
            "날짜": st.column_config.TextColumn("날짜", width=COL_W_NO_TO_SCORE),
            "선후공": st.column_config.TextColumn("선후공", width=COL_W_NO_TO_SCORE),
            "결과": st.column_config.TextColumn("결과", width=COL_W_NO_TO_SCORE),
            "세트": st.column_config.TextColumn("세트", width=COL_W_NO_TO_SCORE),
            "점수": st.column_config.TextColumn("점수", disabled=True, width=COL_W_NO_TO_SCORE),
            "브릭": st.column_config.NumberColumn("브릭", format="%d", disabled=True),
            "실수": st.column_config.NumberColumn("실수", format="%d", disabled=True),
            "내 덱": st.column_config.TextColumn("내 덱"),
            "상대 덱": st.column_config.TextColumn("상대 덱"),
            "아키타입": st.column_config.TextColumn("아키타입"),
            "승패 요인": st.column_config.TextColumn("승패 요인"),
            "특정 카드": st.column_config.TextColumn("특정 카드"),
            "비고": st.column_config.TextColumn("비고"),
        },
    )
    if len(edited_guide) > 1:
        st.session_state._guide_reset_widget = True
        st.rerun()

    st.subheader("📝 경기 기록")
    _n = max(len(data_df), 1)
    _record_h = min(520, max(200, 72 + _n * 30))
    edited_data = st.data_editor(
        data_df,
        num_rows="dynamic",
        use_container_width=True,
        height=int(_record_h),
        key="data_editor",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width=COL_W_NO_TO_SCORE),
            "날짜": st.column_config.TextColumn("날짜", width=COL_W_NO_TO_SCORE),
            "선후공": st.column_config.SelectboxColumn("선후공", options=_select_options(["선", "후"]), width=COL_W_NO_TO_SCORE),
            "결과": st.column_config.SelectboxColumn("결과", options=_select_options(["승", "패"]), width=COL_W_NO_TO_SCORE),
            "세트": st.column_config.SelectboxColumn("세트", options=_select_options(["OO", "OXO", "XOO", "XX", "XOX", "OXX"]), width=COL_W_NO_TO_SCORE),
            "점수": st.column_config.TextColumn("점수", width=COL_W_NO_TO_SCORE),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=_select_options(st.session_state.options["내 덱"])),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=_select_options(st.session_state.options["상대 덱"])),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=_select_options(st.session_state.options["특정 카드"])),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=_select_options(st.session_state.options["승패 요인"])),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=_select_options(st.session_state.options["아키타입"])),
            "브릭": st.column_config.CheckboxColumn("브릭", default=False),
            "실수": st.column_config.CheckboxColumn("실수", default=False),
            "비고": st.column_config.TextColumn("비고"),
        }
    )
    st.session_state.last_edited_record_data = edited_data.copy()

    save_col, dl_col = st.columns([1, 1])
    with save_col:
        if st.button("💾 저장", type="primary", use_container_width=True):
            guide_to_save = _apply_guide_stats_from_records(_single_guide_row(edited_guide), edited_data)
            _persist_record_csv(guide_to_save, edited_data)
            st.success("저장했습니다.")
    _g_dl = _apply_guide_stats_from_records(_single_guide_row(edited_guide), edited_data)
    _merged_dl = pd.concat([_g_dl, edited_data], ignore_index=True)
    csv = _merged_dl.to_csv(index=False).encode("utf-8-sig")
    with dl_col:
        st.download_button("📥 CSV 다운로드", data=csv, file_name=FILENAME, mime="text/csv", use_container_width=True)

# ---------------------------------------------------------
# Setting
# ---------------------------------------------------------
with tab_setting:
    st.title("⚙️ Setting")
    col1, col2, col3 = st.columns(3)
    with col1:
        my_decks = st.text_area("내 덱 목록", value="\n".join(st.session_state.options["내 덱"]), height=200)
    with col2:
        opp_decks = st.text_area("상대 덱 목록", value="\n".join(st.session_state.options["상대 덱"]), height=200)
    with col3:
        specific_cards = st.text_area("특정 카드 목록", value="\n".join(st.session_state.options["특정 카드"]), height=200)
    
    col4, col5 = st.columns(2)
    with col4:
        win_loss_factors = st.text_area("승패 요인 목록", value="\n".join(st.session_state.options["승패 요인"]), height=150)
    with col5:
        archetypes = st.text_area("아키타입 목록", value="\n".join(st.session_state.options["아키타입"]), height=150)

    if st.button("✅ 설정 적용"):
        st.session_state.options["내 덱"] = [x.strip() for x in my_decks.split("\n") if x.strip()]
        st.session_state.options["상대 덱"] = [x.strip() for x in opp_decks.split("\n") if x.strip()]
        st.session_state.options["특정 카드"] = [x.strip() for x in specific_cards.split("\n") if x.strip()]
        st.session_state.options["승패 요인"] = [x.strip() for x in win_loss_factors.split("\n") if x.strip()]
        st.session_state.options["아키타입"] = [x.strip() for x in archetypes.split("\n") if x.strip()]
        st.success("설정이 적용되었습니다.")
