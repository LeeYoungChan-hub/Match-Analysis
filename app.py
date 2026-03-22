import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# --- 파일 경로 설정 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating System", layout="wide")

# 🔥 [추가] 표의 줄 3개와 연필 아이콘을 강제로 숨기는 CSS
hide_ui_style = """
    <style>
    /* 표 왼쪽의 행 번호/핸들 숨기기 */
    [data-testid="stTableIdxColumn"] {
        display: none;
    }
    /* 셀 수정 시 나타나는 연필 아이콘 숨기기 */
    .st-ae svg {
        display: none !important;
    }
    /* 데이터 에디터 하단의 추가/삭제 툴바를 더 깔끔하게 (선택 사항) */
    [data-testid="stDataEditorToolbar"] {
        display: none;
    }
    </style>
"""
st.markdown(hide_ui_style, unsafe_allow_html=True)

# --- 이하 기존 코드 동일 ---
# (중략: load_metadata, load_records 함수 등...)

# [Rating 입력창 부분에서도 확인]
edited_df = st.data_editor(
    st.session_state.df, 
    use_container_width=True, 
    num_rows="dynamic",
    hide_index=True,  # 기본 옵션도 유지
    key="rating_editor_final",
    column_config={
        # (기존 column_config 내용...)
    }
)
