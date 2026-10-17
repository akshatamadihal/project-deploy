
import streamlit as st
from auth import get_connection


def update_profile(user_id, name):
    name = name.strip()

    if not name or len(name) > 60:
        return False, "Name must contain 1–60 characters."

    with get_connection() as conn:
        result = conn.execute(
            "UPDATE users SET name = ? WHERE id = ?",
            (name, user_id)
        )

    if result.rowcount == 1:
        return True, "Profile updated successfully!"

    return False, "Unable to update your profile."


def show_profile():
    user = st.session_state.get("current_user")

    if not user:
        st.warning("Please log in to view your profile.")
        return

    st.title("👤 My EcoScan Profile")
    st.write("Manage your account information.")

    st.markdown("### Account details")

    with st.container(border=True):
        st.markdown(f"**Email:** {user['email']}")
        st.markdown(f"**User ID:** {user['id']}")

        with st.form("profile_form"):
            name = st.text_input(
                "Display name",
                value=user["name"],
                max_chars=60
            )

            submitted = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if submitted:
                success, message = update_profile(
                    user["id"], name
                )

                if success:
                    st.session_state["current_user"]["name"] = (
                        name.strip()
                    )
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    st.divider()

    st.markdown("### Account session")
    st.write("Log out when you finish using EcoScan.")

    if st.button("🚪 Logout", type="primary"):
        st.session_state.pop("current_user", None)
        st.session_state.pop("eco_messages", None)
        st.session_state.pop("last_eco_analysis", None)
        st.rerun()
