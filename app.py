import streamlit as st
import pandas as pd
import os
import json

RECORD_FILE = "yugioh_records.csv"
META_FILE = "metadata_config.json"

st.set_page_config(page_title="26.03 Rating", layout="wide")

# ---------------- CSS ----------------

st.markdown("""
<style>

[data-testid="stTableIdxColumn"] {display:none;}

.styled-table{
    width:420px;
    border-collapse:collapse;
    font-size:13px;
    margin-bottom:30px;
}

.styled-table th{
    background:#e9c35b;
    padding:6px;
    border:1px solid #bbb;
}

.styled-table td{
    background:#f3f3f3;
    padding:6px;
    border:1px solid #ccc;
    text-align:center;
}

.win-val{
    color:#0050ff;
    font-weight:bold;
}

.loss-val{
    color:#ff0000;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------- 데이터 ----------------

def load_records():

    cols=[
        "날짜","선후공","결과",
        "내 덱","상대 덱"
    ]

    if os.path.exists(RECORD_FILE):
        df=pd.read_csv(RECORD_FILE)
        return df

    return pd.DataFrame(columns=cols)


def save_records(df):

    df.to_csv(RECORD_FILE,index=False)


# ---------------- 분석 계산 ----------------

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

    f_rate=(f_total/total*100) if total else 0
    s_rate=(s_total/total*100) if total else 0

    f_wrate=(f_w/f_total*100) if f_total else 0
    f_lrate=(f_l/f_total*100) if f_total else 0

    s_wrate=(s_w/s_total*100) if s_total else 0
    s_lrate=(s_l/s_total*100) if s_total else 0

    return {
        "total":total,
        "w":w,
        "l":l,
        "win_rate":win_rate,
        "f_total":f_total,
        "s_total":s_total,
        "f_rate":f_rate,
        "s_rate":s_rate,
        "f_w":f_w,
        "f_l":f_l,
        "s_w":s_w,
        "s_l":s_l,
        "f_wrate":f_wrate,
        "f_lrate":f_lrate,
        "s_wrate":s_wrate,
        "s_lrate":s_lrate
    }


# ---------------- 표 생성 ----------------

def render_table(title,stats):

    return f"""

<table class='styled-table'>

<tr><th colspan=4>{title}</th></tr>

<tr>
<th>Games</th>
<th>Win Rate</th>
<th>W</th>
<th>L</th>
</tr>

<tr>
<td>{stats["total"]}</td>
<td>{stats["win_rate"]:.2f}%</td>
<td class='win-val'>{stats["w"]}</td>
<td class='loss-val'>{stats["l"]}</td>
</tr>

<tr>
<th>1st</th>
<th>2nd</th>
<th>1st Rate</th>
<th>2nd Rate</th>
</tr>

<tr>
<td>{stats["f_total"]}</td>
<td>{stats["s_total"]}</td>
<td>{stats["f_rate"]:.2f}%</td>
<td>{stats["s_rate"]:.2f}%</td>
</tr>

<tr>
<th>1st Win</th>
<th>1st Lose</th>
<th>1st W%</th>
<th>1st L%</th>
</tr>

<tr>
<td class='win-val'>{stats["f_w"]}</td>
<td class='loss-val'>{stats["f_l"]}</td>
<td>{stats["f_wrate"]:.2f}%</td>
<td>{stats["f_lrate"]:.2f}%</td>
</tr>

<tr>
<th>2nd Win</th>
<th>2nd Lose</th>
<th>2nd W%</th>
<th>2nd L%</th>
</tr>

<tr>
<td class='win-val'>{stats["s_w"]}</td>
<td class='loss-val'>{stats["s_l"]}</td>
<td>{stats["s_wrate"]:.2f}%</td>
<td>{stats["s_lrate"]:.2f}%</td>
</tr>

</table>

"""


# ---------------- 페이지 ----------------

page=st.sidebar.radio("Menu",["Record","Analysis"])

df=load_records()

# ---------------- Record ----------------

if page=="Record":

    st.title("Record")

    new=st.data_editor(df,num_rows="dynamic")

    if st.button("Save"):
        save_records(new)
        st.success("Saved")


# ---------------- Analysis ----------------

else:

    st.title("Analysis")

    if df.empty:
        st.write("No Data")
        st.stop()

    # Overall

    st.markdown(
        render_table(
            "Overall Data",
            calc_stats(df)
        ),
        unsafe_allow_html=True
    )

    # 덱 선택

    my_deck=st.selectbox(
        "내 덱 선택",
        sorted(df["내 덱"].unique())
    )

    deck_df=df[df["내 덱"]==my_deck]

    st.markdown(
        render_table(
            f"{my_deck} 덱별 승률",
            calc_stats(deck_df)
        ),
        unsafe_allow_html=True
    )

    # 상대 덱별

    st.subheader("상대 덱별 승률")

    for opp in sorted(deck_df["상대 덱"].unique()):

        sub=deck_df[deck_df["상대 덱"]==opp]

        st.markdown(
            render_table(
                f"{opp}",
                calc_stats(sub)
            ),
            unsafe_allow_html=True
        )
