import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

# 2. 데이터 및 설정값 초기화
FILENAME = "2026.03 레이팅 - Record.csv"

# 세션 상태: 경기 기록 데이터 초기화
if 'df' not in st.session_state:
    try:
        # 기존 파일 로드
        st.session_state.df = pd.read_csv(FILENAME)
    except:
        # 파일이 없을 경우 초기 가이드 행 생성
        columns = ["NO.", "날짜", "선후공", "결과", "세트 전적", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        sub_label_row = {
            "NO.": "경기", "날짜": "Date", "선후공": "40.46%", "결과": "62.43%", 
            "세트 전적": "Result", "점수": "Rate", "내 덱": "Use.deck", 
            "상대 덱": "Opp. deck", "아키타입": "Plus Arch.", "승패 요인": "W/L Factor",
            "특정 카드": "Certain Card", "브릭": "10", "실수": "30", "비고": "Deatil"
        }
        st.session_state.df = pd.DataFrame([sub_label_row], columns=columns)

# 세션 상태: Setting 드롭다운 옵션 초기화
if 'options' not in st.session_state:
    st.session_state.options = {
        "내 덱": ["KT", "SwoS", "Synchron"],
        "상대 덱": ["Mitsu", "Ennea", "DD", "Red Dra", "Branded", "Maliss"],
        "특정 카드": ["TT Talent", "Droll", "Nibiru"],
        "승패 요인": ["자신 실력", "상대 패", "특정 카드", "운"],
        "아키타입": ["60", "Arch"]
    }

# 3. 상단 탭 구성 (스프레드시트 시트 스타일)
tab1, tab2 = st.tabs(["📊 Record", "⚙️ Setting"])

# ---------------------------------------------------------
# TAB 1: Record 페이지
# ---------------------------------------------------------
with tab1:
    st.title("📊 Rating Dashboard")

    # 데이터 분리 (1행 가이드 / 나머지 데이터)
    guide_df = st.session_state.df.iloc[[0]]
    data_df = st.session_state.df.iloc[1:]

    # 가이드 행 에디터
    st.subheader("📋 가이드 및 통계 (수정 가능)")
    edited_guide = st.data_editor(guide_df, use_container_width=True, key="guide_editor")

    # 실제 데이터 에디터 (Setting의 옵션 반영)
    st.subheader("📝 경기 기록")
    edited_data = st.data_editor(
        data_df,
        num_rows="dynamic",
        use_container_width=True,
        key="data_editor",
        column_config={
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"]),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"]),
            "세트 전적": st.column_config.SelectboxColumn("세트 전적", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"]),
            # Setting 탭에서 설정한 리스트를 드롭다운으로 연결
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.options["내 덱"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.options["상대 덱"]),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.options["특정 카드"]),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.options["승패 요인"]),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.options["아키타입"]),
        }
    )

    # 데이터 합치기 및 저장 버튼
    col_save, col_down = st.columns([1, 4])
    with col_save:
        if st.button("💾 데이터 저장"):
            # 가이드 행과 데이터를 다시 합쳐서 세션에 저장
            st.session_state.df = pd.concat([edited_guide, edited_data], ignore_index=True)
            st.success("변경사항이 저장되었습니다.")
    
    with col_down:
        csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name=FILENAME,
            mime='text/csv',
        )

# ---------------------------------------------------------
# TAB 2: Setting 페이지
# ---------------------------------------------------------
with tab2:
    st.title("⚙️ Setting")
    st.write("Record 페이지 드롭다운에 표시될 항목들을 관리합니다.")
    st.info("각 항목에 대해 한 줄에 하나씩 입력해 주세요.")

    col1, col2, col3 = st.columns(3)
    with col1:
        my_decks = st.text_area("내 덱 목록", value="\n".join(st.session_state.options["내 덱"]), height=250)
    with col2:
        opp_decks = st.text_area("상대 덱 목록", value="\n".join(st.session_state.options["상대 덱"]), height=250)
    with col3:
        specific_cards = st.text_area("특정 카드 목록", value="\n".join(st.session_state.options["특정 카드"]), height=250)
    
    col4, col5 = st.columns(2)
    with col4:
        win_loss_factors = st.text_area("승패 요인 목록", value="\n".join(st.session_state.options["승패 요인"]), height=150)
    with col5:
        archetypes = st.text_area("아키타입 목록", value="\n".join(st.session_state.options["아키타입"]), height=150)

    if st.button("✅ 설정 적용"):
        # 입력된 텍스트를 줄바꿈 기준으로 리스트화
        st.session_state.options["내 덱"] = [x.strip() for x in my_decks.split("\n") if x.strip()]
        st.session_state.options["상대 덱"] = [x.strip() for x in opp_decks.split("\n") if x.strip()]
        st.session_state.options["특정 카드"] = [x.strip() for x in specific_cards.split("\n") if x.strip()]
        st.session_state.options["승패 요인"] = [x.strip() for x in win_loss_factors.split("\n") if x.strip()]
        st.session_state.options["아키타입"] = [x.strip() for x in archetypes.split("\n") if x.strip()]
        st.success("설정이 적용되었습니다. Record 탭에서 확인하세요!")
