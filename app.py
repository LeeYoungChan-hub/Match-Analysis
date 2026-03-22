import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

st.title("📊 Rating Dashboard")

# 2. 데이터 초기화 및 서브 라벨 행 설정
FILENAME = "2026.03 레이팅 - Record.csv"

if 'df' not in st.session_state:
    try:
        # 기존 파일이 있으면 로드
        st.session_state.df = pd.read_csv(FILENAME)
    except:
        # 파일이 없을 경우 사진 구조 그대로 생성 (1행은 서브 라벨)
        columns = [
            "NO.", "날짜", "선후공", "결과", "세트 전적", "점수", 
            "내 덱", "상대 덱", "아키타입", "승패 요인", 
            "특정 카드", "브릭", "실수", "비고", "Deatil"
        ]
        
        # 사진과 동일한 서브 라벨 행 구성
        # 선후공 -> 선공확률(40.46%), 결과 -> 승률(62.43%) 적용
        sub_label_row = {
            "NO.": "경기", 
            "날짜": "Date", 
            "선후공": "40.46%", # 선공 확률
            "결과": "62.43%",   # 전체 승률
            "세트 전적": "Result", 
            "점수": "Rate", 
            "내 덱": "Use.deck", 
            "상대 덱": "Opp. deck", 
            "아키타입": "Plus Arch.", 
            "승패 요인": "W/L Factor",
            "특정 카드": "Certain Card", 
            "브릭": "10", 
            "실수": "30", 
            "비고": "", 
            "Deatil": ""
        }
        st.session_state.df = pd.DataFrame([sub_label_row], columns=columns)

# 3. 데이터 에디터 설정
st.subheader("📝 경기 기록부")
st.info("💡 첫 번째 행은 가이드(확률/라벨) 행입니다. 수치 수정이 필요하면 첫 행을 수정하세요.")

# 에디터 호출
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    # 첫 행에 텍스트(확률 등)를 넣어야 하므로 모든 열을 일반 텍스트 모드로 유지
    column_config={
        "NO.": st.column_config.Column("NO."),
        "날짜": st.column_config.Column("날짜"),
        "선후공": st.column_config.Column("선후공"),
        "결과": st.column_config.Column("결과"),
        "세트 전적": st.column_config.Column("세트 전적"),
        "점수": st.column_config.Column("점수"),
        "내 덱": st.column_config.Column("내 덱"),
        "상대 덱": st.column_config.Column("상대 덱"),
        "아키타입": st.column_config.Column("아키타입"),
        "승패 요인": st.column_config.Column("승패 요인"),
        "특정 카드": st.column_config.Column("특정 카드"),
        "브릭": st.column_config.Column("브릭"),
        "실수": st.column_config.Column("실수"),
    }
)

# 4. 관리 기능
col_save, col_down = st.columns([1, 4])

with col_save:
    if st.button("💾 데이터 저장"):
        st.session_state.df = edited_df
        st.success("변경사항이 세션에 저장되었습니다.")

with col_down:
    # 한글 깨짐 방지를 위해 utf-8-sig 사용
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv,
        file_name=FILENAME,
        mime='text/csv',
    )
