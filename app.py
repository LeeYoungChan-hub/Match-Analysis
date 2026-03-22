import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. [디자인] 시스템 요소 숨기기 및 분석 레이아웃 CSS ---
st.markdown("""
    <style>
    /* [기록 페이지] 시스템 인덱스 및 편집 아이콘 완전 숨김 */
    [data-testid="stTableIdxColumn"] { display: none !important; width: 0px !important; }
    th.col_heading.level0.index_name { display: none !important; }
    
    [data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"] div:first-child svg {
        display: none !important;
    }

    /* 표 내부 텍스트 중앙 정렬 및 폰트 크기 조절 */
    div.row-widget.stDataFrame div[role="grid"] div[role="row"] div {
        text-align: center !important;
        font-size: 13px !important;
    }

    /* [분석 페이지] 이미지 비율 유지를 위한 너비 고정 */
    .analysis-wrapper { width: 420px; margin-left: 0; }
    .styled-table { 
        width: 100%; font-size: 13px; border-collapse: collapse; 
        margin-bottom: 30px; table-layout: fixed; border: 1px solid #dee2e6;
    }
    .styled-table th, .styled-table td { 
        text-align: center !important; border: 1px solid #dee2e6 !important; padding: 6px !important; 
    }
    .styled-table th { 
        background-color: #f9cb9c !important; color: #31333F !important; font-weight: bold !important; 
    }
    .win-val { color: #0000ff !important; font-weight: bold; }
    .loss-val { color: #ff0000 !important; font-weight: bold; }
    
    div[data-testid="stSelectbox"] { width: 100% !important; }
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

def render_styled_table(title, target_df):
    calc_df = target_df[target_df['결과'].isin(['승', '패'])]
    total = len(calc_df)
    if total == 0:
        return f'<table class="styled-table"><tr><th>{title}</th></tr><tr><td>데이터 없음</td></tr></table>'
    
    wins = len(calc_df[calc_df['결과'] == '승'])
    losses = len(calc_df[calc_df['결과'] == '패'])
    win_rate = (wins / total * 100)
    
    f_df, s_df = calc_df[calc_df['선후공'] == '선'], calc_df[calc_df['선후공'] == '후']
    f_total, s_total = len(f_df), len(s_df)
    f_wins = len(f_df[f_df['결과'] == '승'])
    s_wins = len(s_df[s_df['결과'] == '승'])
    
    return f"""
        <table class="styled-table">
            <tr><th colspan="5">{title}</th></tr>
            <tr><th>Overall</th><th>Games</th><th>Win Rate</th><th>W</th><th>L</th></tr>
            <tr><td>Result</td><td>{total}</td><td>{win_rate:.2f}%</td><td class="win-val">{wins}</td><td class="loss-val">{losses}</td></tr>
            <tr><th>Coin</th><th>1st</th><th>2nd</th><th>1st Rate</th><th>2nd Rate</th></tr>
            <tr><td>Result</td><td class="win-val">{f_total}</td><td class="loss-val">{s_total}</td><td class="win-val">{(f_total/total*100):.1f}%</td><td class="loss-val">{(s_total/total*100):.1f}%</td></tr>
            <tr><th>1st</th><th>1st Win</th><th>1st Lose</th><th>1st W%</th><th>1st L%</th></tr>
            <tr><td>Result</td><td class="win-val">{f_wins}</td><td class="loss-val">{f_total-f_wins}</td><td class="win-val">{(f_wins/f_total*100 if f_total>0 else 0):.1f}%</td><td class="loss-val">{(100-(f_wins/f_total*100) if f_total>0 else 0):.1f}%</td></tr>
            <tr><th>2nd</th><th>2nd Win</th><th>2nd Lose</th><th>2nd W%</th><th>2nd L%</th></tr>
            <tr><td>Result</td><td class="win-val">{s_wins}</td><td class="loss-val">{s_total-s_wins}</td><td class="win-val">{(s_wins/s_total*100 if s_total>0 else 0):.1f}%</td><td class="loss-val">{(100-(s_wins/s_total*100) if s_total>0 else 0):.1f}%</td></tr>
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
            "선후공": "선", "결과": "승", "세트": "OO",
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
            "브릭": st.column_config.CheckboxColumn("브릭", width=85), # 1.5배 확장
            "실수": st.column_config.CheckboxColumn("실수", width=85), # 1.5배 확장
            "비고": st.column_config.TextColumn("비고", width=500)
        }
    )
    if not edited_df.equals(st.session_state.df):
        save_data(edited_df)
        st.rerun()

# --- [Analysis 페이지 섹션에 추가할 코드] ---

