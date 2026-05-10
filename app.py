import hashlib
import os
import re
import sqlite3
from datetime import datetime
from typing import Optional, Tuple

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


def get_storage_dir() -> str:
    storage_dir = os.getenv("APP_STORAGE_DIR")
    if not storage_dir:
        storage_dir = os.path.join(os.path.dirname(__file__), ".data")
    os.makedirs(storage_dir, exist_ok=True)
    return storage_dir


def get_db_path() -> str:
    override = os.getenv("APP_DB_PATH")
    if override:
        dir_name = os.path.dirname(override)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        return override
    return os.path.join(get_storage_dir(), "app_data.db")


def get_data_path() -> str:
    override = os.getenv("APP_DATA_PATH")
    if override:
        return override
    return os.path.join(os.path.dirname(__file__), "Superstore.csv")


DB_PATH = get_db_path()
DATA_PATH = get_data_path()


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                salt BLOB NOT NULL,
                pw_hash BLOB NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        columns = [row[1] for row in conn.execute("PRAGMA table_info(users)")]
        if "name" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN name TEXT")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    if salt is None:
        salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return salt, pw_hash


def is_valid_email(email: str) -> bool:
    email = email.strip()
    if not email:
        return False
    return re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email) is not None


def register_user(email: str, name: str, password: str) -> bool:
    salt, pw_hash = hash_password(password)
    created_at = datetime.utcnow().isoformat()
    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO users (email, name, salt, pw_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                (email, name, salt, pw_hash, created_at),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def verify_user(email: str, password: str) -> Optional[Tuple[int, Optional[str], str]]:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT id, name, email, salt, pw_hash FROM users WHERE email = ?", (email,)
        ).fetchone()
    if row is None:
        return None
    salt = row["salt"]
    expected_hash = row["pw_hash"]
    _, pw_hash = hash_password(password, salt)
    if pw_hash == expected_hash:
        return row["id"], row["name"], row["email"]
    return None


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


init_db()

# Session State Initialization
if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.email = None
    st.session_state.display_name = None

