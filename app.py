import os

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# 1. Set up your Streamlit dashboard layout
st.set_page_config(
    page_title="Superstore Analytics", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI polish and Sidebar visibility
st.markdown(
    """
    <style>
        [data-testid="collapsedControl"],
        button[title="Collapse sidebar"],
        button[title="Expand sidebar"] {
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 2147483647 !important;
        }
        [data-testid="stSidebar"] {
            z-index: 2147483646 !important;
        }
        /* Make metric cards pop slightly */
        [data-testid="metric-container"] {
            background-color: rgba(28, 131, 225, 0.05);
            border: 1px solid rgba(28, 131, 225, 0.1);
            padding: 1rem;
            border-radius: 0.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_data_path() -> str:
    override = os.getenv("APP_DATA_PATH")
    if override:
        return override
    return os.path.join(os.path.dirname(__file__), "Superstore.csv")

DATA_PATH = get_data_path()


@st.cache_data(show_spinner=False)
def load_superstore(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="cp1252")
    for col in ["Sales", "Profit", "Discount", "Quantity"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    return df


# ----------------- MAIN DASHBOARD UI -----------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3061/3061341.png", width=60) # Placeholder generic icon
    st.header("Executive Dashboard")
    st.write("Superstore analytics overview")

st.title("📈 Superstore Executive Dashboard")
st.markdown("""
**Welcome to the internal analytics portal.**  
Explore margins, regional risks, and supply chain efficiency below. 
""")

df = load_superstore(DATA_PATH)

if df.empty:
    st.warning("No data available in Superstore.csv. Please ensure the file is in the correct directory.")
else:
    # --- TOP LEVEL METRICS ---
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    profit_margin = (total_profit / total_sales) if total_sales else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("💰 Total Sales", f"${total_sales:,.2f}")
    m2.metric("📈 Total Profit", f"${total_profit:,.2f}")
    m3.metric("🎯 Profit Margin", f"{profit_margin:.2%}")

    st.divider()

    # --- CHARTS GRID ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Regional Sales Distribution")
        region_sales = df.groupby("Region")["Sales"].sum().reset_index()
        fig_region = px.pie(
            region_sales, 
            values='Sales', 
            names='Region', 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_region.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_region, use_container_width=True)

    with col2:
        st.subheader("Profitability by Category")
        category_profit = df.groupby("Category")["Profit"].sum().reset_index().sort_values(by="Profit")
        fig_cat = px.bar(
            category_profit, 
            x='Profit', 
            y='Category', 
            orientation='h',
            color='Profit',
            color_continuous_scale="Viridis"
        )
        fig_cat.update_layout(margin=dict(t=20, b=20, l=20, r=20), coloraxis_showscale=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("Monthly Sales Trend")
    monthly_sales = (
        df.dropna(subset=["Order Date"])
        .set_index("Order Date")
        .resample("ME")["Sales"]
        .sum()
        .reset_index()
    )
    fig_trend = px.area(
        monthly_sales, 
        x="Order Date", 
        y="Sales",
        color_discrete_sequence=["#1f77b4"]
    )
    fig_trend.update_layout(
        xaxis_title="", 
        yaxis_title="Sales ($)",
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_trend, use_container_width=True)


# 2. Define the JavaScript to inject the VoiceOS widget into the parent DOM
widget_injection_code = """
<script>
    window.parent.BrainWidgetConfig = {
        "xApiKey": "",
        "session_id": "session_1777754502_ffd28c6a",
        "tenant_id": "eb29d285-88d4-4891-b791-d23910dc130f"
    };

    if (!window.parent.document.getElementById('voiceos-widget-script')) {
        const script = window.parent.document.createElement('script');
        script.id = 'voiceos-widget-script';
        script.src = "https://voxaos-dev.azurewebsites.net/app-widget-min.js";
        script.async = true;
        window.parent.document.body.appendChild(script);
    }
</script>
"""

# 3. Render the component invisibly (height=0) to execute the injection script
components.html(widget_injection_code, height=0, width=0)
