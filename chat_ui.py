import time

import pandas as pd
import plotly.express as px
import streamlit as st

from app import fetch_data, generate_sql
from viz_app import (
    cumulative_trade_summary,
    market_breadth_summary,
    top_companies_summary,
    top_movers_summary,
    trade_summary,
)


st.set_page_config(
    page_title="PricePulse",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #0b1220;
    --panel: #111827;
    --panel-soft: #172033;
    --ink: #e5eefc;
    --muted: #94a3b8;
    --border: #243041;
    --accent: #38bdf8;
    --accent-dark: #0ea5e9;
    --success: #34d399;
    --warning: #fbbf24;
}

.stApp {
    background: var(--bg);
    color: var(--ink);
}

[data-testid="stHeader"] {
    background: rgba(11, 18, 32, 0.95);
    border-bottom: 1px solid var(--border);
}

[data-testid="stHeader"] svg,
[data-testid="collapsedControl"] svg {
    color: var(--ink) !important;
    fill: var(--ink) !important;
}

[data-testid="stSidebar"] {
    background: var(--panel);
    border-right: 1px solid var(--border);
}

body,
[data-testid="stAppViewContainer"],
[data-testid="stSidebar"],
h1, h2, h3, h4, h5, h6,
label, p {
    font-family: 'Inter', sans-serif !important;
}

.material-icons,
.material-icons-outlined,
.material-icons-round,
.material-icons-sharp,
.material-icons-two-tone,
.material-symbols-outlined,
.material-symbols-rounded,
.material-symbols-sharp {
    font-family: "Material Symbols Outlined", "Material Symbols Rounded", "Material Icons" !important;
    font-weight: normal !important;
    font-style: normal !important;
}

[data-testid="stSidebar"] * {
    color: var(--ink) !important;
}

[data-testid="stMarkdownContainer"],
label,
p,
h1,
h2,
h3,
h4,
h5,
h6 {
    color: var(--ink);
}

.stTextArea textarea,
.stTextInput input {
    background: var(--panel-soft) !important;
    color: var(--ink) !important;
    border: 1px solid var(--border) !important;
}

.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
    color: var(--muted) !important;
}

.stButton > button {
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
}

.stButton > button[kind="secondary"] {
    background: var(--panel-soft) !important;
    color: var(--ink) !important;
}

.stButton > button[kind="primary"] {
    background: var(--accent-dark) !important;
    color: #08111d !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

.main-header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--border);
}

.main-header h1 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    color: var(--ink);
}

.main-header p {
    color: var(--muted);
    margin-top: 0.5rem;
}

.chat-container {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    min-height: 500px;
}

.message {
    margin-bottom: 1rem;
    padding: 1rem;
    border-radius: 8px;
}

.message-user {
    background: rgba(56, 189, 248, 0.10);
    border-left: 3px solid var(--accent);
}

.message-assistant {
    background: var(--panel-soft);
    border: 1px solid var(--border);
}

.metric-card {
    background: var(--panel-soft);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    transition: all 0.2s;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(0,0,0,0.28);
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--ink);
    margin: 0.5rem 0;
}

.metric-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--muted);
}

.sql-box {
    background: #020617;
    color: #dbeafe;
    padding: 1rem;
    border-radius: 8px;
    font-family: 'Monaco', monospace;
    font-size: 12px;
    overflow-x: auto;
}

.sidebar-nav {
    margin: 1rem 0;
}

