import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# 파일 경로
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="듀얼 기록 마스터", layout="wide")

# --- 1. 데이터 로드/저장 함수 ---
def load_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # 혹시 기존 설정에 archetypes가 없으면 추가
                if "archetypes" not in data:
                    data["archetypes"] = ["운영", "전개", "미드레인지", "함떡", "기타"]
                return data
            except: pass
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
    cols = ["NO.", "날짜", "선후공", "결과", "내 덱", "상대 덱", "아키타입", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE)
        # [중요] 기존 파일에 '아키타입' 컬럼이 없으면 새로 만들어줍니다.
        if "아키타입" not in df.columns:
            df["아키타입"] = "미지정"
        # 컬럼 순서를 위 정의대로 강제 정렬합니다.
        return df.reindex(columns=cols)
    return pd.DataFrame(columns=cols)

if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()
if 'df' not in st.session_state:
    st.session_state.df = load_records()

# --- 2. 사이드바 메뉴 ---
st.sidebar.title("🎮 듀얼 메뉴")
page = st.sidebar.radio("이동할 시트", ["📊 전적 기록 (Record)", "⚙️ 설정 관리 (Meta Data)"])

# ---------------------------------------------------------
# [페이지 1] Record
# ---------------------------------------------------------
if page == "📊 전적 기록 (Record)":
    st.title("📊 듀얼 전적 및 실시간 분석")
    df = st.session_state.df

    if not df.empty:
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("총 경기", f"{len(df)}판")
        with c2: st.metric("전체 승률", f"{(len(df[df['결과'] == '승']) / len(df) * 100 if len(df)>0 else 0):.1f}%")
        with c3:
            # 아키타입 분포 그래프 (데이터가 있을 때만)
            if "아키타입" in df.columns:
                fig = px.bar(df['아키타입'].value_counts().reset_index(), x='index', y='아키타입', 
                             title="상대 아키타입 분포", height=250, labels={'index':'아키타입', '아키타입':'판수'})
                st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("📝 듀얼 결과 기록")
    
    if st.button("➕ 새로운 경기 데이터 추가"):
        new_no = df["NO."].max() + 1 if not df.empty else 1
        new_row = pd.DataFrame([{
            "NO.": new_no, "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"), 
            "선후공": "선", "결과": "승", 
            "내 덱": st.session_state.metadata["my_decks"][0], 
            "상대 덱": st.session_state.metadata["opp_decks"][0],
            "아키타입": st.session_state.metadata["archetypes"][0], 
            "특정 카드": st.session_state.metadata["target_cards"][0], 
            "실수": False, "브릭": False, "비고": ""
        }])
        st.session_state.df = pd.concat([df, new_row], ignore_index=True)
        st.rerun()

    # 데이터 에디터 (표 출력)
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
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.metadata["archetypes"]),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.metadata["target_cards"]),
            "실수": st.column_config.CheckboxColumn("실수"),
            "브릭": st.column_config.CheckboxColumn("브릭")
        }
    )

    if st.button("💾 모든 데이터 저장", type="primary"):
        st.session_state.df = edited_df
        st.session_state.df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
        st.success("데이터가 성공적으로 저장되었습니다!")
        st.rerun()

# ---------------------------------------------------------
# [페이지 2] Meta Data
# ---------------------------------------------------------
else:
    st.title("⚙️ Meta Data: 목록 설정")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        my_decks_str = st.text_area("내 덱 리스트", ", ".join(st.session_state.metadata["my_decks"]), height=150)
        opp_decks_str = st.text_area("상대 덱 리스트", ", ".join(st.session_state.metadata["opp_decks"]), height=150)
    
    with m_col2:
        arche_str = st.text_area("상대 아키타입 (운영, 전개 등)", ", ".join(st.session_state.metadata["archetypes"]), height=150)
        cards_str = st.text_area("특정 카드 리스트", ", ".join(st.session_state.metadata["target_cards"]), height=150)
    
    if st.button("✅ 모든 설정값 저장", type="primary"):
        st.session_state.metadata = {
            "my_decks": [x.strip() for x in my_decks_str.split(",") if x.strip()],
            "opp_decks": [x.strip() for x in opp_decks_str.split(",") if x.strip()],
            "archetypes": [x.strip() for x in arche_str.split(",") if x.strip()],
            "target_cards": [x.strip() for x in cards_str.split(",") if x.strip()]
        }
        save_metadata(st.session_state.metadata)
        st.success("설정값이 업데이트되었습니다!")
