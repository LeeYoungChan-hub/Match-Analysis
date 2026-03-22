import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

st.title("📊 Rating Dashboard")

# 2. 데이터 초기화 및 서브 라벨 행 설정
FILENAME = "2026.03 레이팅 - Record.csv"

if 'df' not in st.session_state:
    try:
        # 기존 파일 로드
        df = pd.read_csv(FILENAME)
        st.session_state.df = df
    except:
        # 파일이 없을 경우 사진 구조 그대로 생성 (Deatil 컬럼 삭제)
        columns = [
            "NO.", "날짜", "선후공", "결과", "세트 전적", "점수", 
            "내 덱", "상대 덱", "아키타입", "승패 요인", 
            "특정 카드", "브릭", "실수", "비고"
        ]
        
        # 1행: 비고 아래에 Deatil이 오도록 설정
        sub_label_row = {
            "NO.": "경기", 
            "날짜": "Date", 
            "선후공": "40.46%", 
            "결과": "62.43%", 
            "세트 전적": "Result", 
            "점수": "Rate", 
            "내 덱": "Use.deck", 
            "상대 덱": "Opp. deck", 
            "아키타입": "Plus Arch.", 
            "승패 요인": "W/L Factor",
            "특정 카드": "Certain Card", 
            "브릭": "10", 
            "실수": "30", 
            "비고": "Deatil" # 비고 컬럼의 첫 행 값을 Deatil로 설정
        }
        st.session_state.df = pd.DataFrame([sub_label_row], columns=columns)

# 3. 데이터 에디터 설정
st.subheader("📝 경기 기록부")

edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "선후공": st.column_config.SelectboxColumn(
            "선후공",
            options=["40.46%", "선", "후"]
        ),
        "결과": st.column_config.SelectboxColumn(
            "결과",
            options=["62.43%", "승", "패"]
        ),
        "세트 전적": st.column_config.SelectboxColumn(
            "세트 전적",
            options=["Result", "OO", "OXO", "XOO", "XX", "XOX", "OXX"]
        ),
        # 비고 컬럼 설정
        "비고": st.column_config.Column("비고")
    }
)

# 4. 저장 및 관리
col_save, col_down = st.columns([1, 4])

with col_save:
    if st.button("💾 데이터 저장"):
        st.session_state.df = edited_df
        st.success("변경사항이 저장되었습니다.")

with col_down:
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv,
        file_name=FILENAME,
        mime='text/csv',
    )

st.info("💡 첫 번째 행은 가이드라인입니다. '비고' 열의 첫 행에 'Deatil'이 표시됩니다.")