# ----------------- AUTHENTICATION UI -----------------
if st.session_state.user_id is None:
    # Center the login panel for a clean, modern look
    _, col_main, _ = st.columns([1, 1.5, 1])
    
    with col_main:
        st.title("🔐 Superstore Portal")
        st.markdown("Welcome back. Please log in or register to access the executive dashboard.")
        st.divider()

        tabs = st.tabs(["🔑 Login", "📝 Register"])
        
        with tabs[0]:
            with st.form("login_form", border=False):
                login_email = st.text_input("Email Address", key="login_email")
                login_password = st.text_input("Password", type="password", key="login_password")
                login_submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if login_submit:
                login_email_clean = login_email.strip().lower()
                if not is_valid_email(login_email_clean):
                    st.error("Please enter a valid email address.")
                else:
                    result = verify_user(login_email_clean, login_password)
                if result is None:
                    st.error("Invalid email or password.")
                else:
                    user_id, name, email = result
                    st.session_state.user_id = user_id
                    st.session_state.email = email
                    st.session_state.display_name = name
                    st.rerun()

        with tabs[1]:
            with st.form("register_form", border=False):
                reg_name = st.text_input("Full Name", key="reg_name")
                reg_email = st.text_input("Email Address", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                reg_submit = st.form_submit_button("Create Account", use_container_width=True)
            
            if reg_submit:
                name_clean = reg_name.strip()
                email_normalized = reg_email.strip().lower()
                if not name_clean or not email_normalized or not reg_password:
                    st.error("Full name, email, and password are required.")
                elif not is_valid_email(email_normalized):
                    st.error("Please enter a valid email address.")
                elif register_user(email_normalized, name_clean, reg_password):
                    st.success("Account created successfully! You can now log in.")
                else:
                    st.error("Email already exists. Please log in.")

    st.stop()


# ----------------- MAIN DASHBOARD UI -----------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3061/3061341.png", width=60) # Placeholder generic icon
    st.header("Executive Profile")
    account_name = st.session_state.display_name or st.session_state.email
    st.write(f"**User:** {account_name}")
    st.write(f"**Email:** {st.session_state.email}")
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.email = None
        st.session_state.display_name = None
        st.rerun()

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
    (function() {
        const widgetSelectors = [
            'voiceos-widget',
            '.voiceos-widget',
            '#voiceos-widget',
            '[data-voiceos-widget]'
        ];
        const selectorList = widgetSelectors.join(',');

        const removeDuplicateWidgets = () => {
            const widgetNodes = window.parent.document.querySelectorAll(selectorList);
            if (widgetNodes.length > 1) {
                widgetNodes.forEach((node, index) => {
                    if (index > 0) node.remove();
                });
            }
        };

        removeDuplicateWidgets();

        const existingScript = window.parent.document.getElementById('voiceos-widget-script');
        const widgetExists = window.parent.document.querySelector(selectorList);
        if (window.parent.__voiceosWidgetInitialized && widgetExists) {
            // Avoid reinitializing the widget on Streamlit reruns.
            return;
        }

        const styleId = 'voiceos-widget-style';
        if (!window.parent.document.getElementById(styleId)) {
            const style = window.parent.document.createElement('style');
            style.id = styleId;
            style.textContent = `
                voiceos-widget, .voiceos-widget, #voiceos-widget, [data-voiceos-widget] {
                    z-index: 2147483647 !important;
                }
                voiceos-widget iframe, .voiceos-widget iframe, #voiceos-widget iframe, [data-voiceos-widget] iframe {
                    max-width: 100vw !important;
                    max-height: 100vh !important;
                }
                voiceos-widget[maximized],
                voiceos-widget[fullscreen],
                voiceos-widget[expanded],
                .voiceos-widget.maximized,
                .voiceos-widget.fullscreen,
                .voiceos-widget.expanded,
                .voiceos-widget--maximized,
                .voiceos-widget--fullscreen,
                .voiceos-widget--expanded,
                #voiceos-widget.maximized,
                #voiceos-widget.fullscreen,
                #voiceos-widget.expanded,
                [data-voiceos-widget][data-state="maximized"],
                [data-voiceos-widget][data-state="fullscreen"],
                [data-voiceos-widget][data-state="expanded"] {
                    position: fixed !important;
                    inset: 0 !important;
                    width: 100vw !important;
                    height: 100vh !important;
                    max-width: 100vw !important;
                    max-height: 100vh !important;
                    border-radius: 0 !important;
                }
                voiceos-widget[maximized] iframe,
                voiceos-widget[fullscreen] iframe,
                voiceos-widget[expanded] iframe,
                .voiceos-widget.maximized iframe,
                .voiceos-widget.fullscreen iframe,
                .voiceos-widget.expanded iframe,
                .voiceos-widget--maximized iframe,
                .voiceos-widget--fullscreen iframe,
                .voiceos-widget--expanded iframe,
                #voiceos-widget.maximized iframe,
                #voiceos-widget.fullscreen iframe,
                #voiceos-widget.expanded iframe,
                [data-voiceos-widget][data-state="maximized"] iframe,
                [data-voiceos-widget][data-state="fullscreen"] iframe,
                [data-voiceos-widget][data-state="expanded"] iframe {
                    width: 100vw !important;
                    height: 100vh !important;
                    max-width: 100vw !important;
                    max-height: 100vh !important;
                    border-radius: 0 !important;
                }
            `;
            window.parent.document.head.appendChild(style);
        }

        if (!existingScript || !widgetExists) {
            window.parent.BrainWidgetConfig = {
                "xApiKey": "",
                "session_id": "session_1777754502_ffd28c6a",
                "tenant_id": "eb29d285-88d4-4891-b791-d23910dc130f"
            };

            const script = window.parent.document.createElement('script');
            script.id = 'voiceos-widget-script';
            script.src = "https://voxaos-dev.azurewebsites.net/app-widget-min.js";
            script.async = true;
            script.onload = () => {
                window.parent.__voiceosWidgetInitialized = true;
                removeDuplicateWidgets();
            };
            script.onerror = () => {
                window.parent.__voiceosWidgetInitialized = false;
            };
            window.parent.document.body.appendChild(script);
        }
    })();
</script>
"""

# 3. Render the component invisibly (height=0) to execute the injection script
components.html(widget_injection_code, height=0, width=0)
