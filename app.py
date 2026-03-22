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
<tr><th>Overall</th><th>Games</th><th>Win Rate</th><th>W</th><th>L</th></tr>
<tr><td>Result</td><td>{total}</td><td>{win_rate:.2f}%</td><td class="win-val">{wins}</td><td class="loss-val">{losses}</td></tr>
<tr><th>Coin</th><th>1st</th><th>2nd</th><th>1st Rate</th><th>2nd Rate</th></tr>
<tr><td>Result</td><td class="win-val">{f_total}</td><td class="loss-val">{s_total}</td><td class="win-val">{(f_total/total*100):.1f}%</td><td class="loss-val">{(s_total/total*100):.1f}%</td></tr>
<tr><th>1st</th><th>1st Win</th><th>1st Lose</th><th>1st W%</th><th>1st L%</th></tr>
<tr><td>Result</td><td class="win-val">{f_wins}</td><td class="loss-val">{f_total-f_wins}</td><td class="win-val">{(f_wins/f_total*100 if f_total>0 else 0):.1f}%</td><td class="loss-val">{(100-(f_wins/f_total*100) if f_total>0 else 0):.1f}%</td></tr>
<tr><th>2nd</th><th>2nd Win</th><th>2nd Lose</th><th>2nd W%</th><th>2nd L%</th></tr>
<tr><td>Result</td><td class="win-val">{s_wins}</td><td class="loss-val">{s_total-s_wins}</td><td class="win-val">{(s_wins/s_total*100 if s_total>0 else 0):.1f}%</td><td class="loss-val">{(100-(s_wins/s_total*100) if s_total>0 else 0):.1f}%</td></tr>
</table>
"""


# ⭐ Matchup Table 함수 (위치 이동됨)

def create_matchup_table(df):

    df = df[df['결과'].isin(['승','패'])]

    total_games = len(df)

    rows = []

    for opp in sorted(df['상대 덱'].unique()):

        sub = df[df['상대 덱'] == opp]

        total = len(sub)
        w = len(sub[sub['결과']=='승'])
        l = len(sub[sub['결과']=='패'])

        win_rate = (w/total*100) if total else 0

        first = sub[sub['선후공']=='선']
        second = sub[sub['선후공']=='후']

        first_w = len(first[first['결과']=='승'])
        second_w = len(second[second['결과']=='승'])

        first_rate = (first_w/len(first)*100) if len(first)>0 else 0
        second_rate = (second_w/len(second)*100) if len(second)>0 else 0

        share = (total/total_games*100) if total_games else 0

        arch = sub['아키타입'].iloc[0] if len(sub)>0 else ""

        rows.append({
            "Matchup": opp,
            "Total": total,
            "W": w,
            "L": l,
            "W%": round(win_rate,2),
            "1stW%": round(first_rate,2),
            "2ndW%": round(second_rate,2),
            "Share": round(share,1),
            "Arch": arch
        })

    df_out = pd.DataFrame(rows)

    if not df_out.empty:
        df_out = df_out.sort_values("W%", ascending=False)

    return df_out


# --- 4. 메인 로직 ---
