import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

st.title("📊 Rating Dashboard")

# 2. 데이터 로드 및 컬럼 설정
# 사진과 동일하게 메인 라벨(한글) 밑에 서브 라벨(영어)이 오는 구조로 설정
column_mapping = {
    "NO.": "NO.\n(경기)",
    "날짜": "날짜\n(Date)",
    "선후공": "선후공\n(40.46%)",
    "결과": "결과\n(62.43%)",
    "세트 전적": "세트 전적\n(Result)",
    "점수": "점수\n(Rate)",
    "내 덱": "내 덱\n(Use.deck)",
    "상대 덱": "상대 덱\n(Opp. deck)",
    "아키타입": "아키타입\n(Plus Arch.)",
    "승패 요인": "승패 요인\n(W/L Factor)",
    "특정 카드": "특정 카드\n(Certain Card)",
    "브릭": "브릭\n(10)",
    "실수": "실수\n(30)",
    "비고": "비고",
    "Deatil": "Deatil"
}

# 초기 데이터 구성
if 'df' not in st.session_state:
    try:
        # 기존 파일이 있으면 불러오기
        raw_df = pd.read_csv("2026.03 레이팅 - Record.csv")
        # 첫 번째 행이 영어 라벨인 경우 제외하고 로드
        if not raw_df.empty and raw_df.iloc[0]['NO.'] == '경기':
            st.session_state.df = raw_df.iloc[1:].reset_index(drop=True)
        else:
            st.session_state.df = raw_df
    except:
        # 파일이 없으면 빈 데이터프레임 생성
        st.session_state.df = pd.DataFrame(columns=column_mapping.keys())

# 3. 데이터 에디터 (표 형식)
# 서브 라벨을 column_config의 label로 적용
st.subheader("📝 경기 기록")

edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "NO.": st.column_config.Column("NO.\n(경기)"),
        "날짜": st.column_config.Column("날짜\n(Date)"),
        "선후공": st.column_config.Column("선후공\n(40.46%)"),
        "결과": st.column_config.Column("결과\n(62.43%)"),
        "세트 전적": st.column_config.Column("세트 전적\n(Result)"),
        "점수": st.column_config.Column("점수\n(Rate)"),
        "내 덱": st.column_config.Column("내 덱\n(Use.deck)"),
        "상대 덱": st.column_config.Column("상대 덱\n(Opp. deck)"),
        "아키타입": st.column_config.Column("아키타입\n(Plus Arch.)"),
        "승패 요인": st.column_config.Column("승패 요인\n(W/L Factor)"),
        "특정 카드": st.column_config.Column("특정 카드\n(Certain Card)"),
        "브릭": st.column_config.CheckboxColumn("브릭\n(10)"),
        "실수": st.column_config.CheckboxColumn("실수\n(30)"),
    }
)

# 4. 저장 및 관리
col_save, col_down = st.columns([1, 4])
with col_save:
    if st.button("💾 데이터 저장"):
        st.session_state.df = edited_df
        st.success("저장 완료!")

with col_down:
    # 깃허브 업로드용 CSV 생성 (원래의 깔끔한 컬럼명으로 저장)
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv,
        file_name="2026.03 레이팅 - Record.csv",
        mime='text/csv',
    )
