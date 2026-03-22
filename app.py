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
[data-testid="stTableIdxColumn"] { display: none !important; width: 0px !important; }
th.col_heading.level0.index_name { display: none !important; }

[data-testid="stDataFrameResizable"] div[role="grid"] div[role="row"] div:first-child svg {
    display: none !important;
}

div.row-widget.stDataFrame div[role="grid"] div[role="row"] div {
    text-align: center !important;
    font-size: 13px !important;
}

.analysis-wrapper { width: 420px; margin-left: 0; }

.styled-table {
    width: 100%;
    font-size: 13px;
    border-collapse: collapse;
    margin-bottom: 30px;
    table-layout: fixed;
    border: 1px solid #dee2e6;
}

.styled-table th, .styled-table td {
    text-align: center !important;
    border: 1px solid #dee2e6 !important;
    padding: 6px !important;
}

.styled-table th {
    background-color: #f9cb9c !important;
    color: #31333F !important;
    font-weight: bold !important;
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
                    if key not in saved:
                        saved[key] = default_meta[key]
                return saved
            except:
                pass

    return default_meta


def load_records():

    cols = [
        "NO.", "날짜", "선후공", "결과",
        "세트 전적", "점수",
        "내 덱", "상대 덱", "아키타입",
        "승패 요인", "특정 카드",
        "브릭", "실수", "비고"
    ]

    if os.path.exists(RECORD_FILE):

        try:
            df = pd.read_csv(RECORD_FILE, dtype=str).fillna("")

            for col in cols:
                if col not in df.columns:
                    df[col] = ""

            for col in ["브릭", "실수"]:
                df[col] = df[col].apply(lambda x: True if str(x).lower() in ['true', '1'] else False)

            return df[cols].reset_index(drop=True)

        except:
            pass

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

    f_df = calc_df[calc_df['선후공'] == '선']
    s_df = calc_df[calc_df['선후공'] == '후']

    f_total = len(f_df)
    s_total = len(s_df)

    f_wins = len(f_df[f_df['결과'] == '승'])
    s_wins = len(s_df[s_df['결과'] == '승'])

    return f"""
<table class="styled-table">

<tr><th colspan="5">{title}</th></tr>

<tr>
<th>Overall</th>
<th>Games</th>
<th>Win Rate</th>
<th>W</th>
<th>L</th>
</tr>

<tr>
<td>Result</td>
<td>{total}</td>
<td>{win_rate:.2f}%</td>
<td class="win-val">{wins}</td>
<td class="loss-val">{losses}</td>
</tr>

<tr>
<th>Coin</th>
<th>1st</th>
<th>2nd</th>
<th>1st Rate</th>
<th>2nd Rate</th>
</tr>

<tr>
<td>Result</td>
<td class="win-val">{f_total}</td>
<td class="loss-val">{s_total}</td>
<td class="win-val">{(f_total/total*100):.1f}%</td>
<td class="loss-val">{(s_total/total*100):.1f}%</td>
</tr>

<tr>
<th>1st</th>
<th>1st Win</th>
<th>1st Lose</th>
<th>1st W%</th>
<th>1st L%</th>
</tr>

<tr>
<td>Result</td>
<td class="win-val">{f_wins}</td>
<td class="loss-val">{f_total-f_wins}</td>
<td class="win-val">{(f_wins/f_total*100 if f_total>0 else 0):.1f}%</td>
<td class="loss-val">{(100-(f_wins/f_total*100) if f_total>0 else 0):.1f}%</td>
</tr>

<tr>
<th>2nd</th>
<th>2nd Win</th>
<th>2nd Lose</th>
<th>2nd W%</th>
<th>2nd L%</th>
</tr>

<tr>
<td>Result</td>
<td class="win-val">{s_wins}</td>
<td class="loss-val">{s_total-s_wins}</td>
<td class="win-val">{(s_wins/s_total*100 if s_total>0 else 0):.1f}%</td>
<td class="loss-val">{(100-(s_wins/s_total*100) if s_total>0 else 0):.1f}%</td>
</tr>

</table>
"""


# --- 4. 메인 로직 ---

if 'metadata' not in st.session_state:
    st.session_state.metadata = load_metadata()

if 'df' not in st.session_state:
    st.session_state.df = load_records()

page = st.sidebar.radio("메뉴", ["📊 Record", "📈 Analysis", "⚙️ Setting"])


# ---------------- Record ----------------

if page == "📊 Record":

    st.title("📊 Record")

    if st.button("➕ 새로운 경기 추가"):

        meta = st.session_state.metadata

        new_row = pd.DataFrame([{

            "NO.": str(len(st.session_state.df) + 1),
            "날짜": pd.Timestamp.now().strftime("%m.%d"),
            "선후공": "선",
            "결과": "승",
            "세트 전적": "OO",
            "점수": "",

            "내 덱": meta["my_decks"][0],
            "상대 덱": meta["opp_decks"][0],
            "아키타입": meta["archetypes"][0],
            "승패 요인": meta["win_loss_reasons"][0],
            "특정 카드": meta["target_cards"][0],

            "브릭": False,
            "실수": False,
            "비고": ""

        }])

        st.session_state.df = pd.concat(
            [st.session_state.df, new_row],
            ignore_index=True
        ).reset_index(drop=True)

        save_data(st.session_state.df)
        st.rerun()

    edited_df = st.data_editor(

        st.session_state.df,

        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        key="ygo_editor_v10",

        column_config={

            "NO.": st.column_config.TextColumn("NO.", width=45),

            "날짜": st.column_config.TextColumn("날짜", width=65),

            "선후공": st.column_config.SelectboxColumn(
                "선후공",
                options=["선", "후"],
                width=75
            ),

            "결과": st.column_config.SelectboxColumn(
                "결과",
                options=["승", "패"],
                width=65
            ),

            "세트 전적": st.column_config.SelectboxColumn(
                "세트",
                options=["OO", "OXO", "XOO", "XX", "XOX", "OXX"],
                width=60
            ),

            "점수": st.column_config.TextColumn(
                "점수",
                width=60
            ),

            "내 덱": st.column_config.SelectboxColumn(
                "내 덱",
                options=st.session_state.metadata.get("my_decks", []),
                width=100
            ),

            "상대 덱": st.column_config.SelectboxColumn(
                "상대 덱",
                options=st.session_state.metadata.get("opp_decks", []),
                width=100
            ),

            "아키타입": st.column_config.SelectboxColumn(
                "아키타입",
                options=st.session_state.metadata.get("archetypes", []),
                width=90
            ),

            "승패 요인": st.column_config.SelectboxColumn(
                "승패 요인",
                options=st.session_state.metadata.get("win_loss_reasons", []),
                width=100
            ),

            "특정 카드": st.column_config.SelectboxColumn(
                "특정 카드",
                options=st.session_state.metadata.get("target_cards", []),
                width=100
            ),

            "브릭": st.column_config.CheckboxColumn("브릭", width=85),

            "실수": st.column_config.CheckboxColumn("실수", width=85),

            "비고": st.column_config.TextColumn("비고", width=500)

        }
    )

    if not edited_df.equals(st.session_state.df):
        save_data(edited_df)
        st.rerun()

# ---------------- Analysis ----------------

elif page == "📈 Analysis":

    st.title("📈 Rating Analysis")

    df_ana = load_records()

    if not df_ana.empty:

        st.markdown('<div class="analysis-wrapper">', unsafe_allow_html=True)

        # ---------------- Overall ----------------

        st.markdown(
            render_styled_table("Overall Data", df_ana),
            unsafe_allow_html=True
        )

        # ---------------- Deck Winrate ----------------

        st.subheader("덱별 승률")

        sel_my = st.selectbox(
            "내 덱 선택",
            st.session_state.metadata["my_decks"],
            label_visibility="collapsed"
        )

        deck_df = df_ana[df_ana['내 덱'] == sel_my]

        st.markdown(
            render_styled_table(sel_my, deck_df),
            unsafe_allow_html=True
        )

        # ---------------- Matchup Analysis ----------------

        st.subheader("특정 매치업 분석")

        c1, c2 = st.columns(2)

        with c1:
            m_my = st.selectbox(
                "Use.Deck",
                st.session_state.metadata["my_decks"],
                label_visibility="collapsed",
                key="m_my"
            )

        with c2:
            m_opp = st.selectbox(
                "Opp.Deck",
                st.session_state.metadata["opp_decks"],
                label_visibility="collapsed",
                key="m_opp"
            )

        st.markdown(
            render_styled_table(
                "결과",
                df_ana[
                    (df_ana['내 덱'] == m_my) &
                    (df_ana['상대 덱'] == m_opp)
                ]
            ),
            unsafe_allow_html=True
        )

        # ---------------- Matchup Table ----------------

        st.subheader("Matchup Table")

        deck_filter = st.selectbox(
            "Matchup 기준 덱",
            st.session_state.metadata["my_decks"],
            key="matchup_deck"
        )

        df_match = df_ana[df_ana["내 덱"] == deck_filter]

        matchup_table = create_matchup_table(df_match)

        st.dataframe(
            matchup_table,
            use_container_width=True,
            hide_index=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Setting ----------------

else:

    st.title("⚙️ Setting")

    meta = st.session_state.metadata

    c1, c2 = st.columns(2)

    with c1:
        new_my = st.text_area(
            "내 덱 (쉼표 구분)",
            ", ".join(meta.get("my_decks", []))
        )

    with c2:
        new_opp = st.text_area(
            "상대 덱 (쉼표 구분)",
            ", ".join(meta.get("opp_decks", []))
        )

    c3, c4 = st.columns(2)

    with c3:
        new_reasons = st.text_area(
            "승패 요인 (쉼표 구분)",
            ", ".join(meta.get("win_loss_reasons", []))
        )

    with c4:
        new_arche = st.text_area(
            "아키타입 (쉼표 구분)",
            ", ".join(meta.get("archetypes", []))
        )

    c5, _ = st.columns(2)

    with c5:
        new_cards = st.text_area(
            "특정 카드 (쉼표 구분)",
            ", ".join(meta.get("target_cards", []))
        )

    if st.button("✅ 설정 저장"):

        st.session_state.metadata = {

            "my_decks": [x.strip() for x in new_my.split(",") if x.strip()],
            "opp_decks": [x.strip() for x in new_opp.split(",") if x.strip()],
            "win_loss_reasons": [x.strip() for x in new_reasons.split(",") if x.strip()],
            "archetypes": [x.strip() for x in new_arche.split(",") if x.strip()],
            "target_cards": [x.strip() for x in new_cards.split(",") if x.strip()]

        }

        with open(META_FILE, 'w', encoding='utf-8') as f:
            json.dump(
                st.session_state.metadata,
                f,
                ensure_ascii=False,
                indent=4
            )

        st.success("설정 저장 완료!")
        st.rerun()
