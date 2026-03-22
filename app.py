import streamlit as st
import pandas as pd
import os
import json

RECORD_FILE="yugioh_records.csv"
META_FILE="metadata_config.json"

st.set_page_config(page_title="26.03 Rating",layout="wide")

# ---------------- CSS ----------------

st.markdown("""
<style>

.win{
color:#0050ff;
font-weight:bold;
}

.loss{
color:#ff0000;
font-weight:bold;
}

table{
border-collapse:collapse;
width:420px;
margin-bottom:30px;
}

th{
background:#e6c56c;
border:1px solid #bbb;
padding:6px;
text-align:center;
}

td{
background:#f4f4f4;
border:1px solid #ccc;
padding:6px;
text-align:center;
}

</style>
""",unsafe_allow_html=True)

# ---------------- 기본 데이터 ----------------

meta_default={
"my_decks":[],
"opp_decks":[],
"archetypes":[],
"reasons":[],
"cards":[]
}

set_record=[
"OO","OXO","XOO",
"XX","XOX","OXX"
]

# ---------------- 데이터 로드 ----------------

def load_records():

    cols=[
    "날짜",
    "내 덱",
    "상대 덱",
    "아키타입",
    "선후공",
    "결과",
    "세트",
    "요인",
    "카드"
    ]

    if os.path.exists(RECORD_FILE):

        return pd.read_csv(RECORD_FILE)

    return pd.DataFrame(columns=cols)


def save_records(df):

    df.to_csv(RECORD_FILE,index=False)


def load_meta():

    if os.path.exists(META_FILE):

        with open(META_FILE,"r") as f:
            return json.load(f)

    return meta_default


def save_meta(meta):

    with open(META_FILE,"w") as f:
        json.dump(meta,f)


# ---------------- 색상 표시 ----------------

def color_val(v):

    if v in ["선","승","OO","OXO","XOO"]:
        return f"<span class='win'>{v}</span>"

    if v in ["후","패","XX","XOX","OXX"]:
        return f"<span class='loss'>{v}</span>"

    return v


# ---------------- 통계 계산 ----------------

def calc_stats(df):

    calc=df[df["결과"].isin(["승","패"])]

    total=len(calc)

    w=len(calc[calc["결과"]=="승"])
    l=len(calc[calc["결과"]=="패"])

    win_rate=(w/total*100) if total else 0

    first=calc[calc["선후공"]=="선"]
    second=calc[calc["선후공"]=="후"]

    f_total=len(first)
    s_total=len(second)

    f_w=len(first[first["결과"]=="승"])
    f_l=len(first[first["결과"]=="패"])

    s_w=len(second[second["결과"]=="승"])
    s_l=len(second[second["결과"]=="패"])

    return{
    "total":total,
    "w":w,
    "l":l,
    "rate":win_rate,
    "f_total":f_total,
    "s_total":s_total,
    "f_w":f_w,
    "f_l":f_l,
    "s_w":s_w,
    "s_l":s_l
    }


# ---------------- 표 생성 ----------------

def render_table(title,stats):

    return f"""

<table>

<tr><th colspan=4>{title}</th></tr>

<tr>
<th>Games</th>
<th>Win Rate</th>
<th>W</th>
<th>L</th>
</tr>

<tr>
<td>{stats["total"]}</td>
<td>{stats["rate"]:.2f}%</td>
<td class='win'>{stats["w"]}</td>
<td class='loss'>{stats["l"]}</td>
</tr>

<tr>
<th>1st</th>
<th>2nd</th>
<th>1st W</th>
<th>2nd W</th>
</tr>

<tr>
<td>{stats["f_total"]}</td>
<td>{stats["s_total"]}</td>
<td class='win'>{stats["f_w"]}</td>
<td class='win'>{stats["s_w"]}</td>
</tr>

</table>

"""

# ---------------- 메뉴 ----------------

page=st.sidebar.radio("Menu",["Record","Analysis","Setting"])

df=load_records()
meta=load_meta()

# ---------------- Record ----------------

if page=="Record":

    st.title("Match Record")

    col1,col2=st.columns(2)

    with col1:

        my_deck=st.selectbox(
        "내 덱",
        meta["my_decks"]
        )

        opp_deck=st.selectbox(
        "상대 덱",
        meta["opp_decks"]
        )

        archetype=st.selectbox(
        "아키타입",
        meta["archetypes"]
        )

        coin=st.selectbox(
        "선후공",
        ["선","후"]
        )

    with col2:

        result=st.selectbox(
        "결과",
        ["승","패"]
        )

        set_score=st.selectbox(
        "세트 전적",
        set_record
        )

        reason=st.selectbox(
        "승패 요인",
        meta["reasons"]
        )

        card=st.selectbox(
        "특정 카드",
        meta["cards"]
        )

    if st.button("기록 추가"):

        new_row={
        "날짜":pd.Timestamp.now(),
        "내 덱":my_deck,
        "상대 덱":opp_deck,
        "아키타입":archetype,
        "선후공":coin,
        "결과":result,
        "세트":set_score,
        "요인":reason,
        "카드":card
        }

        df=pd.concat([df,pd.DataFrame([new_row])],ignore_index=True)

        save_records(df)

        st.success("저장 완료")

    st.subheader("기록")

    if not df.empty:

        show=df.copy()

        for c in ["선후공","결과","세트"]:
            show[c]=show[c].apply(color_val)

        st.write(show.to_html(escape=False,index=False),unsafe_allow_html=True)


# ---------------- Analysis ----------------

elif page=="Analysis":

    st.title("Analysis")

    if df.empty:

        st.write("데이터 없음")
        st.stop()

    st.markdown(
    render_table(
    "Overall Data",
    calc_stats(df)
    ),
    unsafe_allow_html=True
    )

    st.subheader("덱별 승률")

    deck=st.selectbox(
    "내 덱 선택",
    df["내 덱"].dropna().unique()
    )

    sub=df[df["내 덱"]==deck]

    st.markdown(
    render_table(
    deck,
    calc_stats(sub)
    ),
    unsafe_allow_html=True
    )

    st.subheader("상대 덱별")

    for opp in sorted(sub["상대 덱"].dropna().unique()):

        opp_df=sub[sub["상대 덱"]==opp]

        st.markdown(
        render_table(
        opp,
        calc_stats(opp_df)
        ),
        unsafe_allow_html=True
        )


# ---------------- Setting ----------------

else:

    st.title("Setting")

    my=st.text_area(
    "내 덱 목록",
    "\n".join(meta["my_decks"])
    )

    opp=st.text_area(
    "상대 덱 목록",
    "\n".join(meta["opp_decks"])
    )

    arch=st.text_area(
    "아키타입",
    "\n".join(meta["archetypes"])
    )

    reason=st.text_area(
    "승패 요인",
    "\n".join(meta["reasons"])
    )

    cards=st.text_area(
    "특정 카드",
    "\n".join(meta["cards"])
    )

    if st.button("Setting 저장"):

        meta["my_decks"]=my.split("\n")
        meta["opp_decks"]=opp.split("\n")
        meta["archetypes"]=arch.split("\n")
        meta["reasons"]=reason.split("\n")
        meta["cards"]=cards.split("\n")

        save_meta(meta)

        st.success("저장 완료")
