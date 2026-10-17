
import os
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

REVIEW_FILE = "ecoscan_reviews.csv"

COLUMNS = [
    "date",
    "name",
    "rating",
    "review",
]


def load_reviews():
    if not os.path.exists(REVIEW_FILE):
        return pd.DataFrame(columns=COLUMNS)

    try:
        df = pd.read_csv(REVIEW_FILE)

        for column in COLUMNS:
            if column not in df.columns:
                df[column] = ""

        return df[COLUMNS].fillna("")

    except (OSError, pd.errors.ParserError, ValueError):
        st.warning("Unable to read the existing reviews file.")
        return pd.DataFrame(columns=COLUMNS)


def show_reviews():
    st.title("⭐ EcoScan Reviews")
    st.write(
        "Tell us what you think. Your feedback helps "
        "us improve the EcoScan experience."
    )

    with st.form("eco_review_form", clear_on_submit=True):
        name = st.text_input(
            "Your name (optional)",
            max_chars=60,
            placeholder="Enter your name"
        )

        rating = st.select_slider(
            "Rate your experience",
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda x: "⭐" * x
        )

        review = st.text_area(
            "Write your review",
            placeholder="What did you like or what can we improve?",
            max_chars=1000,
            height=120
        )

        submitted = st.form_submit_button(
            "Submit Review 🌿",
            type="primary",
            use_container_width=True
        )

        if submitted:
            if not review.strip():
                st.error("Please write a review before submitting.")
            else:
                new_review = pd.DataFrame([{
                    "date": datetime.now(timezone.utc).isoformat(
                        timespec="seconds"
                    ),
                    "name": name.strip() or "Anonymous",
                    "rating": rating,
                    "review": review.strip()
                }])

                try:
                    # Write the header only when creating a new file.
                    new_review.to_csv(
                        REVIEW_FILE,
                        mode="a",
                        header=not os.path.exists(REVIEW_FILE),
                        index=False,
                        encoding="utf-8"
                    )

                    st.success("Thank you for sharing your feedback! 💚")
                    st.rerun()

                except OSError:
                    st.error(
                        "The review could not be saved. "
                        "Check that the application folder is writable."
                    )

    st.divider()
    st.subheader("💬 Community Feedback")

    reviews_df = load_reviews()

    if reviews_df.empty:
        st.info(
            "No reviews yet. Be the first to share your experience!"
        )
        return

    reviews_df["rating"] = pd.to_numeric(
        reviews_df["rating"], errors="coerce"
    )
    valid_ratings = reviews_df["rating"].dropna()

    if not valid_ratings.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Average Rating",
                f"{valid_ratings.mean():.1f} / 5 ⭐"
            )

        with col2:
            st.metric("Total Reviews", len(reviews_df))

    sort_option = st.selectbox(
        "Sort reviews",
        ["Newest first", "Highest rating", "Lowest rating"]
    )

    if sort_option == "Newest first":
        reviews_df = reviews_df.iloc[::-1]
    elif sort_option == "Highest rating":
        reviews_df = reviews_df.sort_values(
            "rating", ascending=False
        )
    else:
        reviews_df = reviews_df.sort_values(
            "rating", ascending=True
        )

    for _, row in reviews_df.iterrows():
        with st.container(border=True):
            st.markdown(
                f"**{str(row['name'])[:60]}** · "
                f"{'⭐' * max(0, min(5, int(row['rating']))) if pd.notna(row['rating']) else 'No rating'}"
            )

            st.write(str(row["review"])[:1000])

            if row["date"]:
                st.caption(str(row["date"])[:19])
