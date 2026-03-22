```python
import streamlit as st
import pandas as pd
import os
import json

# ---------------- 기본 설정 ----------------

RECORD_FILE = "yugioh_records.csv"
META_FILE = "metadata_config.json"

st.set_page_config(page_title="26.03 Rating", layout="wide")

# ---------------- CSS ----------------

st.markdown("""
<style>

[data-testid="stTableIdxColumn"] {display:none;}
th.col_heading.level0.index_name {display:none;}

.analysis-wrapper{
    width:420px;
}

.styled-table{
    width:100%;
    border-collapse:collapse;
    font-size:13px;
    margin-bottom:30px;
}

.styled-table th{
    background:#f9cb9c;
    padding:6px;
    border:1px solid #ddd;
}

.styled-table td{
    padding:6px;
    border:1px solid #ddd;
    text-align:center;
}

.win-val{
    color:#0000ff;
    font-weight:bold;
}

.loss-val{
    color:#ff0000;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------- 데이터 로드 ----------------


def load_metadata():

    default = {
        "my_decks": ["KT","Ennea","Maliss","Tenpai"],
        "opp_decks": ["KT","Ennea","Maliss","Tenpai","Labrynth","Branded"],
        "archetypes": ["운영","전개","미드레인지","함떡","기타"],
        "win_loss_reasons": ["상대 패","자신 실력","특정 카드","핸드 말림","기타"],
        "target_cards": ["증식의 G","하루 우라라","무한포영","니비루","드롤"]
    }

    if os.path.exists(META_FILE):
        with open(META_FILE,"r",encoding="utf-8") as f:
            try:
                data=json.load(f)
                for k in default:
                    if k not in data:
                        data[k]=default[k]
                return data
            except:
                return default

    return default


def load_records():

    cols=[
        "NO.","날짜","선후공","결과",
        "세트 전적","점수",
        "내 덱","상대 덱","아키타입",
        "승패 요인","특정 카드",
        "브릭","실수","비고"
    ]

    if os.path.exists(RECORD_FILE):

        try:
            df=pd.read_csv(RECORD_FILE,dtype=str).fillna("")

            for c in cols:
                if c not in df.columns:
                    df[c]=""

            for c in ["브릭","실수"]:
                df[c]=df[c].apply(lambda x:True if str(x).lower() in ["true","1"] else False)

            return df[cols].reset_index(drop=True)

        except:
            pass

    return pd.DataFrame(columns=cols)


def save_data(df):

    df.to_csv(RECORD_FILE,index=False,encoding="utf-8-sig")
    st.session_state.df=df.reset_index(drop=True)


# ---------------- 분석 테이블 ----------------


def render_styled_table(title,df):

    calc=df[df["결과"].isin(["승","패"])]
    total=len(calc)

    if total==0:
        return f"<table class='styled-table'><tr><th>{title}</th></tr><tr><td>데이터 없음</td></tr></table>"

    w=len(calc[calc["결과"]=="승"])
    l=len(calc[calc["결과"]=="패"])

    win_rate=(w/total*100)

    first=calc[calc["선후공"]=="선"]
    second=calc[calc["선후공"]=="후"]

    f_total=len(first)
    s_total=len(second)

    f_w=len(first[first["결과"]=="승"])
    s_w=len(second[second["결과"]=="승"])

    return f"""
<table class='styled-table'>

<tr><th colspan=5>{title}</th></tr>

<tr>
<th>Games</th>
<th>WinRate</th>
<th>W</th>
<th>L</th>
<th>-</th>
</tr>

<tr>
<td>{total}</td>
<td>{win_rate:.2f}%</td>
<td class='win-val'>{w}</td>
<td class='loss-val'>{l}</td>
<td>-</td>
</tr>

<tr>
<th>1st</th>
<th>2nd</th>
<th>1st W%</th>
<th>2nd W%</th>
<th>-</th>
</tr>

<tr>
<td>{f_total}</td>
<td>{s_total}</td>
<td>{(f_w/f_total*100 if f_total else 0):.1f}%</td>
<td>{(s_w/s_total*100 if s_total else 0):.1f}%</td>
<td>-</td>
</tr>

</table>
"""


# ---------------- Matchup Table ----------------


def create_matchup_table(df):

    df=df[df["결과"].isin(["승","패"])]

    total_games=len(df)

    rows=[]

    for opp in sorted(df["상대 덱"].unique()):

        sub=df[df["상대 덱"]==opp]

        total=len(sub)

        w=len(sub[sub["결과"]=="승"])
        l=len(sub[sub["결과"]=="패"])

        win_rate=(w/total*100) if total else 0

        first=sub[sub["선후공"]=="선"]
        second=sub[sub["선후공"]=="후"]

        first_w=len(first[first["결과"]=="승"])
        second_w=len(second[second["결과"]=="승"])

        first_rate=(first_w/len(first)*100) if len(first) else 0
        second_rate=(second_w/len(second)*100) if len(second) else 0

        share=(total/total_games*100) if total_games else 0

        arch=sub["아키타입"].iloc[0] if len(sub)>0 else ""

        rows.append({
            "Matchup":opp,
            "Total":total,
            "W":w,
            "L":l,
            "W%":round(win_rate,2),
            "1stW%":round(first_rate,2),
            "2ndW%":round(second_rate,2),
            "Share":round(share,1),
            "Arch":arch
        })

    df_out=pd.DataFrame(rows)

    if not df_out.empty:
        df_out=df_out.sort_values("W%",ascending=False)

    return df_out


# ---------------- 세션 초기화 ----------------

if "metadata" not in st.session_state:
    st.session_state.metadata=load_metadata()

if "df" not in st.session_state:
    st.session_state.df=load_records()

page=st.sidebar.radio("메뉴",["📊 Record","📈 Analysis","⚙️ Setting"])

# ---------------- Record ----------------

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

        st.session_state.df=pd.concat(
            [st.session_state.df,new_row],
            ignore_index=True
        )

        save_data(st.session_state.df)
        st.rerun()

    edited=st.data_editor(
        st.session_state.df,
        use_container_width=True,
        hide_index=True
    )

    if not edited.equals(st.session_state.df):

        save_data(edited)
        st.rerun()

# ---------------- Analysis ----------------

elif page=="📈 Analysis":

    st.title("📈 Rating Analysis")

    df=load_records()

    if not df.empty:

        st.markdown('<div class="analysis-wrapper">',unsafe_allow_html=True)

        st.markdown(render_styled_table("Overall",df),unsafe_allow_html=True)

        st.subheader("덱 승률")

        my=st.selectbox("내 덱",st.session_state.metadata["my_decks"])

        deck_df=df[df["내 덱"]==my]

        st.markdown(render_styled_table(my,deck_df),unsafe_allow_html=True)

        st.subheader("Matchup Table")

        deck_filter=st.selectbox(
            "기준 덱",
            st.session_state.metadata["my_decks"],
            key="match"
        )

        df_match=df[df["내 덱"]==deck_filter]

        table=create_matchup_table(df_match)

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True
        )

        st.markdown('</div>',unsafe_allow_html=True)

# ---------------- Setting ----------------

else:

    st.title("⚙️ Setting")

    meta=st.session_state.metadata

    my=st.text_area("내 덱",",".join(meta["my_decks"]))
    opp=st.text_area("상대 덱",",".join(meta["opp_decks"]))
    arch=st.text_area("아키타입",",".join(meta["archetypes"]))
    reason=st.text_area("승패 요인",",".join(meta["win_loss_reasons"]))
    cards=st.text_area("특정 카드",",".join(meta["target_cards"]))

    if st.button("저장"):

        st.session_state.metadata={
            "my_decks":[x.strip() for x in my.split(",") if x.strip()],
            "opp_decks":[x.strip() for x in opp.split(",") if x.strip()],
            "archetypes":[x.strip() for x in arch.split(",") if x.strip()],
            "win_loss_reasons":[x.strip() for x in reason.split(",") if x.strip()],
            "target_cards":[x.strip() for x in cards.split(",") if x.strip()]
        }

        with open(META_FILE,"w",encoding="utf-8") as f:
            json.dump(st.session_state.metadata,f,ensure_ascii=False,indent=4)

        st.success("저장 완료")
        st.rerun()
```
