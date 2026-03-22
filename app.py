import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

# 2. 스크린샷 스타일 재현을 위한 CSS (서브 라벨 스타일 포함)
st.markdown("""
    <style>
    .metric-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #eeeeee;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 10px;
    }
    .main-label {
        font-size: 26px;
        font-weight: bold;
        color: #333;
        margin-bottom: 0px;
    }
    .sub-label {
        font-size: 14px;
        color: #888; /* 회색 서브 라벨 */
        margin-top: -5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Rating Dashboard")

# 3. 상단 요약 섹션 (사진과 똑같은 서브 라벨 추가)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('''
        <div class="metric-container">
            <p class="main-label">62.43%</p>
            <p class="sub-label">Result</p>
        </div>
    ''', unsafe_allow_html=True)
with col2:
    st.markdown('''
        <div class="metric-container">
            <p class="main-label">40.46%</p>
            <p class="sub-label">First</p>
        </div>
    ''', unsafe_allow_html=True)
with col3:
    st.markdown('''
        <div class="metric-container">
            <p class="main-label">71.21%</p>
            <p class="sub-label">Second</p>
        </div>
    ''', unsafe_allow_html=True)
with col4:
    st.markdown('''
        <div class="metric-container">
            <p class="main-label">124</p>
            <p class="sub-label">Games</p>
        </div>
    ''', unsafe_allow_html=True)

st.divider()

# 4. 하단 데이터 표 (기존 구조 유지)
st.subheader("📝 경기 기록 데이터")

# 초기 컬럼 설정
columns = [
    "NO.", "날짜", "선후공", "결과", "세트 전적", "점수", 
    "내 덱", "상대 덱", "아키타입", "승패 요인", 
    "특정 카드", "브릭", "실수", "비고"
]

# CSV 파일이 있다면 불러오고, 없다면 샘플 데이터 생성
if 'df' not in st.session_state:
    try:
        # 파일이 있는 경우 불러오기
        st.session_state.df = pd.read_csv("2026.03 레이팅 - Record.csv")
    except:
        # 파일이 없는 경우 빈 틀 생성
        st.session_state.df = pd.DataFrame(columns=columns)

# 데이터 에디터 출력
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "브릭": st.column_config.CheckboxColumn("브릭"),
        "실수": st.column_config.CheckboxColumn("실수"),
        "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"]),
        "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"])
    }
)

# 저장 및 다운로드 버튼
if st.button("💾 변경사항 저장"):
    st.session_state.df = edited_df
    st.success("데이터가 로컬 세션에 저장되었습니다.")

csv = edited_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 CSV 다운로드 (GitHub 업데이트용)",
    data=csv,
    file_name="2026.03 레이팅 - Record.csv",
    mime='text/csv',
)
