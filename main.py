<<<<<<< HEAD:Streamlit Dev/main.py
import streamlit as st
import pandas as pd
import re
import os
from streamlit_autorefresh import st_autorefresh



# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="ClimateScope", layout="wide")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {
        "subhadip": {
            "email": "subhadip@gmail.com",
            "password": "subhadip123"
        }
    }

if "image_counter" not in st.session_state:
    st.session_state.image_counter = 0

# --------------------------------------------------
# AUTH PAGE
# --------------------------------------------------
def auth_page():
    st.image(
        "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?auto=format&fit=crop&w=1600&q=80",
        use_container_width=True
    )

    st.title("🔐 ClimateScope Authentication")
    st.caption("Login or Register to access the ClimateScope Dashboard")

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", key="login_btn"):
            users = st.session_state.users
            if username in users and users[username]["password"] == password:
                st.success("✅ Login Successful")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    with tab2:
        reg_user = st.text_input("Username", key="reg_user")
        reg_email = st.text_input("Email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        reg_conf = st.text_input("Confirm Password", type="password")

        if st.button("Register", key="register_btn"):
            if not reg_user or not reg_email or not reg_pass:
                st.error("❌ All fields required")
            elif reg_user in st.session_state.users:
                st.error("❌ Username already exists")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", reg_email):
                st.error("❌ Invalid email format")
            elif reg_pass != reg_conf:
                st.error("❌ Passwords do not match")
            else:
                st.session_state.users[reg_user] = {
                    "email": reg_email,
                    "password": reg_pass
                }
                st.success("✅ Registration successful. Please login.")

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
def dashboard():

    # --------------------------------------------------
    # LIVE IMAGE CONTROL
    # --------------------------------------------------
    st.header("⏱ Live Weather Image Control")

    enable_timer = st.checkbox("Enable Auto Image Change")

    timer_options = {
        "00:15 (15 seconds)": 15000,
        "00:30 (30 seconds)": 30000,
        "01:00 (1 minute)": 60000
    }

    selected_timer = st.selectbox(
        "Select Timer",
        list(timer_options.keys()),
        disabled=not enable_timer
    )

    weather_images = [
        "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
        "https://images.unsplash.com/photo-1501630834273-4b5604d2ee31",
        "https://images.unsplash.com/photo-1500674425229-f692875b0ab7"
    ]

    refresh_interval = timer_options[selected_timer] if enable_timer else 0

    if refresh_interval > 0:
        st_autorefresh(interval=refresh_interval, key="auto_refresh")
        st.session_state.image_counter += 1
    else:
        st.session_state.image_counter = 0

    index = st.session_state.image_counter % len(weather_images)

    st.image(
        weather_images[index],
        use_container_width=True,
        caption=f"Live Weather Image (Update #{st.session_state.image_counter})"
    )

    st.divider()

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------
    st.title("🌍 ClimateScope Dashboard")
    st.subheader("Visualizing Global Weather Trends")
    st.success(f"Welcome {st.session_state.username} 👋")

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------
    @st.cache_data
    def load_data():
        # Get the correct path to the CSV file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        csv_path = os.path.join(parent_dir, "GlobalWeatherRepository.csv")
        return pd.read_csv(csv_path)

    try:
        df = load_data()
        st.success("✅ Dataset loaded successfully")
    except FileNotFoundError:
        st.error("❌ Error: GlobalWeatherRepository.csv not found")
        return
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return

    # --------------------------------------------------
    # USER CONTROLS
    # --------------------------------------------------
    st.header("🔘 User Controls")

    if "country" not in df.columns:
        st.error("❌ Error: 'country' column not found in dataset")
        return

    countries = sorted(df["country"].dropna().unique())
    if len(countries) == 0:
        st.error("❌ No country data available")
        return

    selected_country = st.selectbox("🌍 Select Country", countries)

    unit = st.radio("🌡 Temperature Unit", ["Celsius", "Fahrenheit"])

    temp_col = "temperature_celsius" if unit == "Celsius" else "temperature_fahrenheit"

    country_df = df[df["country"] == selected_country]

    if country_df.empty:
        st.warning(f"⚠️ No data available for {selected_country}")
        return

    st.subheader(f"📄 Data Preview – {selected_country}")
    st.dataframe(country_df.head(), use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # SMART WEATHER SUMMARY
    # --------------------------------------------------
    st.header("🧠 Smart Weather Summary")

    avg_temp = country_df[temp_col].mean()
    max_temp = country_df[temp_col].max()
    avg_wind = country_df["wind_kph"].mean()
    
    # Handle empty mode
    condition_mode = country_df["condition_text"].mode()
    common_condition = condition_mode[0] if len(condition_mode) > 0 else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡 Avg Temp", f"{avg_temp:.1f}")
    c2.metric("🔥 Max Temp", f"{max_temp:.1f}")
    c3.metric("💨 Avg Wind (km/h)", f"{avg_wind:.1f}")
    c4.metric("☁ Common Weather", common_condition)

    # --------------------------------------------------
    # EXTREME WEATHER ALERTS
    # --------------------------------------------------
    if unit == "Celsius" and max_temp > 35:
        st.error("🚨 Heat Alert: Extremely high temperature detected!")

    if avg_wind > 30:
        st.warning("⚠️ Strong wind conditions observed")

    st.divider()

    # --------------------------------------------------
    # TEMPERATURE TREND
    # --------------------------------------------------
    if st.checkbox("📈 Show Temperature Trend"):
        st.subheader("Temperature Trend Over Time")
        if "last_updated" in country_df.columns:
            trend_df = country_df.sort_values("last_updated")
            st.line_chart(trend_df.set_index("last_updated")[temp_col])
        else:
            st.warning("⚠️ 'last_updated' column not found")

    # --------------------------------------------------
    # WEATHER CONDITION DISTRIBUTION
    # --------------------------------------------------
    st.subheader("☁ Weather Condition Distribution")
    condition_counts = country_df["condition_text"].value_counts()
    st.bar_chart(condition_counts)

    # --------------------------------------------------
    # AUTO INSIGHT
    # --------------------------------------------------
    st.info(
        f"📌 Insight: {selected_country} experiences an average temperature of "
        f"{avg_temp:.1f}°{unit[0]} with predominantly "
        f"{common_condition.lower()} conditions."
    )

    st.divider()

    # --------------------------------------------------
    # DATASET OVERVIEW
    # --------------------------------------------------
    st.header("📊 Dataset Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Rows", df.shape[0])
    c2.metric("Total Columns", df.shape[1])
    c3.metric("Missing Values", df.isnull().sum().sum())

    # --------------------------------------------------
    # LOGOUT
    # --------------------------------------------------
    if st.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.image_counter = 0
        st.rerun()

    st.markdown("---")
    st.markdown("📘 **ClimateScope – Milestone 1 Web Application**")

# --------------------------------------------------
# PAGE CONTROLLER
# --------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
=======
import streamlit as st
import pandas as pd
import re
import os
from streamlit_autorefresh import st_autorefresh

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="ClimateScope", layout="wide")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {
        "subhadip": {
            "email": "subhadip@gmail.com",
            "password": "subhadip123"
        }
    }

if "image_counter" not in st.session_state:
    st.session_state.image_counter = 0

# --------------------------------------------------
# AUTH PAGE
# --------------------------------------------------
def auth_page():
    st.image(
        "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?auto=format&fit=crop&w=1600&q=80",
        use_container_width=True
    )

    st.title("🔐 ClimateScope Authentication")
    st.caption("Login or Register to access the ClimateScope Dashboard")

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", key="login_btn"):
            users = st.session_state.users
            if username in users and users[username]["password"] == password:
                st.success("✅ Login Successful")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    with tab2:
        reg_user = st.text_input("Username", key="reg_user")
        reg_email = st.text_input("Email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        reg_conf = st.text_input("Confirm Password", type="password")

        if st.button("Register", key="register_btn"):
            if not reg_user or not reg_email or not reg_pass:
                st.error("❌ All fields required")
            elif reg_user in st.session_state.users:
                st.error("❌ Username already exists")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", reg_email):
                st.error("❌ Invalid email format")
            elif reg_pass != reg_conf:
                st.error("❌ Passwords do not match")
            else:
                st.session_state.users[reg_user] = {
                    "email": reg_email,
                    "password": reg_pass
                }
                st.success("✅ Registration successful. Please login.")

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
def dashboard():

    # --------------------------------------------------
    # LIVE IMAGE CONTROL
    # --------------------------------------------------
    st.header("⏱ Live Weather Image Control")

    enable_timer = st.checkbox("Enable Auto Image Change")

    timer_options = {
        "00:15 (15 seconds)": 15000,
        "00:30 (30 seconds)": 30000,
        "01:00 (1 minute)": 60000
    }

    selected_timer = st.selectbox(
        "Select Timer",
        list(timer_options.keys()),
        disabled=not enable_timer
    )

    weather_images = [
        "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
        "https://images.unsplash.com/photo-1501630834273-4b5604d2ee31",
        "https://images.unsplash.com/photo-1500674425229-f692875b0ab7"
    ]

    refresh_interval = timer_options[selected_timer] if enable_timer else 0

    if refresh_interval > 0:
        st_autorefresh(interval=refresh_interval, key="auto_refresh")
        st.session_state.image_counter += 1
    else:
        st.session_state.image_counter = 0

    index = st.session_state.image_counter % len(weather_images)

    st.image(
        weather_images[index],
        use_container_width=True,
        caption=f"Live Weather Image (Update #{st.session_state.image_counter})"
    )

    st.divider()

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------
    st.title("🌍 ClimateScope Dashboard")
    st.subheader("Visualizing Global Weather Trends")
    st.success(f"Welcome {st.session_state.username} 👋")

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------
    @st.cache_data
    def load_data():
        # Get the correct path to the CSV file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        csv_path = os.path.join(parent_dir, "GlobalWeatherRepository.csv")
        return pd.read_csv(csv_path)

    try:
        df = load_data()
        st.success("✅ Dataset loaded successfully")
    except FileNotFoundError:
        st.error("❌ Error: GlobalWeatherRepository.csv not found")
        return
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return

    # --------------------------------------------------
    # USER CONTROLS
    # --------------------------------------------------
    st.header("🔘 User Controls")

    if "country" not in df.columns:
        st.error("❌ Error: 'country' column not found in dataset")
        return

    countries = sorted(df["country"].dropna().unique())
    if len(countries) == 0:
        st.error("❌ No country data available")
        return

    selected_country = st.selectbox("🌍 Select Country", countries)

    unit = st.radio("🌡 Temperature Unit", ["Celsius", "Fahrenheit"])

    temp_col = "temperature_celsius" if unit == "Celsius" else "temperature_fahrenheit"

    country_df = df[df["country"] == selected_country]

    if country_df.empty:
        st.warning(f"⚠️ No data available for {selected_country}")
        return

    st.subheader(f"📄 Data Preview – {selected_country}")
    st.dataframe(country_df.head(), use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # SMART WEATHER SUMMARY
    # --------------------------------------------------
    st.header("🧠 Smart Weather Summary")

    avg_temp = country_df[temp_col].mean()
    max_temp = country_df[temp_col].max()
    avg_wind = country_df["wind_kph"].mean()
    
    # Handle empty mode
    condition_mode = country_df["condition_text"].mode()
    common_condition = condition_mode[0] if len(condition_mode) > 0 else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡 Avg Temp", f"{avg_temp:.1f}")
    c2.metric("🔥 Max Temp", f"{max_temp:.1f}")
    c3.metric("💨 Avg Wind (km/h)", f"{avg_wind:.1f}")
    c4.metric("☁ Common Weather", common_condition)

    # --------------------------------------------------
    # EXTREME WEATHER ALERTS
    # --------------------------------------------------
    if unit == "Celsius" and max_temp > 35:
        st.error("🚨 Heat Alert: Extremely high temperature detected!")

    if avg_wind > 30:
        st.warning("⚠️ Strong wind conditions observed")

    st.divider()

    # --------------------------------------------------
    # TEMPERATURE TREND
    # --------------------------------------------------
    if st.checkbox("📈 Show Temperature Trend"):
        st.subheader("Temperature Trend Over Time")
        if "last_updated" in country_df.columns:
            trend_df = country_df.sort_values("last_updated")
            st.line_chart(trend_df.set_index("last_updated")[temp_col])
        else:
            st.warning("⚠️ 'last_updated' column not found")

    # --------------------------------------------------
    # WEATHER CONDITION DISTRIBUTION
    # --------------------------------------------------
    st.subheader("☁ Weather Condition Distribution")
    condition_counts = country_df["condition_text"].value_counts()
    st.bar_chart(condition_counts)

    # --------------------------------------------------
    # AUTO INSIGHT
    # --------------------------------------------------
    st.info(
        f"📌 Insight: {selected_country} experiences an average temperature of "
        f"{avg_temp:.1f}°{unit[0]} with predominantly "
        f"{common_condition.lower()} conditions."
    )

    st.divider()

    # --------------------------------------------------
    # DATASET OVERVIEW
    # --------------------------------------------------
    st.header("📊 Dataset Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Rows", df.shape[0])
    c2.metric("Total Columns", df.shape[1])
    c3.metric("Missing Values", df.isnull().sum().sum())

    # --------------------------------------------------
    # LOGOUT
    # --------------------------------------------------
    if st.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.image_counter = 0
        st.rerun()

    st.markdown("---")
    st.markdown("📘 **ClimateScope – Milestone 1 Web Application**")

# --------------------------------------------------
# PAGE CONTROLLER
# --------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
>>>>>>> 8ca6fe5a824cfeeae6975d0a3bf3f43e7cc68365:main.py
    auth_page()