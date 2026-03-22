import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="26.03 Rating", layout="wide")

# --- 2. CSS ---
st.markdown("""
<style>

[data-testid="stTableIdxColumn"] {display:none}
th.col_heading.level0.index_name {display:none}

div[data-testid="stDataFrame"] div[role="gridcell"]{
text-align:center !important;
font-size:13px !important;
}

div[data-testid="stDataFrame"] div:has-text("선"),
div[data-testid="stDataFrame"] div:has-text("승"),
div[data-testid="stDataFrame"] div:has-text("OO"),
div[data-testid="stDataFrame"] div:has-text("OXO"),
div[data-testid="stDataFrame"] div:has-text("XOO"){
color:#0066ff;
font-weight:bold;
}

div[data-testid="stDataFrame"] div:has-text("후"),
div[data-testid="stDataFrame"] div:has-text("패"),
div[data-testid="stDataFrame"] div:has-text("XX"),
div[data-testid="stDataFrame"] div:has-text("XOX"),
div[data-testid="stDataFrame"] div:has-text("OXX"){
color:#ff0000;
font-weight:bold;
}

</style>
""", unsafe_allow_html=True)


# --- Metadata ---
def load_metadata():

    default_meta={
        "my_decks":["KT","Ennea","Maliss","Tenpai"],
        "opp_decks":["KT","Ennea","Maliss","Tenpai"],
        "archetypes":["전개","미드","운영","함떡"],
        "reasons":["상대 패","내 실력","핸드 말림","특정 카드"],
        "cards":["G","우라라","포영","니비루","드롤"]
    }

    if os.path.exists(META_FILE):
        with open(META_FILE,'r',encoding='utf-8') as f:
            try:
                data=json.load(f)
                return data
            except:
                pass

    return default_meta


def load_records():

    cols=[
    "NO.","날짜","선후공","결과","세트 전적","점수",
    "내 덱","상대 덱","아키타입",
    "승패 요인","특정 카드",
    "브릭","실수","비고"
    ]

    if os.path.exists(RECORD_FILE):

        df=pd.read_csv(RECORD_FILE,dtype=str).fillna("")

        for c in cols:
            if c not in df.columns:
                df[c]=""

        return df[cols]

    return pd.DataFrame(columns=cols)


def save_records(df):

    df.to_csv(RECORD_FILE,index=False,encoding='utf-8-sig')



# --- 세션 ---
if "meta" not in st.session_state:
    st.session_state.meta=load_metadata()

if "df" not in st.session_state:
    st.session_state.df=load_records()


page=st.sidebar.radio("메뉴",["Record","Analysis","Setting"])



# ------------------------
# Record
# ------------------------
if page=="Record":

    st.title("Record")

    if st.button("경기 추가"):

        new_row={
        "NO.":len(st.session_state.df)+1,
        "날짜":"",
        "선후공":"선",
        "결과":"승",
        "세트 전적":"OO",
        "점수":"",
        "내 덱":st.session_state.meta["my_decks"][0],
        "상대 덱":st.session_state.meta["opp_decks"][0],
        "아키타입":st.session_state.meta["archetypes"][0],
        "승패 요인":st.session_state.meta["reasons"][0],
        "특정 카드":st.session_state.meta["cards"][0],
        "브릭":False,
        "실수":False,
        "비고":""
        }

        st.session_state.df=pd.concat(
            [st.session_state.df,pd.DataFrame([new_row])],
            ignore_index=True
        )


    edited=st.data_editor(

        st.session_state.df,

        use_container_width=True,

        hide_index=True,

        column_config={

        "NO.":st.column_config.TextColumn(width=40),

        "날짜":st.column_config.TextColumn(width=70),

        "선후공":st.column_config.SelectboxColumn(
        options=["선","후"],
        width=60
        ),

        "결과":st.column_config.SelectboxColumn(
        options=["승","패"],
        width=60
        ),

        "세트 전적":st.column_config.SelectboxColumn(
        options=["OO","OXO","XOO","XX","XOX","OXX"],
        width=80
        ),

        "점수":st.column_config.TextColumn(width=60),

        "내 덱":st.column_config.SelectboxColumn(
        options=st.session_state.meta["my_decks"]
        ),

        "상대 덱":st.column_config.SelectboxColumn(
        options=st.session_state.meta["opp_decks"]
        ),

        "아키타입":st.column_config.SelectboxColumn(
        options=st.session_state.meta["archetypes"]
        ),

        "승패 요인":st.column_config.SelectboxColumn(
        options=st.session_state.meta["reasons"]
        ),

        "특정 카드":st.column_config.SelectboxColumn(
        options=st.session_state.meta["cards"]
        ),

        "브릭":st.column_config.CheckboxColumn(),

        "실수":st.column_config.CheckboxColumn(),

        "비고":st.column_config.TextColumn(width=400)

        }

    )


    if not edited.equals(st.session_state.df):

        st.session_state.df=edited

        save_records(edited)

        st.rerun()



# ------------------------
# Analysis (원래 코드 그대로 유지)
# ------------------------
elif page=="Analysis":

    st.title("Analysis")

    df=load_records()

    st.write(df)



# ------------------------
# Setting
# ------------------------
else:

    st.title("Setting")

    meta=st.session_state.meta

    my_decks=st.text_area("내 덱",",".join(meta["my_decks"]))
    opp_decks=st.text_area("상대 덱",",".join(meta["opp_decks"]))
    arche=st.text_area("아키타입",",".join(meta["archetypes"]))
    reasons=st.text_area("승패 요인",",".join(meta["reasons"]))
    cards=st.text_area("특정 카드",",".join(meta["cards"]))


    if st.button("저장"):

        new_meta={

        "my_decks":[x.strip() for x in my_decks.split(",") if x.strip()],
        "opp_decks":[x.strip() for x in opp_decks.split(",") if x.strip()],
        "archetypes":[x.strip() for x in arche.split(",") if x.strip()],
        "reasons":[x.strip() for x in reasons.split(",") if x.strip()],
        "cards":[x.strip() for x in cards.split(",") if x.strip()]

        }

        with open(META_FILE,"w",encoding="utf-8") as f:
            json.dump(new_meta,f,ensure_ascii=False,indent=4)

        st.session_state.meta=new_meta

        st.success("저장 완료")

        st.rerun()
