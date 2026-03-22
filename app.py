import streamlit as st
import pandas as pd
import os
import json

# --- 데이터 로직 (생략 - 기존 코드 유지) ---
# load_metadata(), load_records(), save_data() 등은 그대로 사용합니다.

# --- [디자인 설정] 이미지와 동일한 승리/패배 색상 정의 ---
STYLE_CONFIG = {
    "container_width": "33%",          # 왼쪽 1/3 너비
    "font_size": "14px",
    "header_bg": "#f9cb9c",            # 연한 주황색 (이미지 헤더 색상)
    "cell_padding": "10px",
    "win_color": "#0000ff",            # 파란색 (승리)
    "loss_color": "#ff0000"            # 빨간색 (패배)
}

# --- 4. 분석 표 렌더링 함수 (이미지 디자인 완벽 재현) ---
def render_styled_table(title, target_df):
    calc_df = target_df[target_df['결과'].isin(['승', '패'])]
    total = len(calc_df)
    
    # 데이터가 없을 때 표시할 빈 표
    if total == 0:
        return f"""
            <table class="styled-table">
                <tr><th colspan="5">{title}</th></tr>
                <tr><td style='color:gray;' colspan="5">분석할 데이터가 없습니다.</td></tr>
            </table>
        """
        
    wins = len(calc_df[calc_df['결과'] == '승'])
    losses = len(calc_df[calc_df['결과'] == '패'])
    win_rate = (wins / total * 100) if total > 0 else 0
    
    f_df, s_df = calc_df[calc_df['선후공'] == '선'], calc_df[calc_df['선후공'] == '후']
    f_count, s_count = len(f_df), len(s_df)
    
    f_wins = len(f_df[f_df['결과'] == '승'])
    f_losses = len(f_df[f_df['결과'] == '패'])
    f_win_rate = (f_wins / f_count * 100) if f_count > 0 else 0
    
    s_wins = len(s_df[s_df['결과'] == '승'])
    s_losses = len(s_df[s_df['결과'] == '패'])
    s_win_rate = (s_wins / s_count * 100) if s_count > 0 else 0
    
    # 승리/패배 글씨 색상 적용 (색상은 CSS에서 처리됨)
    return f"""
        <table class="styled-table">
            <tr><th colspan="5" class="table-main-title">{title}</th></tr>
            <tr><th>Overall</th><th>Games</th><th>Win Rate</th><th>W</th><th>L</th></tr>
            <tr>
                <td>Result</td>
                <td>{total}</td>
                <td>{win_rate:.2f}%</td>
                <td class="win-val">{wins}</td>
                <td class="loss-val">{losses}</td>
            </tr>
            <tr><th>Coin</th><th>1st</th><th>2nd</th><th>1st Rate</th><th>2nd Rate</th></tr>
            <tr>
                <td>Result</td>
                <td class="win-val">{f_count}</td>
                <td class="loss-val">{s_count}</td>
                <td class="win-val">{(f_count/total*100):.2f}%</td>
                <td class="loss-val">{(s_count/total*100):.2f}%</td>
            </tr>
            <tr><th>1st</th><th>1st Win</th><th>1st Lose</th><th>1st W%</th><th>1st L%</th></tr>
            <tr>
                <td>Result</td>
                <td class="win-val">{f_wins}</td>
                <td class="loss-val">{f_losses}</td>
                <td class="win-val">{f_win_rate:.2f}%</td>
                <td class="loss-val">{(100-f_win_rate):.2f}%</td>
            </tr>
            <tr><th>2nd</th><th>2nd Win</th><th>2nd Lose</th><th>2nd W%</th><th>2nd L%</th></tr>
            <tr>
                <td>Result</td>
                <td class="win-val">{s_wins}</td>
                <td class="loss-val">{s_losses}</td>
                <td class="win-val">{s_win_rate:.2f}%</td>
                <td class="loss-val">{(100-s_win_rate):.2f}%</td>
            </tr>
        </table>
    """

