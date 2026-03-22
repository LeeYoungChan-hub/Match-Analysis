import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정 - 요청하신 대로 이름을 Rating으로 설정
st.set_page_config(page_title="Rating", layout="wide")

st.title("📈 Rating 경기 기록 분석")
st.info("CSV 파일을 업로드하여 '2026.03 레이팅' 데이터를 분석하세요.")

# 파일 업로드
uploaded_file = st.file_uploader("2026.03 레이팅 - Record.csv 파일을 선택하세요", type="csv")

if uploaded_file is not None:
    # 데이터 로드 (첫 번째 행은 컬럼명, 두 번째 행은 영어/보조 설명이므로 0, 1행 처리 필요)
    # 2행부터 실제 데이터가 시작되므로 skiprows를 고려하거나 로드 후 필터링합니다.
    df = pd.read_csv(uploaded_file)
    
    # 두 번째 행(영문 설명 행) 및 데이터가 없는 행 제거
    # 'NO.' 컬럼이 숫자이거나 '경기'가 아닌 데이터만 남깁니다.
    df = df[pd.to_numeric(df['NO.'], errors='coerce').notnull()]
    
    # 1. 상단 요약 지표 (Metrics)
    total_games = len(df)
    wins = len(df[df['결과'] == '승'])
    win_rate = (wins / total_games) * 100 if total_games > 0 else 0
    
    # 실수(Mistake) 횟수 계산 (TRUE/FALSE 기반)
    mistakes = df['실수'].astype(str).str.upper().value_counts().get('TRUE', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 경기 수", f"{total_games}회")
    col2.metric("총 승리", f"{wins}승")
    col3.metric("전체 승률", f"{win_rate:.1f}%")
    col4.metric("총 실수 횟수", f"{mistakes}회")

    st.divider()

    # 2. 시각화 레이아웃
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("선후공별 승률")
        # 선후공에 따른 승률 계산
        turn_stats = df.groupby(['선후공', '결과']).size().unstack(fill_value=0)
        if '승' in turn_stats.columns:
            fig_turn = px.bar(turn_stats, barmode='group', title="선/후공 승패 분포",
                             color_discrete_map={'승': '#636EFA', '패': '#EF553B'})
            st.plotly_chart(fig_turn, use_container_width=True)
        else:
            st.write("승리 데이터가 충분하지 않습니다.")

    with col_right:
        st.subheader("상대 덱 분포 (Top 10)")
        opp_counts = df['상대 덱'].value_counts().head(10)
        fig_opp = px.pie(values=opp_counts.values, names=opp_counts.index, hole=0.4)
        st.plotly_chart(fig_opp, use_container_width=True)

    # 3. 상세 분석 섹션
    st.subheader("아키타입/상대 덱 상세 통계")
    
    # 상대 덱별 승률표
    summary = df.groupby('상대 덱')['결과'].value_counts().unstack(fill_value=0)
    if '승' not in summary.columns: summary['승'] = 0
    if '패' not in summary.columns: summary['패'] = 0
    
    summary['총합'] = summary['승'] + summary['패']
    summary['승률(%)'] = (summary['승'] / summary['총합'] * 100).round(1)
    summary = summary.sort_values(by='총합', ascending=False)
    
    st.table(summary[['총합', '승', '패', '승률(%)']])

    # 4. 특이사항 확인 (실수나 비고가 적힌 경기)
    with st.expander("복기 필요한 경기 (실수 혹은 비고 있음)"):
        note_df = df[(df['실수'].astype(str).str.upper() == 'TRUE') | (df['비고'].notna())]
        st.write(note_df[['NO.', '상대 덱', '결과', '실수', '비고']])

else:
    st.warning("파일을 업로드하면 대시보드가 활성화됩니다.")
