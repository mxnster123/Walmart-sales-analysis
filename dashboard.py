import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Walmart Sales Analytics",
    page_icon="📊",
    layout="wide"
)

# ---------------- DARK BLUE THEME ----------------
st.markdown("""
<style>
.stApp {
    background-color: #0B1220;
    color: #F8FAFC;
}

h1, h2, h3 {
    color: #F8FAFC;
}

[data-testid="stMetric"] {
    background-color: #162238;
    border: 1px solid #263852;
    padding: 20px;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: #CBD5E1;
}

[data-testid="stMetricValue"] {
    color: #60A5FA;
}

[data-testid="stSidebar"] {
    background-color: #111C30;
}

hr {
    border-color: #263852;
}
</style>
""", unsafe_allow_html=True)


# ---------------- CHART STYLING HELPER ----------------
def style_fig(fig, **extra):
    fig.update_layout(
        paper_bgcolor="#0B1220",
        plot_bgcolor="#111C30",
        font_color="#F8FAFC",
        **extra
    )
    return fig


# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    data = pd.read_csv("Walmart_Sales.csv")
    data.columns = data.columns.str.strip()

    raw_dates = data["Date"].astype(str).str.strip()

    # Try the common Walmart format first, then fall back to looser parsing.
    parsed = pd.to_datetime(raw_dates, format="%d-%m-%Y", errors="coerce")
    if parsed.isna().all():
        parsed = pd.to_datetime(raw_dates, format="%Y-%m-%d", errors="coerce")
    if parsed.isna().all():
        parsed = pd.to_datetime(
            raw_dates, format="mixed", dayfirst=True, errors="coerce"
        )
    data["Date"] = parsed

    # Strip $ and commas in case sales are stored as text.
    data["Weekly_Sales"] = pd.to_numeric(
        data["Weekly_Sales"].astype(str).str.replace(r"[$,\s]", "", regex=True),
        errors="coerce"
    )

    rows_before = len(data)
    data = data.dropna(subset=["Date", "Weekly_Sales"])
    if data.empty:
        raise ValueError(
            f"All {rows_before} rows were dropped. Sample raw Date values: "
            f"{raw_dates.head(3).tolist()}"
        )
    data["Year"] = data["Date"].dt.year
    data["Month"] = data["Date"].dt.month
    data["Month_Name"] = data["Date"].dt.strftime("%b")
    data["Year_Month"] = data["Date"].dt.to_period("M").astype(str)
    data["Holiday_Type"] = data["Holiday_Flag"].map(
        {1: "Holiday", 0: "Non-Holiday"}
    )
    return data


try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.info("Check that Walmart_Sales.csv and dashboard.py are in the same folder.")
    st.stop()


# ---------------- HEADER ----------------
st.title("📊 Walmart Sales Analytics")
st.caption("Interactive Retail Sales Performance Dashboard")
st.markdown("---")


# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("🎛️ Dashboard Filters")

store_options = sorted(df["Store"].unique())

selected_stores = st.sidebar.multiselect(
    "Select Stores",
    options=store_options,
    default=store_options
)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered_df = df[
    df["Store"].isin(selected_stores)
    & (df["Date"].dt.date >= start_date)
    & (df["Date"].dt.date <= end_date)
].copy()

if filtered_df.empty:
    st.warning("No data found for the selected filters. Please change them.")
    st.stop()


# ---------------- KPI CARDS ----------------
def format_sales(value):
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.1f}K"
    else:
        return f"${value:,.0f}"


col1, col2, col3, col4 = st.columns(4)

total_sales = filtered_df["Weekly_Sales"].sum()
average_sales = filtered_df["Weekly_Sales"].mean()
store_count = filtered_df["Store"].nunique()
best_store = filtered_df.groupby("Store")["Weekly_Sales"].sum().idxmax()

col1.metric("💰 Total Sales", format_sales(total_sales))
col2.metric("📈 Average Weekly Sales", format_sales(average_sales))
col3.metric("🏬 Stores Selected", f"{store_count}")
col4.metric("🏆 Best Store", f"Store {best_store}")
st.markdown("---")


# ---------------- MONTHLY SALES TREND ----------------
st.subheader("📈 Monthly Sales Trend")

