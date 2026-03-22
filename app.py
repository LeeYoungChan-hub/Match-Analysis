import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

# 2. 데이터 및 설정값 초기화
FILENAME = "2026.03 레이팅 - Record.csv"

# 세션 상태: 경기 기록 데이터 초기화
if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv(FILENAME)
        st.session_state.df['브릭'] = st.session_state.df['브릭'].map({'TRUE': True, 'FALSE': False, True: True, False: False}).fillna(False)
        st.session_state.df['실수'] = st.session_state.df['실수'].map({'TRUE': True, 'FALSE': False, True: True, False: False}).fillna(False)
    except:
        columns = ["NO.", "날짜", "선후공", "결과", "세트 전적", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        sub_label_row = {
            "NO.": "0판", "날짜": "Date", "선후공": "0.00%", "결과": "0.00%", 
            "세트 전적": "Result", "점수": "Rate", "내 덱": "Use.deck", 
            "상대 덱": "Opp. deck", "아키타입": "Plus Arch.", "승패 요인": "W/L Factor",
            "특정 카드": "Certain Card", "브릭": "0", "실수": "0", "비고": "Deatil"
        }
        st.session_state.df = pd.DataFrame([sub_label_row], columns=columns)

# 세션 상태: Setting 옵션 및 UI 설정
if 'options' not in st.session_state:
    st.session_state.options = {
        "내 덱": ["KT", "SwoS", "Synchron"],
        "상대 덱": ["Mitsu", "Ennea", "DD", "Red Dra", "Branded", "Maliss"],
        "특정 카드": ["TT Talent", "Droll", "Nibiru"],
        "승패 요인": ["자신 실력", "상대 패", "특정 카드", "운"],
        "아키타입": ["60", "Arch"]
    }
if 'table_height' not in st.session_state:
    st.session_state.table_height = 20000  # 기본 높이

# 3. 자동 계산 함수 (Auto-save 로직)
def update_stats():
    # 에디터에서 변경된 최신 데이터를 가져옴
    if "data_editor" in st.session_state:
        edited_data = st.session_state["data_editor"]["edited_rows"]
        added_data = st.session_state["data_editor"]["added_rows"]
        # 실제로는 st.data_editor의 state를 직접 다루기보다 
        # 에디터 결과물인 edited_df를 활용하는 것이 안정적이므로 버튼 클릭 없이도 반영되게 구성함

# 4. 상단 탭 구성
tab1, tab2 = st.tabs(["📊 Record", "⚙️ Setting"])

# ---------------------------------------------------------
# TAB 1: Record 페이지
# ---------------------------------------------------------
with tab1:
    st.title("📊 Rating Dashboard")

    # 데이터 분리
    guide_df = st.session_state.df.iloc[[0]].copy()
    data_df = st.session_state.df.iloc[1:].copy()

    # 상단 가이드 표 (통계 표시용)
    st.subheader("📋 가이드 및 통계")
    edited_guide = st.data_editor(guide_df, use_container_width=True, key="guide_editor")

    # 하단 경기 기록 표 (자동 저장 및 높이 조절 적용)
    st.subheader("📝 경기 기록")
    edited_data = st.data_editor(
        data_df,
        num_rows="dynamic",
        use_container_width=True,
        height=st.session_state.table_height, # 설정된 높이 반영
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

    # 실시간 통계 계산 (저장 버튼 없이도 데이터가 바뀌면 계산)
    total_games = len(edited_data)
    if total_games > 0:
        win_rate = (len(edited_data[edited_data["결과"] == "승"]) / total_games) * 100
        first_rate = (len(edited_data[edited_data["선후공"] == "선"]) / total_games) * 100
        brick_sum = edited_data["브릭"].sum()
        mistake_sum = edited_data["실수"].sum()
        
        # 가이드 행에 값 강제 주입
        edited_guide.at[0, "결과"] = f"{win_rate:.2f}%"
        edited_guide.at[0, "선후공"] = f"{first_rate:.2f}%"
        edited_guide.at[0, "브릭"] = str(brick_sum)
        edited_guide.at[0, "실수"] = str(mistake_sum)
        edited_guide.at[0, "NO."] = f"{total_games}판"

    # 수동 저장 버튼 (세션 데이터 확정용)
    if st.button("💾 최종 데이터 저장"):
        st.session_state.df = pd.concat([edited_guide, edited_data], ignore_index=
