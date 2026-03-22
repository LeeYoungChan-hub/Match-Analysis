import streamlit as st
import pandas as pd
import os
import json

# --- 1. 기본 설정 및 파일 경로 ---
RECORD_FILE = 'yugioh_records.csv'
META_FILE = 'metadata_config.json'

st.set_page_config(page_title="YGO Rating Analysis", layout="wide")

# --- 2. 디자인 CSS ---
st.markdown("""
<style>

/* 시스템 인덱스 숨기기 */
[data-testid="stTableIdxColumn"] { display:none !important; }
th.col_heading.level0.index_name { display:none !important; }

/* Record 표 텍스트 */
div.row-widget.stDataFrame div[role="grid"] div[role="row"] div{
    text-align:center !important;
    font-size:13px !important;
}

/* Record 색상 */
div[data-testid="stDataFrame"] div[role="gridcell"]:has-text("선"),
div[data-testid="stDataFrame"] div[role="gridcell"]:has-text("승"),
div[data-testid="stDataFrame"] div[role="gridcell"]:has-text("OO"),
div[data-testid="stDataFrame"] div[role="gridcell"]:has-text("OXO"),
div[data-testid="stDataFrame"] div[role="gridcell"]:has-text("XOO"){
    color:#0000ff !important;
    font-weight:bold;
}

div[data-testid="stDataFrame"] div[role="gridcell"]:has-text("후"),
div[data-testid="stDataFrame"] div[role="gridcell"]:has-text("패"),
div[data-testid="stDataFrame"] div[role="gridcell"]:has-text("XX"),
div[data-testid="stDataFrame"] div[role="gridcell"]:has-text("XOX"),
div[data-testid="stDataFrame"] div[role="gridcell"]:has-text("OXX"){
    color:#ff0000 !important;
    font-weight:bold;
}

/* 실수 체크 빨간색 */
div[data-testid="stDataFrame"] input[type="checkbox"]:checked{
    accent-color:red !important;
}

/* 분석 표 */
.analysis-wrapper{ width:420px; }

.styled-table{
    width:100%;
    font-size:13px;
    border-collapse:collapse;
    margin-bottom:30px;
    table-layout:fixed;
    border:1px solid #dee2e6;
}

.styled-table th,
.styled-table td{
    text-align:center !important;
    border:1px solid #dee2e6 !important;
    padding:6px !important;
}

.styled-table th{
    background-color:#f9cb9c !important;
    font-weight:bold;
}

.win-val{ color:#0000ff !important; font-weight:bold; }
.loss-val{ color:#ff0000 !important; font-weight:bold; }

</style>
""", unsafe_allow_html=True)

# --- 데이터 로직 ---
def load_metadata():
    default_meta = {
        "my_decks": ["KT", "Ennea", "Maliss", "Tenpai"],
        "opp_decks": ["KT", "Ennea", "Maliss", "Tenpai", "Labrynth", "Branded"],
        "archetypes": ["운영", "전개", "미드레인지", "함떡", "기타"],
        "win_loss_reasons": ["상대 패", "자신 실력", "특정 카드", "핸드 말림", "기타"],
        "target_cards": ["증식의 G", "하루 우라라", "무한포영", "니비루", "드롤"]
    }

    if os.path.exists(META_FILE):
        with open(META_FILE,'r',encoding='utf-8') as f:
            try:
                saved=json.load(f)
                for key in default_meta:
                    if key not in saved:
                        saved[key]=default_meta[key]
                return saved
            except:
                pass

    return default_meta


def load_records():

    cols=[
    "NO.","날짜","선후공","결과","세트 전적","점수",
    "내 덱","상대 덱","아키타입","승패 요인",
    "특정 카드","브릭","실수","비고"
    ]

    if os.path.exists(RECORD_FILE):

        try:
            df=pd.read_csv(RECORD_FILE,dtype=str).fillna("")

            for col in cols:
                if col not in df.columns:
                    df[col]=""

            for col in ["브릭","실수"]:
                df[col]=df[col].apply(lambda x:True if str(x).lower() in ['true','1'] else False)

            return df[cols].reset_index(drop=True)

        except:
            pass

    return pd.DataFrame(columns=cols)


def save_data(df):
    df.to_csv(RECORD_FILE,index=False,encoding='utf-8-sig')
    st.session_state.df=df.reset_index(drop=True)