.nav-item {
    padding: 0.5rem 1rem;
    margin: 0.25rem 0;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.nav-item:hover {
    background: var(--panel-soft);
}

.nav-active {
    background: rgba(56, 189, 248, 0.14);
    color: var(--accent);
    font-weight: 600;
}
</style>
""",
    unsafe_allow_html=True,
)


if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "dashboard_days" not in st.session_state:
    st.session_state.dashboard_days = 7
if "top_n_companies" not in st.session_state:
    st.session_state.top_n_companies = 5
if "nav_loading" not in st.session_state:
    st.session_state.nav_loading = False
if "latest_query_result" not in st.session_state:
    st.session_state.latest_query_result = None
if "latest_query_message" not in st.session_state:
    st.session_state.latest_query_message = ""


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## PricePulse")
        st.caption("DSE market dashboard and AI query")
        st.markdown("---")

        current_page = st.session_state.page
        selected = st.radio(
            "Navigation",
            ["Dashboard", "AI Query"],
            index=0 if current_page == "Dashboard" else 1,
        )
        if selected != current_page:
            st.session_state.page = selected
            st.session_state.nav_loading = True
            st.rerun()

        if selected == "Dashboard":
            st.markdown("---")
            st.select_slider(
                "Days to show",
                options=[7, 15, 30],
                value=st.session_state.dashboard_days,
                key="dashboard_days",
            )
            st.slider(
                "Top N companies",
                min_value=3,
                max_value=15,
                value=st.session_state.top_n_companies,
                step=1,
                key="top_n_companies",
            )


def format_number(value) -> str:
    if pd.isna(value):
        return "-"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    if isinstance(value, float):
        return f"{value:,.0f}"
    return f"{value:,}"


def build_dashboard_chart(summary_df: pd.DataFrame, metric: str, title: str, color: str):
    fig = px.line(summary_df, x="date", y=metric, markers=True)
    fig.update_traces(
        line=dict(color=color, width=3),
        marker=dict(color=color, size=6),
        hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(23,32,51,0.75)",
        font=dict(color="#e5eefc"),
        margin=dict(l=12, r=12, t=48, b=12),
        height=320,
        showlegend=False,
        xaxis=dict(title=None, gridcolor="#243041", tickangle=-35),
        yaxis=dict(title=None, gridcolor="#243041"),
    )
    return fig


def build_multi_line_chart(df: pd.DataFrame, series_map: list[tuple[str, str, str]], title: str):
    fig = px.line(df, x="date", y=[item[0] for item in series_map], markers=True)
    for trace, (_, label, color) in zip(fig.data, series_map):
        trace.name = label
        trace.line.color = color
        trace.line.width = 3
        trace.marker.color = color
        trace.marker.size = 6
        trace.hovertemplate = "%{x}<br>%{y:,.0f}<extra>" + label + "</extra>"
    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(23,32,51,0.75)",
        font=dict(color="#e5eefc"),
        margin=dict(l=12, r=12, t=48, b=12),
        height=360,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(title=None, gridcolor="#243041", tickangle=-35),
        yaxis=dict(title=None, gridcolor="#243041"),
    )
    return fig


def build_market_breadth_chart(df: pd.DataFrame):
    fig = px.bar(
        df,
        x="date",
        y=["gainers", "losers", "unchanged"],
        barmode="group",
        color_discrete_map={
            "gainers": "#34d399",
            "losers": "#f87171",
            "unchanged": "#94a3b8",
        },
    )
    for trace in fig.data:
        trace.hovertemplate = "%{x}<br>%{y:,.0f}<extra>" + trace.name.title() + "</extra>"
    fig.update_layout(
        title="Daily Market Breadth",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(23,32,51,0.75)",
        font=dict(color="#e5eefc"),
        margin=dict(l=12, r=12, t=48, b=12),
        height=360,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(title=None, gridcolor="#243041", tickangle=-35),
        yaxis=dict(title=None, gridcolor="#243041"),
    )
    return fig


def build_top_movers_chart(df: pd.DataFrame, mode: str):
    if mode == "gainers":
        movers_df = df.nlargest(5, "pct_change").sort_values("pct_change", ascending=True)
        title = "Top Gainers"
        color = "#34d399"
    else:
        movers_df = df.nsmallest(5, "pct_change").sort_values("pct_change", ascending=False)
        title = "Top Losers"
        color = "#f87171"

    fig = px.bar(
        movers_df,
        x="pct_change",
        y="inst_code",
        orientation="h",
        text="pct_change",
    )
    fig.update_traces(
        marker=dict(color=color),
        texttemplate="%{x:.2f}%",
        textposition="inside",
        insidetextanchor="middle",
        hovertemplate="%{y}<br>%{x:.2f}%<extra></extra>",
    )
    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(23,32,51,0.75)",
        font=dict(color="#e5eefc"),
        margin=dict(l=12, r=24, t=48, b=12),
        height=360,
        showlegend=False,
        xaxis=dict(title="Percent Change", gridcolor="#243041"),
        yaxis=dict(title=None, gridcolor="#243041"),
    )
    return fig


def build_top_companies_chart(df: pd.DataFrame, metric: str, title: str, color: str, top_n: int):
    top_df = df.nlargest(top_n, metric).sort_values(metric, ascending=True)
    fig = px.bar(
        top_df,
        x=metric,
        y="inst_code",
        orientation="h",
        text=metric,
    )
    fig.update_traces(
        marker=dict(color=color),
        texttemplate="%{x:,.0f}",
        textposition="inside",
        insidetextanchor="middle",
        hovertemplate="%{y}<br>%{x:,.0f}<extra></extra>",
    )
    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(23,32,51,0.75)",
        font=dict(color="#e5eefc"),
        margin=dict(l=12, r=24, t=48, b=12),
        height=320,
        showlegend=False,
        xaxis=dict(title=None, gridcolor="#243041"),
        yaxis=dict(title=None, gridcolor="#243041"),
    )
    return fig


def render_dashboard() -> None:
    st.markdown('<div class="main-header"><h1>Market Dashboard</h1><p>Daily trading activity overview</p></div>', unsafe_allow_html=True)
    st.caption(f"Showing the last {st.session_state.dashboard_days} trading days.")

    summary_df = trade_summary(st.session_state.dashboard_days)
    if isinstance(summary_df, str):
        st.error(summary_df)
        return

    company_df = top_companies_summary(st.session_state.dashboard_days)
    if isinstance(company_df, str):
        st.error(company_df)
        return

    movers_df = top_movers_summary(st.session_state.dashboard_days)
    if isinstance(movers_df, str):
        st.error(movers_df)
        return

    summary_df = summary_df.copy()
    summary_df["date"] = pd.to_datetime(summary_df["date"], errors="coerce")
    summary_df = summary_df.sort_values("date")
    company_df = company_df.copy()
    movers_df = movers_df.copy()
    movers_df["pct_change"] = pd.to_numeric(movers_df["pct_change"], errors="coerce")

    chart_specs = [
        ("total_trade", "Total Trades", "#38bdf8"),
        ("total_value", "Total Value (BDT)", "#34d399"),
        ("total_volume", "Total Volume", "#fbbf24"),
    ]

    if st.session_state.dashboard_days >= 30:
        for metric, title, color in chart_specs:
            st.plotly_chart(
                build_dashboard_chart(summary_df, metric, title, color),
                use_container_width=True,
            )
    else:
        chart_col1, chart_col2, chart_col3 = st.columns(3)
        for col, (metric, title, color) in zip((chart_col1, chart_col2, chart_col3), chart_specs):
            with col:
                st.plotly_chart(
                    build_dashboard_chart(summary_df, metric, title, color),
                    use_container_width=True,
                )

    st.markdown("---")
    st.subheader(f"Top {st.session_state.top_n_companies} Companies By Activity")

    top_chart_specs = [
        ("total_trade", "Top 5 by Trades", "#38bdf8"),
        ("total_volume", "Top 5 by Volume", "#fbbf24"),
        ("total_value", "Top 5 by Value", "#34d399"),
    ]

    if st.session_state.dashboard_days >= 30:
        for metric, title, color in top_chart_specs:
            st.plotly_chart(
                build_top_companies_chart(company_df, metric, title, color, st.session_state.top_n_companies),
                use_container_width=True,
            )
    else:
        bar_col1, bar_col2, bar_col3 = st.columns(3)
        for col, (metric, title, color) in zip((bar_col1, bar_col2, bar_col3), top_chart_specs):
            with col:
                st.plotly_chart(
                    build_top_companies_chart(company_df, metric, title, color, st.session_state.top_n_companies),
                    use_container_width=True,
                )

    st.markdown("---")
    st.subheader("Additional Market Signals")

    signal_col1, signal_col2 = st.columns(2)
    with signal_col1:
        st.plotly_chart(
            build_top_movers_chart(movers_df, "gainers"),
            use_container_width=True,
        )
    with signal_col2:
        st.plotly_chart(
            build_top_movers_chart(movers_df, "losers"),
            use_container_width=True,
        )

def render_workspace() -> None:
    st.markdown('<div class="main-header"><h1>AI Query</h1><p>Ask questions in plain English</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container():
            prompt = st.text_area(
                "What would you like to know?",
                placeholder="Example: Show closing price of ACI for the last 7 days",
                height=100,
                key="prompt_input"
            )
            
            col_btn1, col_btn2 = st.columns([1, 4])
            with col_btn1:
                submitted = st.button("Run Query", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("### AI Query")
        st.caption("Write your question and run it to generate SQL and fetch results.")
    
    if submitted and prompt.strip():
        user_prompt = prompt.strip()

        with st.spinner("Analyzing your question..."):
            result = fetch_data(generate_sql(user_prompt))

        if isinstance(result, str):
            st.session_state.latest_query_message = f"❌ {result}"
            st.session_state.latest_query_result = None
        else:
            st.session_state.latest_query_message = f"✅ Found {len(result)} records"
            st.session_state.latest_query_result = result
        st.rerun()

    if not st.session_state.latest_query_message:
        st.info("💡 Ask a question above to get started.")
    else:
        if st.session_state.latest_query_message.startswith("❌"):
            st.error(st.session_state.latest_query_message)
        else:
            st.success(st.session_state.latest_query_message)

        if isinstance(st.session_state.latest_query_result, pd.DataFrame) and not st.session_state.latest_query_result.empty:
            st.dataframe(st.session_state.latest_query_result, use_container_width=True)

render_sidebar()

if st.session_state.nav_loading:
    with st.spinner(f"Opening {st.session_state.page}..."):
        time.sleep(0.35)
    st.session_state.nav_loading = False


# Main content routing
if st.session_state.page == "Dashboard":
    render_dashboard()
else:
    render_workspace()
