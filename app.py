import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

st.title("📊 Rating Dashboard")

# 2. 데이터 초기화
FILENAME = "2026.03 레이팅 - Record.csv"

if 'df' not in st.session_state:
    try:
        df = pd.read_csv(FILENAME)
        st.session_state.df = df
    except:
        columns = ["NO.", "날짜", "선후공", "결과", "세트 전적", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        # 사진과 동일한 가이드 행 생성
        sub_label_row = {
            "NO.": "경기", "날짜": "Date", "선후공": "40.46%", "결과": "62.43%", 
            "세트 전적": "Result", "점수": "Rate", "내 덱": "Use.deck", 
            "상대 덱": "Opp. deck", "아키타입": "Plus Arch.", "승패 요인": "W/L Factor",
            "특정 카드": "Certain Card", "브릭": "10", "실수": "30", "비고": "Deatil"
        }
        st.session_state.df = pd.DataFrame([sub_label_row], columns=columns)

# 3. 데이터 분리 (가이드 행과 실제 데이터 행)
# 첫 번째 행은 가이드용으로 따로 보관
guide_df = st.session_state.df.iloc[[0]]
# 두 번째 행부터는 실제 데이터
data_df = st.session_state.df.iloc[1:]

# 4. 화면 구성
st.subheader("📋 가이드 및 통계 (수정 가능)")
# 가이드 행만 보여주는 에디터 (드롭다운 없이 자유 입력)
edited_guide = st.data_editor(guide_df, use_container_width=True, key="guide_editor")

st.subheader("📝 경기 기록")
# 실제 데이터 에디터 (여기서만 드롭다운 적용, 가이드 값은 제외)
edited_data = st.data_editor(
    data_df,
    num_rows="dynamic",
    use_container_width=True,
    key="data_editor",
    column_config={
        "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"]),
        "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"]),
        "세트 전적": st.column_config.SelectboxColumn("세트 전적", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"])
    }
)

# 5. 데이터 합치기 및 저장
if st.button("💾 데이터 저장"):
    # 가이드 행과 수정된 데이터를 다시 합침
    st.session_state.df = pd.concat([edited_guide, edited_data], ignore_index=True)
    st.success("변경사항이 저장되었습니다.")

# 6. 다운로드 기능
csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 CSV 다운로드",
    data=csv,
    file_name=FILENAME,
    mime='text/csv',
)