elif page == "📈 Analysis":
    st.title("📈 Rating Analysis")
    df_ana = load_records()
    
    if not df_ana.empty:
        # 1. 상단 Overall 요약
        st.markdown('<div class="analysis-wrapper">', unsafe_allow_html=True)
        st.markdown(render_styled_table("Overall Data", df_ana), unsafe_allow_html=True)
        
        # 2. 내 덱 선택 필터
        st.subheader("내 덱별 상세 분석")
        sel_my = st.selectbox("내 덱 선택", st.session_state.metadata["my_decks"], label_visibility="collapsed")
        
        # 3. 선택한 내 덱의 기본 요약 표
        st.markdown(render_styled_table(f"Result: {sel_my}", df_ana[df_ana['내 덱'] == sel_my]), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        # 4. [수정됨] Setting에 등록된 모든 상대 덱별 지표 표
        st.subheader(f"📊 {sel_my} Matchup Analysis (All Registered Decks)")
        
        # 현재 내 덱으로 필터링된 데이터
        matchup_df = df_ana[df_ana['내 덱'] == sel_my]
        calc_df = matchup_df[matchup_df['결과'].isin(['승', '패'])]
        
        # 설정(Setting)에 등록된 모든 상대 덱 리스트 가져오기
        all_opp_decks = st.session_state.metadata.get("opp_decks", [])
        
        if all_opp_decks:
            total_games_all = len(calc_df)
            
            # 상단 Total 합계 행 계산
            tw = len(calc_df[calc_df['결과'] == '승'])
            tl = len(calc_df[calc_df['결과'] == '패'])
            tf = calc_df[calc_df['선후공'] == '선']
            ts = calc_df[calc_df['선후공'] == '후']
            tfw = (len(tf[tf['결과'] == '승']) / len(tf) * 100) if len(tf) > 0 else 0
            tsw = (len(ts[ts['결과'] == '승']) / len(ts) * 100) if len(ts) > 0 else 0

            # 표 본문 생성 (설정된 모든 덱을 순회)
            rows_html = f"""
                <tr style="background-color: #fff2cc; font-weight: bold;">
                    <td>Total</td><td>{total_games_all}</td><td class="win-val">{tw}</td><td class="loss-val">{tl}</td>
                    <td>{(tw/total_games_all*100 if total_games_all>0 else 0):.2f}%</td>
                    <td>{tfw:.2f}%</td><td>{tsw:.2f}%</td><td>100.00%</td><td>-</td>
                </tr>
            """

            for opp in all_opp_decks:
                # 해당 상대 덱의 데이터만 추출
                opp_sub = calc_df[calc_df['상대 덱'] == opp]
                g = len(opp_sub)
                
                if g > 0:
                    # 데이터가 있는 경우 계산
                    w = len(opp_sub[opp_sub['결과'] == '승'])
                    l = len(opp_sub[opp_sub['결과'] == '패'])
                    f_sub = opp_sub[opp_sub['선후공'] == '선']
                    s_sub = opp_sub[opp_sub['선후공'] == '후']
                    fw = (len(f_sub[f_sub['결과'] == '승']) / len(f_sub) * 100) if len(f_sub) > 0 else 0
                    sw = (len(s_sub[s_sub['결과'] == '승']) / len(s_sub) * 100) if len(s_sub) > 0 else 0
                    share = (g / total_games_all * 100)
                    arch_count = len(opp_sub[opp_sub['아키타입'] != ""])
                    arch_share = (arch_count / g * 100)
                    
                    rows_html += f"""
                        <tr>
                            <td>{opp}</td><td>{g}</td><td class="win-val">{w}</td><td class="loss-val">{l}</td>
                            <td>{(w/g*100):.2f}%</td><td>{fw:.2f}%</td><td>{sw:.2f}%</td><td>{share:.2f}%</td><td>{arch_share:.2f}%</td>
                        </tr>
                    """
                else:
                    # 데이터가 없는 경우 (0으로 표시)
                    rows_html += f"""
                        <tr style="color: #999;">
                            <td>{opp}</td><td>0</td><td>0</td><td>0</td>
                            <td>0.00%</td><td>0.00%</td><td>0.00%</td><td>0.00%</td><td>0.00%</td>
                        </tr>
                    """

            # 최종 테이블 출력
            st.markdown(f"""
                <table class="styled-table" style="table-layout: auto; width: 100%;">
                    <tr style="background-color: #fbbc04 !important; color: black;">
                        <th>Matchup</th><th>Total</th><th>W</th><th>L</th>
                        <th>W%</th><th>1st W%</th><th>2nd W%</th><th>Share</th><th>Plus Arch</th>
                    </tr>
                    {rows_html}
                </table>
            """, unsafe_allow_html=True)
        else:
            st.info("Setting에서 상대 덱을 먼저 등록해 주세요.")
    else:
        st.warning("먼저 'Record' 페이지에서 경기를 기록해 주세요.")

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
