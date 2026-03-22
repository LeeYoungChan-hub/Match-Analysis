import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

# 2. 데이터 로드 및 초기화
FILENAME = "2026.03 레이팅 - Record.csv"

if 'df' not in st.session_state:
    try:
        # 기존 파일 로드
        df = pd.read_csv(FILENAME)
        st.session_state.df = df
    except:
        # 파일이 없을 경우 사진 구조 그대로 생성
        columns = [
            "NO.", "날짜", "선후공", "결과", "세트 전적", "점수", 
            "내 덱", "상대 deck", "아키타입", "승패 요인", 
            "특정 카드", "브릭", "실수", "비고"
        ]
        # 1행 가이드 데이터
        sub_label_row = {
            "NO.": "경기", "날짜": "Date", "선후공": "40.46%", "결과": "62.43%", 
            "세트 전적": "Result", "점수": "Rate", "내 덱": "Use.deck", 
            "상대 deck": "Opp. deck", "아키타입": "Plus Arch.", "승패 요인": "W/L Factor",
            "특정 카드": "Certain Card", "브릭": "10", "실수": "30", "비고": "Deatil"
        }
        st.session_state.df = pd.DataFrame([sub_label_row], columns=columns)

# 3. 데이터 에디터 (하나의 표로 통합 및 드롭다운 설정)
# '경기 기록' 문구 삭제됨
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "선후공": st.column_config.SelectboxColumn(
            "선후공",
            options=["선", "후"] # 드롭다운에 확률(40.46%)은 제외하고 선, 후만 표시
        ),
        "결과": st.column_config.SelectboxColumn(
            "결과",
            options=["승", "패"] # 드롭다운에 승률(62.43%)은 제외하고 승, 패만 표시
        ),
        "세트 전적": st.column_config.SelectboxColumn(
            "세트 전적",
            options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"] # Result 제외
        )
    }
)

# 4. 저장 및 다운로드 버튼
col_save, col_down = st.columns([1, 4])

with col_save:
    if st.button("💾 저장"):
        st.session_state.df = edited_df
        st.success("저장되었습니다.")

with col_down:
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv,
        file_name=FILENAME,
        mime='text/csv',
    )

st.info("💡 첫 번째 행은 가이드라인(통계/라벨)입니다. 두 번째 행부터 데이터를 입력하세요.")
