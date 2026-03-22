import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. [디자인] 분석 페이지 전용 스타일 업데이트 ---
st.markdown("""
    <style>
    /* 공통 테이블 스타일 */
    [data-testid="stTableIdxColumn"] { display: none !important; width: 0px !important; }
    th.col_heading.level0.index_name { display: none !important; }
    [data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"] div:first-child svg { display: none !important; }

    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div {
        text-align: center !important; font-size: 13px !important;
    }

    /* 이미지 스타일의 분석 테이블 */
    .analysis-container { margin-bottom: 40px; }
    .matchup-table { 
        width: 100%; font-size: 12px; border-collapse: collapse; 
        table-layout: fixed; border: 1px solid #000;
    }
    .matchup-table th, .matchup-table td { 
        text-align: center !important; border: 1px solid #dee2e6 !important; padding: 4px !important; 
    }
    .matchup-table th { 
        background-color: #fbbc04 !important; color: #000 !important; font-weight: bold !important; 
    }
    .total-row { background-color: #fff2cc; font-weight: bold; }
    .win-text { color: #0000ff; font-weight: bold; }
    .loss-text { color: #ff0000; font-weight: bold; }
    
    div[data-testid="stSelectbox"] { width: 300px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 로직 ---
def load_metadata():
    default_meta = {
        "my_decks": ["KT", "Ennea", "Maliss", "Tenpai"],
        "opp_decks": ["KT", "Ennea", "Maliss", "Tenpai", "Labrynth", "Branded"],
        "archetypes": ["운영", "전개", "미드레인지", "함떡", "기타"],
        "win_loss_reasons": ["상대 패", "자신 실력", "특정 카드", "핸드 말림", "기타"],
        "target_cards": ["증식의 G", "하루 우라라", "무한포영", "니비루", "드롤"]
    }
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            try:
                saved = json.load(f)
                for key in default_meta:
                    if key not in saved: saved[key] = default_meta[key]
                return saved
            except: pass
    return default_meta

def load_records():
    cols = ["NO.", "날짜", "선후공", "결과", "세트 전적", "내 덱", "상대 덱", "아키타입", "승패 요인", "특정 카드", "브릭", "실수", "비고"]
    if os.path.exists(RECORD_FILE):
        try:
            df = pd.read_csv(RECORD_FILE, dtype=str).fillna("")
            for col in cols:
                if col not in df.columns: df[col] = ""
            for col in ["브릭", "실수"]:
                df[col] = df[col].apply(lambda x: True if str(x).lower() in ['true', '1'] else False)
            return df[cols].reset_index(drop=True)
        except: pass
    return pd.DataFrame(columns=cols)

def save_data(df):
    df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
    st.session_state.df = df.reset_index(drop=True)

# [핵심] 이미지의 상대 덱별 지표 계산 함수
def render_matchup_analysis(target_df):
    calc_df = target_df[target_df['결과'].isin(['승', '패'])]
    total_count = len(calc_df)
    if total_count == 0:
        return "<p>데이터가 없습니다.</p>"

    # 상대 덱별 그룹화
    unique_opps = calc_df['상대 덱'].unique()
    stats = []
    
    # 상단 Total 행 계산
    total_w = len(calc_df[calc_df['결과'] == '승'])
    total_l = len(calc_df[calc_df['결과'] == '패'])
    total_f = calc_df[calc_df['선후공'] == '선']
    total_s = calc_df[calc_df['선후공'] == '후']
    
    total_f_w = (len(total_f[total_f['결과'] == '승']) / len(total_f) * 100) if len(total_f) > 0 else 0
    total_s_w = (len(total_s[total_s['결과'] == '승']) / len(total_s) * 100) if len(total_s) > 0 else 0

    rows_html = f"""
        <tr class="total-row">
            <td>Total</td><td>{total_count}</td><td class="win-text">{total_w}</td><td class="loss-text">{total_l}</td>
            <td>{(total_w/total_count*100):.2f}%</td><td>{total_f_w:.2f}%</td><td>{total_s_w:.2f}%</td><td>100.00%</td><td>-</td>
        </tr>
    """

    for opp in unique_opps:
        opp_df = calc_df[calc_df['상대 덱'] == opp]
        t = len(opp_df)
        w = len(opp_df[opp_df['결과'] == '승'])
        l = len(opp_df[opp_df['결과'] == '패'])
        
        f_df = opp_df[opp_df['선후공'] == '선']
        s_df = opp_df[opp_df['선후공'] == '후']
        
        fw = (len(f_df[f_df['결과'] == '승']) / len(f_df) * 100) if len(f_df) > 0 else 0
        sw = (len(s_df[s_df['결과'] == '승']) / len(s_df) * 100) if len(s_df) > 0 else 0
        
        share = (t / total_count * 100)
        # 아키타입 기입 비율 계산 (비어있지 않은 아키타입 수 / 해당 덱 총 경기수)
        arch_count = len(opp_df[opp_df['아키타입'] != ""])
        arch_share = (arch_count / t * 100)

        rows_html += f"""
            <tr>
                <td>{opp}</td><td>{t}</td><td class="win-text">{w}</td><td class="loss-text">{l}</td>
                <td>{(w/t*100):.2f}%</td><td>{fw:.2f}%</td><td>{sw:.2f}%</td><td>{share:.2f}%</td><td>{arch_share:.2f}%</td>
            </tr>
        """

    return f"""
        <table class="matchup-table">
            <tr>
                <th style="width:15%">Matchup</th><th style="width:8%">Total</th><th style="width:8%">W</th><th style="width:8%">L</th>
                <th style="width:12%">W%</th><th style="width:12%">1st W%</th><th style="width:12%">2nd W%</th><th style="width:12%">Share</th><th style="width:13%">Arch Share</th>
            </tr>
            {rows_html}
        </table>
    """

# --- 4. 메인 로직 ---
if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()
if 'df' not in st.session_state:
    st.session_state.df = load_records()

page = st.sidebar.radio("메뉴", ["📊 Record", "📈 Analysis", "⚙️ Setting"])

if page == "📊 Record":
    st.title("📊 Record")
    if st.button("➕ 새로운 경기 추가"):
        meta = st.session_state.metadata
        new_row = pd.DataFrame([{
            "NO.": str(len(st.session_state.df) + 1), "날짜": pd.Timestamp.now().strftime("%m.%d"),
            "선후공": "선", "결과": "승", "세트 전적": "OO",
            "내 덱": meta["my_decks"][0], "상대 덱": meta["opp_decks"][0],
            "아키타입": meta["archetypes"][0], "승패 요인": meta["win_loss_reasons"][0],
            "특정 카드": meta["target_cards"][0], "브릭": False, "실수": False, "비고": ""
        }])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True).reset_index(drop=True)
        save_data(st.session_state.df)
        st.rerun()

    edited_df = st.data_editor(
        st.session_state.df, use_container_width=True, num_rows="dynamic", hide_index=True, key="ygo_editor_v10",
        column_config={
            "NO.": st.column_config.TextColumn("NO.", width=45),
            "날짜": st.column_config.TextColumn("날짜", width=65),
            "선후공": st.column_config.SelectboxColumn("선후공", options=["선", "후"], width=65),
            "결과": st.column_config.SelectboxColumn("결과", options=["승", "패"], width=65),
            "세트 전적": st.column_config.SelectboxColumn("세트", options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"], width=85),
            "내 덱": st.column_config.SelectboxColumn("내 덱", options=st.session_state.metadata.get("my_decks", []), width=100),
            "상대 덱": st.column_config.SelectboxColumn("상대 덱", options=st.session_state.metadata.get("opp_decks", []), width=100),
            "아키타입": st.column_config.SelectboxColumn("아키타입", options=st.session_state.metadata.get("archetypes", []), width=90),
            "승패 요인": st.column_config.SelectboxColumn("승패 요인", options=st.session_state.metadata.get("win_loss_reasons", []), width=100),
            "특정 카드": st.column_config.SelectboxColumn("특정 카드", options=st.session_state.metadata.get("target_cards", []), width=100),
            "브릭": st.column_config.CheckboxColumn("브릭", width=85), 
            "실수": st.column_config.CheckboxColumn("실수", width=85), 
            "비고": st.column_config.TextColumn("비고", width=500)
        }
    )
    if not edited_df.equals(st.session_state.df):
        save_data(edited_df)
        st.rerun()

elif page == "📈 Analysis":
    st.title("📈 Matchup Analysis")
    df_ana = load_records()
    
    if not df_ana.empty:
        # 내 덱 필터링
        sel_my = st.selectbox("My Deck Filter", st.session_state.metadata["my_decks"])
        filtered_df = df_ana[df_ana['내 덱'] == sel_my]
        
        st.markdown(f"### [ {sel_my} ] Matchup Statistics")
        # 이미지의 표 형식으로 렌더링
        st.markdown(render_matchup_analysis(filtered_df), unsafe_allow_html=True)
        
        # 추가 분석 (선택한 상대 덱과의 상세 전적)
        st.divider()
        st.subheader("상세 매치 확인")
        sel_opp = st.selectbox("Opponent Deck", st.session_state.metadata["opp_decks"])
        detail_df = filtered_df[filtered_df['상대 덱'] == sel_opp]
        st.dataframe(detail_df, use_container_width=True, hide_index=True)

else:
    st.title("⚙️ Setting")
    meta = st.session_state.metadata
    c1, c2 = st.columns(2)
    with c1: new_my = st.text_area("내 덱 (쉼표 구분)", ", ".join(meta.get("my_decks", [])))
    with c2: new_opp = st.text_area("상대 덱 (쉼표 구분)", ", ".join(meta.get("opp_decks", [])))
    c3, c4 = st.columns(2)
    with c3: new_reasons = st.text_area("승패 요인 (쉼표 구분)", ", ".join(meta.get("win_loss_reasons", [])))
    with c4: new_arche = st.text_area("아키타입 (쉼표 구분)", ", ".join(meta.get("archetypes", [])))
    c5, _ = st.columns(2)
    with c5: new_cards = st.text_area("특정 카드 (쉼표 구분)", ", ".join(meta.get("target_cards", [])))
    
    if st.button("✅ 설정 저장"):
        st.session_state.metadata = {
            "my_decks": [x.strip() for x in new_my.split(",") if x.strip()],
            "opp_decks": [x.strip() for x in new_opp.split(",") if x.strip()],
            "win_loss_reasons": [x.strip() for x in new_reasons.split(",") if x.strip()],
            "archetypes": [x.strip() for x in new_arche.split(",") if x.strip()],
            "target_cards": [x.strip() for x in new_cards.split(",") if x.strip()]
        }
        with open(META_FILE, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.metadata, f, ensure_ascii=False, indent=4)
        st.success("설정 저장 완료!")
        st.rerun()
