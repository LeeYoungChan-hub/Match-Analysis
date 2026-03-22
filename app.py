import hashlib
import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 표 스타일 설정
CELL_FONT_PX = "10px"
COL_W_STATUS = 25  # 요청하신 25픽셀로 설정
COL_W_NO = 40      # NO. 열도 함께 축소

def _compact_layout_css() -> None:
    st.markdown(
        f"""
        <style>
        .block-container {{ padding: 0.45rem 0.55rem !important; max-width: 100% !important; }}
        [data-testid="stDataFrame"] {{ margin-bottom: 0.15rem !important; font-size: {CELL_FONT_PX} !important; }}
        /* 셀 내부 여백 최소화하여 25px에서도 아이콘이 잘 보이게 조정 */
        [data-testid="stDataFrame"] [role="gridcell"] {{ 
            padding-left: 0px !important; 
            padding-right: 0px !important; 
            text-align: center !important; 
            justify-content: center !important; 
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

_compact_layout_css()

# 2. 데이터 및 설정값 초기화 (이모지만 남김)
FILENAME = "2026.03 레이팅 - Record.csv"
STATUS_OPTS = ["⚪", "🔵", "🟠"]

if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv(FILENAME)
        if "상태" not in st.session_state.df.columns:
            st.session_state.df.insert(1, "상태", "⚪")
        # 기존 데이터 타입 보정
        st.session_state.df['브릭'] = pd.to_numeric(st.session_state.df['브릭'], errors='coerce').fillna(0).astype(bool)
        st.session_state.df['실수'] = pd.to_numeric(st.session_state.df['실수'], errors='coerce').fillna(0).astype(bool)
    except:
        columns = ["NO.", "상태", "날짜", "선후공", "결과", "세트", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        st.session_state.df = pd.DataFrame([["0", "⚪", "Date", "0%", "0%", "Result", "0", "Deck", "Opp", "Arch", "Factor", "Card", 0, 0, "Detail"]], columns=columns)

# (중략: _brick_mistake_sums, _display_cell_str 등 로직 함수는 이전과 동일)

# 3. 메인 화면
tab_record, tab_setting = st.tabs(["📊 Record", "⚙️ Setting"])

with tab_record:
    st.title("📊 Rating Dashboard")
    
    # 가이드와 데이터 분리
    guide_df = st.session_state.df.iloc[[0]].copy()
    data_df = st.session_state.df.iloc[1:].copy()

    # 가이드 행은 텍스트로, 기록 행은 선택박스로 처리
    st.subheader("📋 가이드 및 통계")
    st.data_editor(
        guide_df, use_container_width=True, height=96, num_rows="fixed", hide_index=True,
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width=COL_W_NO),
            "상태": st.column_config.TextColumn(" ", width=COL_W_STATUS), # 헤더 이름 제거
            "브릭": st.column_config.NumberColumn("브릭", format="%d"),
            "실수": st.column_config.NumberColumn("실수", format="%d"),
        }
    )

    st.subheader("📝 경기 기록")
    edited_data = st.data_editor(
        data_df, num_rows="dynamic", use_container_width=True, height=500, key="data_editor",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width=COL_W_NO),
            "상태": st.column_config.SelectboxColumn(" ", options=STATUS_OPTS, width=COL_W_STATUS),
            "선후공": st.column_config.SelectboxColumn("선후공", options=["", "선", "후"], width=60),
            "결과": st.column_config.SelectboxColumn("결과", options=["", "승", "패"], width=60),
            "브릭": st.column_config.CheckboxColumn("브릭"),
            "실수": st.column_config.CheckboxColumn("실수"),
        }
    )

    if st.button("💾 저장", type="primary", use_container_width=True):
        # 저장 로직 (생략된 헬퍼 함수 활용하여 파일 쓰기)
        merged = pd.concat([guide_df, edited_data], ignore_index=True)
        st.session_state.df = merged
        merged.to_csv(FILENAME, index=False, encoding="utf-8-sig")
        st.success("25px 너비로 저장되었습니다.")
        st.rerun()
