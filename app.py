import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# 파일 경로 설정
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

# 전체 앱 타이틀 설정
st.set_page_config(page_title="YGO Rating System", layout="wide")

# --- 1. 데이터 로드/저장 함수 ---
def load_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # 새로운 필드(아키타입, 승패요인)가 없을 경우 대비
                if "archetypes" not in data:
                    data["archetypes"] = ["운영", "전개", "미드레인지", "함떡", "기타"]
                if "win_loss_reasons" not in data:
                    data["win_loss_reasons"] = ["패트랩 통과", "기믹 정지", "상대 증식의 G", "핸드 말림", "상대 빌드 돌파", "실수", "기타"]
                return data
            except: pass
    return {
        "my_decks": ["KT", "Ennea", "Maliss", "Tenpai"],
        "opp_decks": ["KT", "Ennea", "Maliss", "Tenpai", "Labrynth", "Branded"],
        "archetypes": ["운영", "전개", "미드레인지", "함떡", "기타"],
        "target_cards": ["증식의 G", "하루 우라라", "무한포영", "니비루", "드롤"],
        "win_loss_reasons": ["패트랩 통과", "기믹 정지", "상대 증식의 G", "핸드 말림", "상대 빌드 돌파", "실수", "기타"]
    }

def save_metadata(data):
    with open(META_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_records():
    # 모든 요청 컬럼 포함 (매치 상세, 승패 요인 등)
    cols = ["NO.", "날짜", "선후공", "결과", "매치 상세", "내 덱", "상대 덱", "아키타입", "특정 카드", "승패 요인", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE)
        for col in cols:
            if col not in df.columns:
                df[col] = "미지정" if col not in ["브릭", "실수"] else False
        return df.reindex(columns=cols)
    return pd.DataFrame(columns=cols)

# 세션 상태 초기화
if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()
if 'df' not in st.session_state:
    st.session_state.df = load_records()

# --- 2. 사이드바 메뉴 (이름을 Rating으로 통일) ---
st.sidebar.title("🎮 Rating 메뉴")
page = st.sidebar.radio("이동할 페이지", ["📊 Rating (전적 기록/분석)", "⚙️ Rating (목록 설정)"])

# ---------------------------------------------------------
# [페이지 1] Rating (전적 기록 및 실시간 분석)
# ---------------------------------------------------------
if page == "📊 Rating (전적 기록/분석)":
    st.title("📊 Rating: 전적 기록 및 분석")
    df = st.session_state.df

    if not df.empty:
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            st.metric("총 경기", f"{len(df)}판")
        with c2:
            win_rate = (len(df[df['결과'] == '승']) / len(df) * 100) if len(df) > 0 else 0
            st.metric("전체 승률", f"{win_rate:.1f}%")
        with c3:
            # 승패 요인 차트
            reason_counts = df['승패 요인'].value_counts().reset_index()
            fig = px.pie(reason_counts, values='승패 요인', names='index', title="주요 승패 요인", height=250)
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("📝 Rating 결과 입력")
    
    if st.button("➕ 새로운 경기 추가"):
        new_no = df["NO."].max() + 1 if not df.empty else 1
        new_row = pd.DataFrame([{
            "NO.": new_no, "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"), 
            "선후공": "선", "결과": "승", 
            "매치 상세": "OO",
            "내 덱": st.session_state.metadata["my_decks"][0], 
            "상대 덱": st.session_state.metadata["opp_decks"][0],
            "아키타입": st.session_state.metadata["archetypes"][0], 
            "특정 카드": st.session_state.metadata["target_cards"][0], 
            "승패 요인": st.session_state.metadata["win_loss_reasons"][0],
            "실수": False, "브릭": False, "비고": ""
        }])
        st.session_state.df = pd.concat([df, new_row], ignore_index=True)
        st.rerun()

    # 데이터 에디터 (표 디자인 최적화)
    edited_df = st.data_editor(
        st.session_state.df, 
        use_container_width=True, 
        num_rows="dynamic",
        hide_index=True,
        key="rating_editor_v1",
        column_config={
            "NO.": st.column_config.NumberColumn("No.", disabled=True, width="small"),
            "선후공": st.column_config.SelectboxColumn("선/후", options=["선", "후"], width="small"),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"], width="small"),
            "매치 상세": st.column_config.SelectboxColumn("세트 결과", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"]),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata["my_decks"]),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata["opp_decks"]),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.metadata["archetypes"]),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.metadata["target_cards"]),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.metadata["win_loss_reasons"]),
            "실수": st.column_config.CheckboxColumn("실수", width="small"),
            "브릭": st.column_config.CheckboxColumn("브릭", width="small"),
        }
    )

    if st.button("💾 Rating 데이터 저장 및 업데이트", type="primary"):
        st.session_state.df = edited_df
        st.session_state.df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.success("Rating 데이터가 성공적으로 저장되었습니다!")
        st.rerun()

# ---------------------------------------------------------
# [페이지 2] Rating (목록 설정 관리)
# ---------------------------------------------------------
else:
    st.title("⚙️ Rating: 목록 설정 관리")
    st.info("여기서 수정한 목록이 Rating 입력창의 드롭다운 메뉴에 반영됩니다.")

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        my_decks_str = st.text_area("내 덱 리스트 (쉼표 구분)", ", ".join(st.session_state.metadata["my_decks"]), height=150)
        opp_decks_str = st.text_area("상대 덱 리스트 (쉼표 구분)", ", ".join(st.session_state.metadata["opp_decks"]), height=150)
    
    with m_col2:
        arche_str = st.text_area("상대 아키타입 (쉼표 구분)", ", ".join(st.session_state.metadata["archetypes"]), height=100)
        reasons_str = st.text_area("승패 요인 리스트 (쉼표 구분)", ", ".join(st.session_state.metadata["win_loss_reasons"]), height=100)
        cards_str = st.text_area("관심 카드 리스트 (쉼표 구분)", ", ".join(st.session_state.metadata["target_cards"]), height=100)
    
    if st.button("✅ Rating 설정값 저장", type="primary"):
        st.session_state.metadata = {
            "my_decks": [x.strip() for x in my_decks_str.split(",") if x.strip()],
            "opp_decks": [x.strip() for x in opp_decks_str.split(",") if x.strip()],
            "archetypes": [x.strip() for x in arche_str.split(",") if x.strip()],
            "win_loss_reasons": [x.strip() for x in reasons_str.split(",") if x.strip()],
            "target_cards": [x.strip() for x in cards_str.split(",") if x.strip()]
        }
        save_metadata(st.session_state.metadata)
        st.success("Rating 설정이 업데이트되었습니다!")
