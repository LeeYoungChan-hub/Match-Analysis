import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# 파일 경로
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

# 페이지 이름 및 레이아웃 설정
st.set_page_config(page_title="Rating", layout="wide")

# --- 1. 데이터 로드/저장 함수 ---
def load_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "my_decks": ["KT", "Ennea", "Maliss", "Tenpai"],
        "opp_decks": ["KT", "Ennea", "Maliss", "Tenpai", "Labrynth", "Branded"],
        "archetypes": ["운영", "전개", "미드레인지", "함떡", "기타"],
        "target_cards": ["증식의 G", "하루 우라라", "무한포영", "니비루", "드롤"]
    }

def save_metadata(data):
    with open(META_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_records():
    if os.path.exists(RECORD_FILE):
        return pd.read_csv(RECORD_FILE)
    # 아키타입 컬럼이 추가된 초기 데이터프레임
    return pd.DataFrame(columns=["NO.", "날짜", "선후공", "결과", "내 덱", "상대 덱", "아키타입", "특정 카드", "브릭", "실수", "비고"])

if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()
if 'df' not in st.session_state:
    st.session_state.df = load_records()

# --- 2. 사이드바 메뉴 (페이지 이름 변경) ---
st.sidebar.title("🎮 듀얼 메뉴")
# 라디오 버튼의 이름을 더 직관적으로 변경했습니다.
page = st.sidebar.radio("이동할 시트", ["📊 듀얼 전적 기록 (Record)", "⚙️ 덱/아키타입 설정 (Meta Data)"])

# ---------------------------------------------------------
# [페이지 1] Record (전적 및 분석)
# ---------------------------------------------------------
if page == "📊 듀얼 전적 기록 (Record)":
    st.title("📊 듀얼 전적 및 실시간 분석")
    df = st.session_state.df

    if not df.empty:
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("총 경기", f"{len(df)}판")
        with c2: st.metric("전체 승률", f"{(len(df[df['결과'] == '승']) / len(df) * 100 if len(df)>0 else 0):.1f}%")
        with c3:
            # 아키타입별 분포 그래프 추가
            fig = px.bar(df['아키타입'].value_counts().reset_index(), x='index', y='아키타입', 
                         title="상대 아키타입 분포", height=300, labels={'index':'아키타입', '아키타입':'판수'})
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("📝 듀얼 결과 기록")
    
    if st.button("➕ 새로운 경기 데이터 추가"):
        new_no = df["NO."].max() + 1 if not df.empty else 1
        new_row = pd.DataFrame([{
            "NO.": new_no, 
            "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"), 
            "선후공": "선", 
            "결과": "승", 
            "내 덱": st.session_state.metadata["my_decks"][0], 
            "상대 덱": st.session_state.metadata["opp_decks"][0],
            "아키타입": st.session_state.metadata["archetypes"][0], # 초기값 추가
            "특정 카드": st.session_state.metadata["target_cards"][0], 
            "실수": False, 
            "브릭": False,
            "비고": ""
        }])
        st.session_state.df = pd.concat([df, new_row], ignore_index=True)
        st.rerun()

    # 데이터 에디터 (아키타입 컬럼 배치 및 드롭다운 연결)
    edited_df = st.data_editor(
        st.session_state.df, 
        use_container_width=True, 
        num_rows="dynamic", 
        hide_index=True,
        column_config={
            "NO.": st.column_config.NumberColumn("No.", disabled=True),
            "선후공": st.column_config.SelectboxColumn("선/후", options=["선", "후"]),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"]),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata["my_decks"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata["opp_decks"]),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.metadata["archetypes"]), # 추가
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.metadata["target_cards"]),
            "실수": st.column_config.CheckboxColumn("실수"),
            "브릭": st.column_config.CheckboxColumn("브릭")
        }
    )

    if st.button("💾 모든 데이터 저장", type="primary"):
        st.session_state.df = edited_df
        st.session_state.df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.success("성공적으로 저장되었습니다!")

# ---------------------------------------------------------
# [페이지 2] Meta Data (목록 관리)
# ---------------------------------------------------------
else:
    st.title("⚙️ Meta Data: 목록 및 환경 설정")
    st.info("쉼표(,)를 기준으로 항목을 나누어 입력하세요. 저장하면 즉시 전적 창의 드롭다운에 반영됩니다.")

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        my_decks_str = st.text_area("내 덱 리스트", ", ".join(st.session_state.metadata["my_decks"]), height=150)
        opp_decks_str = st.text_area("상대 덱 리스트", ", ".join(st.session_state.metadata["opp_decks"]), height=150)
    
    with m_col2:
        # 아키타입 관리 입력창 추가
        archetypes_str = st.text_area("상대 아키타입 종류 (운영, 전개 등)", ", ".join(st.session_state.metadata["archetypes"]), height=150)
        cards_str = st.text_area("특정 카드 리스트", ", ".join(st.session_state.metadata["target_cards"]), height=150)
    
    if st.button("✅ 모든 설정값 저장", type="primary"):
        st.session_state.metadata = {
            "my_decks": [x.strip() for x in my_decks_str.split(",") if x.strip()],
            "opp_decks": [x.strip() for x in opp_decks_str.split(",") if x.strip()],
            "archetypes": [x.strip() for x in archetypes_str.split(",") if x.strip()], # 저장 로직 추가
            "target_cards": [x.strip() for x in cards_str.split(",") if x.strip()]
        }
        save_metadata(st.session_state.metadata)
        st.success("설정값이 업데이트되었습니다! Record 시트에서 확인하세요.")
