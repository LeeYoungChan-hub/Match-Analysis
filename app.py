import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

st.title("📊 Rating Dashboard")

# 2. 데이터 초기화 (사진의 구조와 서브 라벨 행 구현)
FILENAME = "2026.03 레이팅 - Record.csv"

if 'df' not in st.session_state:
    try:
        # 기존 파일 로드 시도
        df = pd.read_csv(FILENAME)
        st.session_state.df = df
    except:
        # 파일이 없을 경우 사진과 똑같은 구조로 생성
        columns = [
            "NO.", "날짜", "선후공", "결과", "세트 전적", "점수", 
            "내 덱", "상대 덱", "아키타입", "승패 요인", 
            "특정 카드", "브릭", "실수", "비고", "Deatil"
        ]
        
        # 사진의 1행(서브 라벨 행) 데이터 구성
        sub_label_row = {
            "NO.": "경기", "날짜": "Date", "선후공": "40.46%", "결과": "62.43%", 
            "세트 전적": "Result", "점수": "Rate", "내 덱": "Use.deck", 
            "상대 덱": "Opp. deck", "아키타입": "Plus Arch.", "승패 요인": "W/L Factor",
            "특정 카드": "Certain Card", "브릭": "10", "실수": "30", "비고": "", "Deatil": ""
        }
        
        # 데이터프레임 생성 및 서브 라벨 행 삽입
        st.session_state.df = pd.DataFrame([sub_label_row], columns=columns)

# 3. 데이터 에디터 설정
st.subheader("📝 경기 기록부")

# 에디터에서 첫 번째 행(라벨 행)은 가급적 수정하지 않도록 안내
st.info("💡 첫 번째 행은 서브 라벨(가이드) 행입니다. 데이터는 두 번째 행부터 입력하세요.")

edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    # 브릭과 실수는 체크박스로 만들지 않음 (첫 행에 '10', '30' 글자가 들어가야 하므로 일반 텍스트 열 유지)
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

# 4. 저장 및 다운로드 기능
col_save, col_down = st.columns([1, 4])

with col_save:
    if st.button("💾 변경사항 저장"):
        st.session_state.df = edited_df
        st.success("세션에 저장되었습니다.")

with col_down:
    # 엑셀/CSV로 내보낼 때 서브 라벨 행을 포함하여 저장
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 CSV 다운로드 (GitHub 업로드용)",
        data=csv,
        file_name=FILENAME,
        mime='text/csv',
    )

st.divider()
st.caption("GitHub 저장소의 파일과 일치시키려면 다운로드한 CSV를 업로드해 주세요.")
