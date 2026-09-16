import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일: 여덟 자리 숫자 → 날짜
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 여러 장르가 "|"로 적혀 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("기타")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 숫자형 열 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


df = load_data()

st.caption(f"분석 대상 영화: {len(df):,}편")


# ==================================================
# 그래프 1. 장르별 영화 편수
# ==================================================
st.divider()

st.header("그래프 1. 장르별 영화 편수")

genre_count = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화 편수"]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.5,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

fig1.update_layout(
    legend_title_text="장르",
    margin=dict(t=60, b=20, l=20, r=20)
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.markdown("### 이 그래프로 알 수 있는 것")

st.text_area(
    "이 그래프로 알 수 있는 것",
    value="",
    placeholder="여기에 이 그래프를 통해 알 수 있는 내용을 한 문장으로 작성하세요.",
    height=80,
    key="graph1_explanation"
)


# ==================================================
# 그래프 2. 장르별 영화 관객 트리맵
# ==================================================
st.divider()

st.header("그래프 2. 장르별 영화 관객 트리맵")

treemap_df = df[
    df["genre"].notna()
    & df["movieNm"].notna()
    & df["total_audi"].notna()
].copy()

treemap_df = treemap_df[treemap_df["total_audi"] > 0]

fig2 = px.treemap(
    treemap_df,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화의 총 관객 규모"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    margin=dict(t=60, b=20, l=20, r=20)
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.markdown("### 이 그래프로 알 수 있는 것")

st.text_area(
    "이 그래프로 알 수 있는 것",
    value="",
    placeholder="여기에 이 그래프를 통해 알 수 있는 내용을 한 문장으로 작성하세요.",
    height=80,
    key="graph2_explanation"
)


# ==================================================
# 그래프 3. 총 관객 히스토그램
# ==================================================
st.divider()

st.header("그래프 3. 영화별 총 관객 분포")

hist_df = df[
    df["movieNm"].notna()
    & df["total_audi"].notna()
    & (df["total_audi"] >= 0)
].copy()

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 분포",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수"
    }
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수",
    margin=dict(t=60, b=20, l=20, r=20)
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# --------------------------------------------------
# 히스토그램에서 가장 많이 몰린 구간 계산
# --------------------------------------------------
counts, bin_edges = pd.cut(
    hist_df["total_audi"],
    bins=20,
    include_lowest=True,
    retbins=True
)

bin_counts = counts.value_counts().sort_index()

most_common_bin = bin_counts.idxmax()

lower_bound = most_common_bin.left
upper_bound = most_common_bin.right


# --------------------------------------------------
# 총 관객이 가장 많은 영화 계산
# --------------------------------------------------
max_movie = hist_df.loc[
    hist_df["total_audi"].idxmax()
]

max_movie_name = max_movie["movieNm"]
max_movie_audi = int(max_movie["total_audi"])


# --------------------------------------------------
# 그래프 아래 설명
# --------------------------------------------------
st.markdown("### 이 그래프로 알 수 있는 것")

st.write(
    f"대부분의 영화는 총 관객 **{lower_bound:,.0f}명 ~ {upper_bound:,.0f}명** "
    f"구간에 몰려 있으며, 총 관객이 가장 많은 영화는 "
    f"**{max_movie_name}**으로 **{max_movie_audi:,}명**을 기록했습니다."
)

st.text_area(
    "이 그래프로 알 수 있는 것에 대한 추가 설명",
    value="",
    placeholder="필요하다면 이 그래프에 대한 설명을 추가로 작성하세요.",
    height=80,
    key="graph3_explanation"
)