# --- 분석 표 ---
def render_styled_table(title,df):

    calc=df[df["결과"].isin(["승","패"])]

    total=len(calc)

    if total==0:
        return "<table class='styled-table'><tr><td>No Data</td></tr></table>"

    wins=len(calc[calc["결과"]=="승"])
    losses=len(calc[calc["결과"]=="패"])

    rate=wins/total*100

    first=calc[calc["선후공"]=="선"]
    second=calc[calc["선후공"]=="후"]

    f_total=len(first)
    s_total=len(second)

    f_win=len(first[first["결과"]=="승"])
    s_win=len(second[second["결과"]=="승"])

    return f"""
<table class="styled-table">

<tr><th colspan=5>{title}</th></tr>

<tr>
<th>Overall</th><th>Games</th><th>Win Rate</th><th>W</th><th>L</th>
</tr>

<tr>
<td>Result</td>
<td>{total}</td>
<td>{rate:.2f}%</td>
<td class="win-val">{wins}</td>
<td class="loss-val">{losses}</td>
</tr>

<tr>
<th>Coin</th><th>1st</th><th>2nd</th><th>1st Rate</th><th>2nd Rate</th>
</tr>

<tr>
<td>Result</td>
<td class="win-val">{f_total}</td>
<td class="loss-val">{s_total}</td>
<td>{(f_total/total*100):.1f}%</td>
<td>{(s_total/total*100):.1f}%</td>
</tr>

</table>
"""


# --- 세션 ---
if 'metadata' not in st.session_state:
    st.session_state.metadata=load_metadata()

if 'df' not in st.session_state:
    st.session_state.df=load_records()

page=st.sidebar.radio("메뉴",["📊 Record","📈 Analysis","⚙️ Setting"])


# --- Record ---
if page=="📊 Record":

    st.title("📊 Record")

    if st.button("➕ 새로운 경기 추가"):

        meta=st.session_state.metadata

        new_row=pd.DataFrame([{
        "NO.":str(len(st.session_state.df)+1),
        "날짜":pd.Timestamp.now().strftime("%m.%d"),
        "선후공":"선",
        "결과":"승",
        "세트 전적":"OO",
        "점수":"",
        "내 덱":meta["my_decks"][0],
        "상대 덱":meta["opp_decks"][0],
        "아키타입":meta["archetypes"][0],
        "승패 요인":meta["win_loss_reasons"][0],
        "특정 카드":meta["target_cards"][0],
        "브릭":False,
        "실수":False,
        "비고":""
        }])

        st.session_state.df=pd.concat([st.session_state.df,new_row],ignore_index=True)

        save_data(st.session_state.df)

        st.rerun()

    edited_df=st.data_editor(
        st.session_state.df,
        use_container_width=True,
        hide_index=True,
        key="editor",
        column_config={

        "NO.":st.column_config.TextColumn("NO.",width=45),
        "날짜":st.column_config.TextColumn("날짜",width=65),
        "선후공":st.column_config.SelectboxColumn("선후공",options=["선","후"],width=65),
        "결과":st.column_config.SelectboxColumn("결과",options=["승","패"],width=65),
        "세트 전적":st.column_config.SelectboxColumn("세트",options=["OO","OXO","XOO","XX","XOX","OXX"],width=85),
        "점수":st.column_config.TextColumn("점수",width=65),
        "내 덱":st.column_config.SelectboxColumn("내 덱",options=st.session_state.metadata["my_decks"],width=100),
        "상대 덱":st.column_config.SelectboxColumn("상대 덱",options=st.session_state.metadata["opp_decks"],width=100),
        "아키타입":st.column_config.SelectboxColumn("아키타입",options=st.session_state.metadata["archetypes"],width=90),
        "승패 요인":st.column_config.SelectboxColumn("승패 요인",options=st.session_state.metadata["win_loss_reasons"],width=100),
        "특정 카드":st.column_config.SelectboxColumn("특정 카드",options=st.session_state.metadata["target_cards"],width=100),
        "브릭":st.column_config.CheckboxColumn("브릭",width=85),
        "실수":st.column_config.CheckboxColumn("실수",width=85),
        "비고":st.column_config.TextColumn("비고",width=400)
        }
    )

    if not edited_df.equals(st.session_state.df):

        save_data(edited_df)

        st.rerun()


# --- Analysis ---
elif page=="📈 Analysis":

    st.title("📈 Rating Analysis")

    df=load_records()

    st.markdown(render_styled_table("Overall Data",df),unsafe_allow_html=True)


# --- Setting ---
else:

    st.title("⚙️ Setting")

    meta=st.session_state.metadata

    new_my=st.text_area("내 덱",",".join(meta["my_decks"]))
    new_opp=st.text_area("상대 덱",",".join(meta["opp_decks"]))
    new_arche=st.text_area("아키타입",",".join(meta["archetypes"]))
    new_reason=st.text_area("승패 요인",",".join(meta["win_loss_reasons"]))
    new_cards=st.text_area("특정 카드",",".join(meta["target_cards"]))

    if st.button("저장"):

        st.session_state.metadata={

        "my_decks":[x.strip() for x in new_my.split(",") if x.strip()],
        "opp_decks":[x.strip() for x in new_opp.split(",") if x.strip()],
        "archetypes":[x.strip() for x in new_arche.split(",") if x.strip()],
        "win_loss_reasons":[x.strip() for x in new_reason.split(",") if x.strip()],
        "target_cards":[x.strip() for x in new_cards.split(",") if x.strip()]

        }

        with open(META_FILE,'w',encoding='utf-8') as f:
            json.dump(st.session_state.metadata,f,ensure_ascii=False,indent=4)

        st.success("저장 완료")

        st.rerun()
