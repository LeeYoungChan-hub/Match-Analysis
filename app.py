import streamlit as st
import pandas as pd
# 1. 페이지 설정
st.set_page_config(page_title="Rating Dashboard", layout="wide")
# 2. 데이터 및 설정값 초기화
FILENAME = "2026.03 레이팅 - Record.csv"
if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv(FILENAME)
        # 데이터 로드 시 체크박스 열을 불리언 타입으로 확실히 변환
        st.session_state.df['브릭'] = pd.to_numeric(st.session_state.df['브릭'], errors='coerce').fillna(0).astype(bool)
        st.session_state.df['실수'] = pd.to_numeric(st.session_state.df['실수'], errors='coerce').fillna(0).astype(bool)
    except:
        columns = ["NO.", "날짜", "선후공", "결과", "세트 전적", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        sub_label_row = {
            "NO.": "0", "날짜": "Date", "선후공": "0.00%", "결과": "0.00%", 
            "세트 전적": "Result", "점수": "0", "내 덱": "Use.deck", 
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
# 3. 상단 탭 구성
tab1, tab2 = st.tabs(["📊 Record", "⚙️ Setting"])
# ---------------------------------------------------------
# TAB 1: Record 페이지
# ---------------------------------------------------------
with tab1:
    st.title("📊 Rating Dashboard")
    # 1행(가이드)과 나머지(데이터) 분리
    guide_df = st.session_state.df.iloc[[0]].copy()
    data_df = st.session_state.df.iloc[1:].copy()
    # 가이드가 위에 있어 같은 실행에서 편집 중인 표를 쓸 수 없음 → 직전 실행의 편집본 사용
    stats_src = st.session_state.get("last_edited_record_data", data_df)
    _sync_guide_stats_row(guide_df, stats_src)
    st.subheader("📋 가이드 및 통계")
    # 가이드 행은 체크박스가 아닌 일반 텍스트로 표시되도록 설정
    edited_guide = st.data_editor(
        guide_df,
        use_container_width=True,
        key="guide_editor",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", disabled=True),
            "점수": st.column_config.TextColumn("점수", disabled=True),
            "브릭": st.column_config.NumberColumn("브릭", format="%d", disabled=True),
            "실수": st.column_config.NumberColumn("실수", format="%d", disabled=True),
        },
    )
    st.subheader("📝 경기 기록")
    edited_data = st.data_editor(
        data_df,
        num_rows="dynamic",
        use_container_width=True,
        key="data_editor",
        column_config={
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"]),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"]),
            "세트 전적": st.column_config.SelectboxColumn("세트 전적", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"]),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.options["내 덱"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.options["상대 덱"]),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.options["특정 카드"]),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.options["승패 요인"]),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.options["아키타입"]),
            "브릭": st.column_config.CheckboxColumn("브릭", default=False),
            "실수": st.column_config.CheckboxColumn("실수", default=False),
        }
    )
    st.session_state.last_edited_record_data = edited_data.copy()
    if st.button("💾 데이터 저장"):
        if len(edited_data) > 0:
            # --- 계산 로직 ---
            total_games = len(edited_data)
            win_count = len(edited_data[edited_data["결과"] == "승"])
            first_count = len(edited_data[edited_data["선후공"] == "선"])
            brick_count, mistake_count = _brick_mistake_sums(edited_data)
            last_no = edited_data.iloc[-1]["NO."]
            last_score = edited_data.iloc[-1]["점수"]
            # --- 가이드 행(edited_guide) 업데이트 ---
            edited_guide.iloc[0, edited_guide.columns.get_loc("NO.")] = _display_cell_str(last_no)
            edited_guide.iloc[0, edited_guide.columns.get_loc("점수")] = _display_cell_str(last_score)
            edited_guide.iloc[0, edited_guide.columns.get_loc("결과")] = f"{(win_count/total_games)*100:.2f}%"
            edited_guide.iloc[0, edited_guide.columns.get_loc("선후공")] = f"{(first_count/total_games)*100:.2f}%"
            edited_guide.iloc[0, edited_guide.columns.get_loc("브릭")] = int(brick_count)
            edited_guide.iloc[0, edited_guide.columns.get_loc("실수")] = int(mistake_count)
        # 데이터 합치기
        st.session_state.df = pd.concat([edited_guide, edited_data], ignore_index=True)
        
        # 파일 저장
        st.session_state.df.to_csv(FILENAME, index=False, encoding='utf-8-sig')
        st.success("데이터 및 통계 합계가 저장되었습니다!")
        st.rerun()
    csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 CSV 다운로드", data=csv, file_name=FILENAME, mime='text/csv')
# ---------------------------------------------------------
# TAB 2: Setting 페이지 (기존과 동일)
# ---------------------------------------------------------
with tab2:
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
