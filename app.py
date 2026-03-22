import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. 데이터 로드 및 저장 함수 ---
def load_records():
    file_path = '2026.03 레이팅 - Record.csv'
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        # 파일이 없을 경우 초기 컬럼 (점수 포함)
        return pd.DataFrame(columns=[
            'NO.', '날짜', '선후공', '결과', '세트 전적', '점수', 
            '내 덱', '상대 덱', '아키타입', '비고'
        ])

def save_records(df):
    df.to_csv('2026.03 레이팅 - Record.csv', index=False)

# --- 2. 세션 상태 및 초기 설정 ---
if "metadata" not in st.session_state:
    st.session_state.metadata = {
        "my_decks": ["KT", "Ennea", "Maliss"],
        "opp_decks": ["KT", "Ennea", "Maliss", "Tenpai", "Labrynth", "Branded", "Mitsu", "DD", "Red Dra", "Dracotail", "Clown Clan"]
    }

# --- 3. 사이드바 메뉴 ---
page = st.sidebar.selectbox("메뉴 선택", ["📝 Record", "📈 Analysis"])

# --- 📝 4. Record 페이지 ---
if page == "📝 Record":
    st.title("📝 Match Recording")
    df = load_records()

    with st.form("match_record_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            no_val = len(df[pd.to_numeric(df['NO.'], errors='coerce').notnull()]) + 1
            date_val = st.date_input("날짜", datetime.now())
        with col2:
            turn_val = st.selectbox("선후공", ["선", "후"])
        with col3:
            result_val = st.selectbox("결과", ["승", "패"])
        
        col4, col5, col6 = st.columns(3)
        with col4:
            sets_val = st.text_input("세트 전적", placeholder="예: XOO")
        with col5:
            score_val = st.text_input("점수", placeholder="예: 2-1") # 점수 칸 추가
        with col6:
            my_deck_val = st.selectbox("내 덱", st.session_state.metadata["my_decks"])
            
        col7, col8 = st.columns(2)
        with col7:
            opp_deck_val = st.selectbox("상대 덱", st.session_state.metadata["opp_decks"])
        with col8:
            arch_val = st.text_input("아키타입", placeholder="세부 아키타입")
            
        note_val = st.text_area("비고")
        
        submit = st.form_submit_button("기록 저장")

        if submit:
            new_entry = {
                'NO.': no_val, '날짜': date_val, '선후공': turn_val, '결과': result_val,
                '세트 전적': sets_val, '점수': score_val, '내 덱': my_deck_val, 
                '상대 덱': opp_deck_val, '아키타입': arch_val, '비고': note_val
            }
            # 데이터 합치기
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_records(df)
            st.success(f"No.{no_val} 경기가 성공적으로 저장되었습니다!")

    st.subheader("최근 기록 (최신 5건)")
    st.dataframe(df.tail(5), use_container_width=True)

# --- 📈 5. Analysis 페이지 ---
elif page == "📈 Analysis":
    st.title("📈 Rating Analysis")
    raw_df = load_records()
    
    # 데이터 정제: NO.가 숫자인 행만 (설명글 제외)
    if not raw_df.empty:
        df_ana = raw_df[pd.to_numeric(raw_df['NO.'], errors='coerce').notnull()].copy()
    else:
        df_ana = pd.DataFrame()

    if not df_ana.empty:
        sel_my = st.selectbox("분석할 내 덱 선택", st.session_state.metadata["my_decks"])
        
        # 필터링: 선택한 내 덱 & 승/패 결과가 명확한 데이터
        calc_df = df_ana[(df_ana['내 덱'] == sel_my) & (df_ana['결과'].isin(['승', '패']))]
        
        if not calc_df.empty:
            st.subheader(f"📊 {sel_my} Matchup Analysis")
            
            # 기초 통계 계산
            total_cnt = len(calc_df)
            w_cnt = len(calc_df[calc_df['결과'] == '승'])
            l_cnt = len(calc_df[calc_df['결과'] == '패'])
            
            f_df = calc_df[calc_df['선후공'] == '선']
            s_df = calc_df[calc_df['선후공'] == '후']
            fw_rate = (len(f_df[f_df['결과'] == '승']) / len(f_df) * 100) if len(f_df) > 0 else 0
            sw_rate = (len(s_df[s_df['결과'] == '승']) / len(s_df) * 100) if len(s_df) > 0 else 0
            arch_total = len(calc_df[calc_df['아키타입'].fillna('').astype(str).str.strip() != ""])

            # --- HTML 표 생성 시작 ---
            html_rows = []
            
            # 1. Total 합계 행 (노란색 강조)
            html_rows.append(f"""
                <tr style="background-color: #fff2cc; font-weight: bold;">
                    <td style="padding:8px; border:1px solid #dee2e6;">Total</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">{total_cnt}</td>
                    <td style="padding:8px; border:1px solid #dee2e6; color:blue;">{w_cnt}</td>
                    <td style="padding:8px; border:1px solid #dee2e6; color:red;">{l_cnt}</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">{(w_cnt/total_cnt*100):.2f}%</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">{fw_rate:.2f}%</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">{sw_rate:.2f}%</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">100%</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">{arch_total}</td>
                </tr>
            """)

            # 2. 개별 상대 덱 리스트 루프
            # 데이터에 있는 상대 덱과 설정된 상대 덱 모두 포함
            display_opps = sorted(list(set(st.session_state.metadata["opp_decks"]) | set(calc_df['상대 덱'].unique())))
            
            for opp in display_opps:
                opp_df = calc_df[calc_df['상대 덱'] == opp]
                g = len(opp_df)
                
                if g > 0:
                    ow = len(opp_df[opp_df['결과'] == '승'])
                    ol = len(opp_df[opp_df['결과'] == '패'])
                    of = opp_df[opp_df['선후공'] == '선']
                    os_ = opp_df[opp_df['선후공'] == '후']
                    ofw = (len(of[of['결과'] == '승']) / len(of) * 100) if len(of) > 0 else 0
                    osw = (len(os_[os_['결과'] == '승']) / len(os_) * 100) if len(os_) > 0 else 0
                    arch_cnt = len(opp_df[opp_df['아키타입'].fillna('').astype(str).str.strip() != ""])
                    
                    html_rows.append(f"""
                        <tr>
                            <td style="padding:8px; border:1px solid #dee2e6; text-align:left; font-weight:bold;">{opp}</td>
                            <td style="padding:8px; border:1px solid #dee2e6;">{g}</td>
                            <td style="padding:8px; border:1px solid #dee2e6;">{ow}</td>
                            <td style="padding:8px; border:1px solid #dee2e6;">{ol}</td>
                            <td style="padding:8px; border:1px solid #dee2e6; font-weight:bold;">{(ow/g*100):.2f}%</td>
                            <td style="padding:8px; border:1px solid #dee2e6;">{ofw:.2f}%</td>
                            <td style="padding:8px; border:1px solid #dee2e6;">{osw:.2f}%</td>
                            <td style="padding:8px; border:1px solid #dee2e6;">{(g/total_cnt*100):.2f}%</td>
                            <td style="padding:8px; border:1px solid #dee2e6;">{arch_cnt}</td>
                        </tr>
                    """)
                elif opp in st.session_state.metadata["opp_decks"]:
                    # 기록은 없지만 리스트에는 있는 덱 (회색 표시)
                    html_rows.append(f"""
                        <tr style="color:#adb5bd;">
                            <td style="padding:8px; border:1px solid #dee2e6; text-align:left;">{opp}</td>
                            <td style="padding:8px; border:1px solid #dee2e6;">0</td><td style="padding:8px; border:1px solid #dee2e6;">0</td>
                            <td style="padding:8px; border:1px solid #dee2e6;">0</td><td style="padding:8px; border:1px solid #dee2e6;">0%</td>
                            <td style="padding:8px; border:1px solid #dee2e6;">0%</td><td style="padding:8px; border:1px solid #dee2e6;">0%</td>
                            <td style="padding:8px; border:1px solid #dee2e6;">0%</td><td style="padding:8px; border:1px solid #dee2e6;">0</td>
                        </tr>
                    """)

            # 최종 테이블 결합
            table_content = "".join(html_rows)
            final_html = f"""
            <div style="overflow-x:auto;">
                <table style="width:100%; border-collapse: collapse; text-align: center; border: 1px solid #dee2e6; font-size: 14px;">
                    <thead>
                        <tr style="background-color: #fbbc04; color: black; font-weight: bold;">
                            <th style="padding:10px; border:1px solid #dee2e6;">Matchup</th>
                            <th style="padding:10px; border:1px solid #dee2e6;">Total</th>
                            <th style="padding:10px; border:1px solid #dee2e6;">W</th>
                            <th style="padding:10px; border:1px solid #dee2e6;">L</th>
                            <th style="padding:10px; border:1px solid #dee2e6; background-color: #e69138; color: white;">W%</th>
                            <th style="padding:10px; border:1px solid #dee2e6;">1st W%</th>
                            <th style="padding:10px; border:1px solid #dee2e6;">2nd W%</th>
                            <th style="padding:10px; border:1px solid #dee2e6;">Share</th>
                            <th style="padding:10px; border:1px solid #dee2e6;">Plus Arch</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_content}
                    </tbody>
                </table>
            </div>
            """
            # 이 부분이 핵심입니다: unsafe_allow_html=True
            st.markdown(final_html, unsafe_allow_html=True)
        else:
            st.info(f"'{sel_my}' 덱으로 기록된 경기 결과가 없습니다.")
    else:
        st.warning("분석할 데이터가 없습니다. Record 페이지에서 먼저 경기를 기록해 주세요.")