# --- [디자인] 분석 페이지 전용 CSS ---
st.markdown(f"""
    <style>
    /* 분석 페이지 컨테이너 너비 제한 (1/3 너비) */
    .analysis-wrapper {{ width: {STYLE_CONFIG["container_width"]}; margin-left: 0; }}
    
    .styled-table {{ 
        width: 100%; 
        font-size: {STYLE_CONFIG["font_size"]}; 
        border-collapse: collapse; 
        margin-bottom: 30px; 
        table-layout: fixed; 
        border: 1px solid #dee2e6;
    }}
    .styled-table th, .styled-table td {{ 
        text-align: center !important; 
        border: 1px solid #dee2e6 !important; 
        padding: {STYLE_CONFIG["cell_padding"]} !important; 
    }}
    
    /* 이미지와 동일한 헤더 스타일 (연한 주황색 배경, 굵은 글씨) */
    .styled-table th {{ 
        background-color: {STYLE_CONFIG["header_bg"]} !important; 
        color: #31333F !important; 
        font-weight: bold !important; 
    }}
    
    /* 메인 타이틀 (OverallData, 덱별 승률) 스타일 */
    .styled-table th.table-main-title {{
        background-color: {STYLE_CONFIG["header_bg"]} !important;
        font-size: 16px;
        padding: 5px !important;
    }}
    
    /* 승리/패배 값 색상 적용 */
    .win-val {{ color: {STYLE_CONFIG["win_color"]} !important; font-weight: bold; }}
    .loss-val {{ color: {STYLE_CONFIG["loss_color"]} !important; font-weight: bold; }}
    
    /* 드롭다운 너비를 분석 wrapper와 일치시킴 */
    div[data-testid="stSelectbox"] {{ width: 100% !important; }}
    
    /* 드롭다운 라벨 스타일 조절 (이미지처럼 드롭다운과 일치하게) */
    div.row-widget.stSelectbox label {{
        font-weight: bold;
        margin-bottom: 2px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. 메인 로직 ---
# (세션 관리 생략 - 기존 코드 유지)

page = st.sidebar.radio("메뉴", ["📊 기록", "📈 분석", "⚙️ 설정"])

if page == "📊 기록":
    st.title("📊 전적 기록 (자동 저장)")
    # ... (기존 기록 페이지 로직 그대로 유지)

elif page == "📈 분석":
    st.title("📈 Rating Analysis")
    df_ana = load_records() # 최신 데이터 로드
    if not df_ana.empty:
        st.markdown('<div class="analysis-wrapper">', unsafe_allow_html=True)
        
        # --- 1. Overall Data (통합 통계) ---
        st.markdown(render_styled_table("Overall Data", df_ana), unsafe_allow_html=True)
        
        # --- 2. 덱별 승률 (내 덱 필터링) ---
        st.subheader("덱별 승률")
        my_deck_list = st.session_state.metadata["my_decks"]
        # 이미지처럼 드롭다운 스타일 맞춤
        selected_my_deck = st.selectbox("내 덱 선택", my_deck_list, label_visibility="collapsed", key="my_deck_sel")
        
        # 필터링된 데이터 전달
        filtered_my_df = df_ana[df_ana['내 덱'] == selected_my_deck]
        st.markdown(render_styled_table(selected_my_deck, filtered_my_df), unsafe_allow_html=True)
        
        # --- 3. 상대 덱별 승률 (이미지 완벽 재현 - 멀티 필터링) ---
        st.subheader("상대 덱별 승률")
        
        # 이미지처럼 가로로 배치된 드롭다운 구현
        c1, c2 = st.columns(2)
        with c1:
            multi_my_deck = st.selectbox("내 덱 (Use.Deck)", my_deck_list, label_visibility="collapsed", key="mult_my_sel")
        with c2:
            opp_deck_list = st.session_state.metadata["opp_decks"]
            multi_opp_deck = st.selectbox("상대 덱 (Opp.Deck)", opp_deck_list, label_visibility="collapsed", key="mult_opp_sel")
            
        # 이중 필터링 적용
        final_filtered_df = df_ana[
            (df_ana['내 덱'] == multi_my_deck) & 
            (df_ana['상대 덱'] == multi_opp_deck)
        ]
        
        # 필터링된 결과로 표 렌더링
        st.markdown(render_styled_table("결과", final_filtered_df), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("분석할 전적 데이터가 없습니다. 먼저 기록 페이지에서 전적을 추가해 주세요.")

else:
    st.title("⚙️ Rating 설정")
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
            # ✅ 괄호 닫기 오류(SyntaxError)가 발생했던 부분 수정 완료
            json.dump(st.session_state.metadata, f, ensure_ascii=False, indent=4)
        st.success("설정 저장 완료!")
        st.rerun()
