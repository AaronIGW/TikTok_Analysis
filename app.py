import streamlit as st
import plotly.express as px
import pandas as pd
from ingest import load_and_clean_tiktok_data
from ai_tagger import generate_content_strategy

st.set_page_config(page_title="TikTok Gaming Analytics", layout="wide")

st.title("🎮 TikTok Content Analytics & Strategy Engine")

# 1. Load Data Pipeline
@st.cache_data
def get_data():
    return load_and_clean_tiktok_data("data.json")

raw_df = get_data()

# ----------------- SIDEBAR FILTERS -----------------
st.sidebar.header("🕹️ Filter Controls")

# Date Range Filter
min_date = raw_df["Date"].min().date()
max_date = raw_df["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Content Category Multiselect
categories = ["All"] + sorted(raw_df["Content_Category"].unique().tolist())
selected_category = st.sidebar.selectbox("Filter by Category", categories)

# Apply Filters
filtered_df = raw_df.copy()

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date) & 
        (filtered_df["Date"].dt.date <= end_date)
    ]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Content_Category"] == selected_category]

# Export Cleaned Data in Sidebar
st.sidebar.markdown("---")
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    label="📥 Download Filtered Data (.csv)",
    data=csv_data,
    file_name="tiktok_cleaned_data.csv",
    mime="text/csv",
    use_container_width=True
)

# ----------------- EXECUTIVE KPI BANNER -----------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Videos", f"{len(filtered_df):,}")
col2.metric("Total Likes", f"{filtered_df['Likes'].sum():,}")
top_outlier = filtered_df['Likes'].max() if len(filtered_df) > 0 else 0
avg_likes = int(filtered_df['Likes'].mean()) if len(filtered_df) > 0 else 0
col3.metric("Top Outlier (Likes)", f"{top_outlier:,}")
col4.metric("Avg Likes / Post", f"{avg_likes:,}")

st.markdown("---")

# ----------------- INTERACTIVE CHARTS -----------------
row1_left, row1_right = st.columns([3, 2])

with row1_left:
    st.subheader("Performance by Content Era")
    if not filtered_df.empty:
        era_stats = filtered_df.groupby("Content_Category")["Likes"].agg(["count", "sum"]).reset_index()
        era_stats.columns = ["Category", "Posts", "Total Likes"]
        fig_era = px.bar(
            era_stats.sort_values(by="Total Likes", ascending=True),
            x="Total Likes",
            y="Category",
            orientation="h",
            color="Total Likes",
            color_continuous_scale="Viridis",
            text="Total Likes"
        )
        fig_era.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_era.update_layout(yaxis_title=None, showlegend=False, height=450)
        st.plotly_chart(fig_era, use_container_width=True)
    else:
        st.warning("No data found for this selection.")

with row1_right:
    st.subheader("Top Sounds Distribution")
    if not filtered_df.empty:
        top_sounds = filtered_df[filtered_df["Likes"] > 0]["Sound"].value_counts().head(8).reset_index()
        top_sounds.columns = ["Sound", "Post Count"]
        fig_sound = px.pie(top_sounds, values="Post Count", names="Sound", hole=0.45)
        fig_sound.update_layout(height=450, showlegend=False)
        st.plotly_chart(fig_sound, use_container_width=True)
    else:
        st.warning("No data found for this selection.")

st.markdown("---")

# ----------------- AI STRATEGIC REPORT -----------------
st.subheader("🤖 AI Content Strategy & Retrospective")
if st.button("Generate Strategy Report", type="primary"):
    if not filtered_df.empty:
        with st.spinner("Analyzing current view metrics and synthesizing video concepts..."):
            report = generate_content_strategy(filtered_df)
            st.markdown(report)
    else:
        st.error("Cannot run strategy on empty dataset.")
else:
    st.info(f"Click the button above to run the AI engine against the current filtered view ({len(filtered_df)} posts).")