# Average (not sum) so months with 4 vs 5 weeks, or partial first/last
# months, don't create artificial ups and downs.
monthly_sales = (
    filtered_df.groupby("Year_Month", as_index=False)["Weekly_Sales"]
    .mean()
    .sort_values("Year_Month")
)

fig_trend = px.line(
    monthly_sales,
    x="Year_Month",
    y="Weekly_Sales",
    markers=True,
    title="Average Weekly Sales by Month",
    labels={
        "Year_Month": "Month",
        "Weekly_Sales": "Avg Weekly Sales ($)"
    },
    template="plotly_dark"
)

fig_trend.update_traces(
    line=dict(color="#60A5FA", width=3),
    marker=dict(size=7)
)

style_fig(fig_trend)
st.plotly_chart(fig_trend, width="stretch")


# ---------------- STORE PERFORMANCE ----------------
st.subheader("🏬 Store Performance")

store_sales = (
    filtered_df.groupby("Store", as_index=False)["Weekly_Sales"]
    .sum()
    .sort_values("Weekly_Sales", ascending=False)
)

top_stores = store_sales.head(10).sort_values(
    "Weekly_Sales", ascending=True
).copy()

# Convert to text so Plotly treats Store as a category, not a number.
top_stores["Store"] = "Store " + top_stores["Store"].astype(str)

fig_stores = px.bar(
    top_stores,
    x="Weekly_Sales",
    y="Store",
    orientation="h",
    title="Top 10 Stores by Total Sales",
    labels={
        "Store": "Store",
        "Weekly_Sales": "Total Sales ($)"
    },
    template="plotly_dark",
    text_auto=",.0f"
)

fig_stores.update_traces(marker_color="#22C55E")
fig_stores.update_yaxes(
    type="category",
    categoryorder="array",
    categoryarray=top_stores["Store"].tolist()
)

style_fig(fig_stores)
st.plotly_chart(fig_stores, width="stretch")


# ---------------- HOLIDAY ANALYSIS ----------------
st.subheader("🎉 Holiday vs Non-Holiday Sales")

holiday_sales = (
    filtered_df.groupby("Holiday_Type", as_index=False)["Weekly_Sales"]
    .mean()
)

fig_holiday = px.bar(
    holiday_sales,
    x="Holiday_Type",
    y="Weekly_Sales",
    color="Holiday_Type",
    title="Average Weekly Sales Comparison",
    labels={
        "Holiday_Type": "Period",
        "Weekly_Sales": "Average Sales ($)"
    },
    template="plotly_dark",
    text_auto=",.0f",
    color_discrete_map={
        "Holiday": "#F59E0B",
        "Non-Holiday": "#60A5FA"
    }
)

style_fig(fig_holiday, showlegend=False)
st.plotly_chart(fig_holiday, width="stretch")


# ---------------- ECONOMIC ANALYSIS ----------------
st.subheader("🌡️ Economic Factors and Sales")

factor1, factor2 = st.columns(2)

with factor1:
    fig_temp = px.scatter(
        filtered_df,
        x="Temperature",
        y="Weekly_Sales",
        title="Temperature vs Weekly Sales",
        labels={
            "Temperature": "Temperature (°F)",
            "Weekly_Sales": "Weekly Sales ($)"
        },
        template="plotly_dark",
        opacity=0.55
    )
    fig_temp.update_traces(marker_color="#A78BFA")
    style_fig(fig_temp)
    st.plotly_chart(fig_temp, width="stretch")

with factor2:
    fig_unemployment = px.scatter(
        filtered_df,
        x="Unemployment",
        y="Weekly_Sales",
        title="Unemployment vs Weekly Sales",
        labels={
            "Unemployment": "Unemployment Rate (%)",
            "Weekly_Sales": "Weekly Sales ($)"
        },
        template="plotly_dark",
        opacity=0.55
    )
    fig_unemployment.update_traces(marker_color="#F472B6")
    style_fig(fig_unemployment)
    st.plotly_chart(fig_unemployment, width="stretch")


# ---------------- DATA PREVIEW ----------------
with st.expander("🔍 View Filtered Dataset"):
    st.write(f"Showing {len(filtered_df):,} records")
    st.dataframe(filtered_df, width="stretch")

st.markdown("---")
st.caption("Walmart Sales Analytics | Python • Pandas • Plotly • Streamlit")
