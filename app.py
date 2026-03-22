import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

st.title("🗂️ Rating 경기 기록부")

# 2. 파일 로드 로직
# GitHub에 처음 올릴 때 파일이 없으면 빈 양식을 만듭니다.
FILENAME = "2026.03 레이팅 - Record.csv"

def load_data():
    try:
        df = pd.read_csv(FILENAME)
    except FileNotFoundError:
        # 파일이 없을 경우 업로드하신 파일의 컬럼 구조 그대로 생성
        columns = [
            "NO.", "날짜", "선후공", "결과", "세트 전적", "점수", 
            "내 덱", "상대 덱", "아키타입", "승패 요인", 
            "특정 카드", "브릭", "실수", "비고", "Deatil"
        ]
        df = pd.DataFrame(columns=columns)
        # 헤더 아래의 보조 설명 행(영어) 추가
        description_row = {
            "NO.": "경기", "날짜": "Date", "선후공": "40.46%", "결과": "62.43%", 
            "세트 전적": "Result", "점수": "Rate", "내 덱": "Use.deck", 
            "상대 덱": "Opp. deck", "아키타입": "Plus Arch.", "승패 요인": "W/L Factor",
            "특정 카드": "Certain Card", "브릭": "10", "실수": "30"
        }
        df = pd.concat([df, pd.DataFrame([description_row])], ignore_index=True)
    return df

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# 3. 데이터 입력 UI (새 경기 추가)
with st.expander("➕ 새 경기 기록 추가"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        new_no = st.text_input("NO.", value=str(len(st.session_state.df)))
        new_date = st.text_input("날짜", placeholder="MM.DD")
    with col2:
        new_turn = st.selectbox("선후공", ["선", "후"])
        new_res = st.selectbox("결과", ["승", "패"])
    with col3:
        new_set = st.text_input("세트 전적", placeholder="OO / XOO")
        new_my = st.text_input("내 덱", value="KT")
    with col4:
        new_opp = st.text_input("상대 덱")
        new_mistake = st.checkbox("실수 여부")

    if st.button("기록 저장"):
        new_data = {
            "NO.": new_no, "날짜": new_date, "선후공": new_turn, "결과": new_res,
            "세트 전적": new_set, "내 덱": new_my, "상대 덱": new_opp, 
            "실수": "TRUE" if new_mistake else "FALSE"
        }
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_data])], ignore_index=True)
        st.success("데이터가 추가되었습니다!")

# 4. 표 형식으로 보여주기 (수정 가능)
st.subheader("📝 전체 기록 (수정 가능)")
# data_editor를 사용하면 엑셀처럼 화면에서 직접 수정이 가능합니다.
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

# 5. 파일 저장 버튼
if st.button("💾 변경사항 CSV로 내보내기"):
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="CSV 다운로드",
        data=csv,
        file_name=FILENAME,
        mime='text/csv',
    )
    st.info("다운로드한 파일을 GitHub 저장소에 덮어쓰기하면 데이터가 유지됩니다.")

# 6. 간단 요약 (형식 유지를 위해 하단 배치)
st.divider()
st.caption("현재 저장된 총 경기 수: " + str(len(st.session_state.df) - 1) + "판")
