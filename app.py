import streamlit as st
import plotly.express as px
import pandas as pd
from ingest import load_and_clean_tiktok_data
from ai_tagger import generate_content_strategy

st.set_page_config(page_title="Gaming BI & Strategy Engine", layout="wide")

st.title("🎮 Gaming Content BI & Strategic Analytics")

@st.cache_data
def get_data():
    return load_and_clean_tiktok_data("data.json")

raw_df = get_data()

# ----------------- SIDEBAR CONTROLS -----------------
st.sidebar.header("🕹️ Multi-Dimensional Filters")

# Date Filter
min_date = raw_df["Date"].min().date()
max_date = raw_df["Date"].max().date()
selected_dates = st.sidebar.date_input("Date Window", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# Primary Game Filter
games = ["All"] + sorted(raw_df["Primary_Game"].unique().tolist())
selected_game = st.sidebar.selectbox("Primary Game", games)

# Format Filter
formats = ["All"] + sorted(raw_df["Content_Format"].unique().tolist())
selected_format = st.sidebar.selectbox("Content Format", formats)

# Filter Execution
filtered_df = raw_df.copy()
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered_df = filtered_df[(filtered_df["Date"].dt.date >= start_date) & (filtered_df["Date"].dt.date <= end_date)]

if selected_game != "All":
    filtered_df = filtered_df[filtered_df["Primary_Game"] == selected_game]

if selected_format != "All":
    filtered_df = filtered_df[filtered_df["Content_Format"] == selected_format]

# CSV Export
st.sidebar.markdown("---")
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.sidebar.download_button("📥 Export Current View (.csv)", data=csv_data, file_name="filtered_gaming_metrics.csv", mime="text/csv", use_container_width=True)

# ----------------- EXECUTIVE KPI BANNER -----------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Videos in View", f"{len(filtered_df):,}")
k2.metric("Total Likes", f"{filtered_df['Likes'].sum():,}")
top_val = filtered_df['Likes'].max() if len(filtered_df) > 0 else 0
avg_val = int(filtered_df['Likes'].mean()) if len(filtered_df) > 0 else 0
k3.metric("Peak Outlier", f"{top_val:,}")
k4.metric("Avg Likes / Post", f"{avg_val:,}")

st.markdown("---")

# ----------------- ANALYTICAL GRAPHS -----------------
tab1, tab2 = st.tabs(["📊 Performance Breakdown", "🔥 Format vs Game Matrix"])

with tab1:
    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader("Performance by Sub-Theme")
        theme_perf = filtered_df.groupby("Sub_Theme")["Likes"].agg(["count", "sum"]).reset_index()
        theme_perf.columns = ["Sub-Theme", "Posts", "Total Likes"]
        fig_theme = px.bar(
            theme_perf.sort_values(by="Total Likes", ascending=True),
            x="Total Likes",
            y="Sub-Theme",
            orientation="h",
            color="Total Likes",
            color_continuous_scale="Turbo",
            text="Total Likes"
        )
        fig_theme.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_theme.update_layout(yaxis_title=None, height=450, showlegend=False)
        st.plotly_chart(fig_theme, use_container_width=True)
    with c2:
        st.subheader("Format Share")
        fmt_counts = filtered_df["Content_Format"].value_counts().reset_index()
        fmt_counts.columns = ["Format", "Count"]
        fig_fmt = px.pie(fmt_counts, values="Count", names="Format", hole=0.4)
        fig_fmt.update_layout(height=450, showlegend=True)
        st.plotly_chart(fig_fmt, use_container_width=True)

with tab2:
    st.subheader("Game × Format Engagement Heatmap (Avg Likes)")
    pivot_df = raw_df.pivot_table(index="Primary_Game", columns="Content_Format", values="Likes", aggfunc="mean").fillna(0).round(0)
    fig_heat = px.imshow(
        pivot_df,
        labels=dict(x="Format", y="Game", color="Avg Likes"),
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale="Blues",
        text_auto=True,
        aspect="auto"
    )
    fig_heat.update_layout(height=480)
    st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ----------------- AI STRATEGY ENGINE -----------------
st.subheader("🤖 Context-Conditioned AI Strategy Engine")
strategy_mode = st.selectbox(
    "Select Strategy Objective:",
    [
        "Comprehensive Channel Audit & Outlier Analysis",
        "Helldivers 2 Tactical Retention & Pacing Playbook",
        "Viral Edit Replication Framework (Skate/Montage Mechanics)"
    ]
)

if st.button("Generate Strategy Report", type="primary"):
    if not filtered_df.empty:
        with st.spinner(f"Running LLM analysis on {strategy_mode}..."):
            report = generate_content_strategy(filtered_df)
            st.markdown(report)
    else:
        st.error("Dataset is empty under current filters.")