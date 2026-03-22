import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="Rating", layout="wide")

# 2. 데이터 및 설정값 초기화
FILENAME = "2026.03 레이팅 - Record.csv"

if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv(FILENAME)
        # 브릭, 실수 컬럼을 불리언(True/False) 타입으로 변환 (체크박스 호환)
        st.session_state.df['브릭'] = st.session_state.df['브릭'].map({'TRUE': True, 'FALSE': False, True: True, False: False}).fillna(False)
        st.session_state.df['실수'] = st.session_state.df['실수'].map({'TRUE': True, 'FALSE': False, True: True, False: False}).fillna(False)
    except:
        columns = ["NO.", "날짜", "선후공", "결과", "세트 전적", "점수", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
        sub_label_row = {
            "NO.": "경기", "날짜": "Date", "선후공": "40.46%", "결과": "62.43%", 
            "세트 전적": "Result", "점수": "Rate", "내 덱": "Use.deck", 
            "상대 덱": "Opp. deck", "아키타입": "Plus Arch.", "승패 요인": "W/L Factor",
            "특정 카드": "Certain Card", "브릭": "0", "실수": "0", "비고": "Deatil"
        }
        st.session_state.df = pd.DataFrame([sub_label_row], columns=columns)

if 'options' not in st.session_state:
    st.session_state.options = {
        "내 덱": ["KT", "SwoS", "Synchron"],
        "상대 덱": ["Mitsu", "Ennea", "DD", "Red Dra", "Branded", "Maliss"],
        "특정 카드": ["TT Talent", "Droll", "Nibiru"],
        "승패 요인": ["자신 실력", "상대 패", "특정 카드", "운"],
        "아키타입": ["60", "Arch"]
    }

# 3. 상단 탭 구성
tab1, tab2 = st.tabs(["📊 Record", "⚙️ Setting"])

# ---------------------------------------------------------
# TAB 1: Record 페이지
# ---------------------------------------------------------
with tab1:
    st.title("📊 Rating Dashboard")

    # 데이터 분리
    guide_df = st.session_state.df.iloc[[0]].copy()
    data_df = st.session_state.df.iloc[1:].copy()

    # 가이드 행 에디터 (브릭/실수 합계 표시)
    st.subheader("📋 가이드 및 통계 (수정 가능)")
    edited_guide = st.data_editor(
        guide_df, 
        use_container_width=True, 
        key="guide_editor",
        column_config={
            "브릭": st.column_config.Column("브릭 (총합)"),
            "실수": st.column_config.Column("실수 (총합)")
        }
    )

    # 실제 데이터 에디터 (체크박스 적용)
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
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.options["내 덱"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.options["상대 덱"]),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.options["특정 카드"]),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.options["승패 요인"]),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.options["아키타입"]),
            # 브릭과 실수를 체크박스로 설정
            "브릭": st.column_config.CheckboxColumn("브릭", default=False),
            "실수": st.column_config.CheckboxColumn("실수", default=False),
        }
    )

    # 데이터 저장 버튼 클릭 시 합계 계산 후 업데이트
    if st.button("💾 데이터 저장"):
        # 실제 데이터에서 체크된 개수 계산
        brick_count = edited_data["브릭"].sum()
        mistake_count = edited_data["실수"].sum()
        
        # 가이드 행의 브릭/실수 값을 업데이트된 합계로 변경
        edited_guide.at[0, "브릭"] = str(brick_count)
        edited_guide.at[0, "실수"] = str(mistake_count)
        
        # 합친 데이터를 세션에 저장
        st.session_state.df = pd.concat([edited_guide, edited_data], ignore_index=True)
        st.success(f"저장 완료! (브릭 합계: {brick_count}, 실수 합계: {mistake_count})")
        st.rerun() # 변경된 합계를 화면에 즉시 반영

    csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 CSV 다운로드", data=csv, file_name=FILENAME, mime='text/csv')

# ---------------------------------------------------------
# TAB 2: Setting 페이지 (기존과 동일)
# ---------------------------------------------------------
with tab2:
    st.title("⚙️ Setting")
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
        st.session_state.options["내 덱"] = [x.strip() for x in my_decks.split("\n") if x.strip()]
        st.session_state.options["상대 덱"] = [x.strip() for x in opp_decks.split("\n") if x.strip()]
        st.session_state.options["특정 카드"] = [x.strip() for x in specific_cards.split("\n") if x.strip()]
        st.session_state.options["승패 요인"] = [x.strip() for x in win_loss_factors.split("\n") if x.strip()]
        st.session_state.options["아키타입"] = [x.strip() for x in archetypes.split("\n") if x.strip()]
        st.success("설정이 적용되었습니다.")
