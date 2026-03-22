import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

# CSS를 활용해 스크린샷의 카드 스타일 재현
st.markdown("""
    <style>
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #636EFA;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-label { font-size: 14px; color: #666; }
    .metric-value { font-size: 24px; font-weight: bold; color: #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Rating Dashboard")

# 1. 상단 요약 섹션 (스크린샷의 4칸 구성)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card"><p class="metric-label">전체 승률</p><p class="metric-value">62.4%</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><p class="metric-label">선공 승률</p><p class="metric-value">40.5%</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><p class="metric-label">후공 승률</p><p class="metric-value">71.2%</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><p class="metric-label">총 경기 수</p><p class="metric-value">124회</p></div>', unsafe_allow_html=True)

st.write("") # 간격 조절
st.divider()

# 2. 데이터 관리 섹션 (스크린샷 하단의 표 구조)
st.subheader("📝 경기 기록 데이터")

# 초기 데이터 (스크린샷의 컬럼 구조 그대로)
if 'df' not in st.session_state:
    columns = [
        "NO.", "날짜", "선후공", "결과", "세트 전적", "점수", 
        "내 덱", "상대 덱", "아키타입", "승패 요인", 
        "특정 카드", "브릭", "실수", "비고"
    ]
    # 샘플 데이터 1줄 추가
    st.session_state.df = pd.DataFrame([
        {
            "NO.": "1", "날짜": "03.22", "선후공": "선", "결과": "승", 
            "세트 전적": "OO", "점수": "1500", "내 덱": "KT", 
            "상대 덱": "Mitsu", "아키타입": "Arch", "승패 요인": "자신 실력",
            "특정 카드": "", "브릭": False, "실수": False, "비고": ""
        }
    ], columns=columns)

# 스크린샷의 표 형식처럼 직접 수정 가능한 에디터
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic", # 행 추가/삭제 가능
    use_container_width=True,
    column_config={
        "브릭": st.column_config.CheckboxColumn("브릭", default=False),
        "실수": st.column_config.CheckboxColumn("실수", default=False),
        "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"]),
        "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"])
    }
)

# 3. 데이터 저장 기능
col_save1, col_save2 = st.columns([1, 5])
with col_save1:
    if st.button("💾 변경사항 저장"):
        st.session_state.df = edited_df
        st.success("저장되었습니다!")

with col_save2:
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 CSV 다운로드 (GitHub 업로드용)",
        data=csv,
        file_name="2026.03 레이팅 - Record.csv",
        mime='text/csv',
    )
