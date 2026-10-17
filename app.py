
import streamlit as st

from auth import init_db, show_auth
from profile import show_profile
from chatbot import show_chatbot
from image_analysis import show_image_analysis
from reviews import show_reviews


st.set_page_config(
    page_title="EcoScan | Smart Sustainability",
    page_icon="🌿",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f0fdf4, #ffffff);
}

[data-testid="stSidebar"] {
    background-color: #123b2a;
}

[data-testid="stSidebar"] * {
    color: white;
}

.eco-hero {
    padding: 30px;
    border-radius: 18px;
    color: white;
    background: linear-gradient(120deg, #14532d, #16a34a);
    margin-bottom: 24px;
}

.eco-hero h1 {
    color: white;
}

.stButton > button {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# Create the database table if it does not exist.
init_db()

# Protect the main website behind login.
if not st.session_state.get("current_user"):
    show_auth()
    st.stop()


user = st.session_state["current_user"]

with st.sidebar:
    st.markdown("# 🌿 EcoScan")
    st.caption("Your sustainability companion")
    st.divider()

    st.write(f"Welcome, {user['name']}!"
             " Scan. Smile. Save the planet.")

    page = st.radio(
        "Navigate",
        [
            "🏠 Home",
            "🔍 Image Analysis",
            "💬 EcoChat",
            "⭐ Reviews",
            "👤 My Profile"
        ],
        key="main_navigation"
    )

    st.divider()
    st.caption("Reduce • Reuse • Recycle")


if page == "🏠 Home":
    st.markdown("""
    <div class="eco-hero">
        <h1>Welcome to EcoScan 🌿</h1>
        <p>Scan smarter. Recycle better. Protect our planet.</p>
        <p>Discover sustainable choices with the help of AI.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Explore your EcoScan dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔍 Image Analysis")
        st.write("Identify waste and explore disposal suggestions.")

        if st.button("Analyze Waste", use_container_width=True):
           
            show_image_analysis()
    with col2:
        st.markdown("### 💬 EcoChat")
        st.write("Ask questions about recycling and sustainability.")

        if st.button("Open EcoChat", use_container_width=True):
           show_chatbot()

    with col3:
        st.markdown("### ⭐ Reviews")
        st.write("Share your experience with EcoScan.so we provide you best service")

        if st.button("Write a Review", use_container_width=True):
            
            show_reviews()

    st.divider()
    st.subheader("🌎 Three simple ways to help")

    c1, c2, c3 = st.columns(3)
    c1.metric("Step 1", "Reduce", "Avoid unnecessary waste")
    c2.metric("Step 2", "Reuse", "Extend product life")
    c3.metric("Step 3", "Recycle", "Sort waste responsibly")

    st.info(
        "Tip: Recycling guidelines differ by location. "
        "Check your local municipal waste-management rules."
    )

elif page == "🔍 Image Analysis":
    show_image_analysis()

elif page == "💬 EcoChat":
    show_chatbot()

elif page == "⭐ Reviews":
    show_reviews()

elif page == "👤 My Profile":
    show_profile()
