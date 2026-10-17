
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error(
            "Gemini API key is missing. Add GEMINI_API_KEY "
            "to your .env file and restart Streamlit."
        )
        return None
    return genai.Client(api_key=api_key)


def show_chatbot():
    st.title("💬 EcoChat")
    st.write(
        "Ask me about recycling, composting, pollution, "
        "climate change, and sustainable living."
    )

    if "eco_messages" not in st.session_state:
        st.session_state.eco_messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! 🌿 I'm EcoChat. How can I help "
                    "you make a more sustainable choice today?"
                )
            }
        ]

    with st.sidebar:
        if st.button("🗑️ Clear Chat", key="clear_eco_chat"):
            st.session_state.eco_messages = []
            st.rerun()

    for message in st.session_state.eco_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask your environmental question...")

    if prompt:
        st.session_state.eco_messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        client = get_client()

        if client is None:
            return

        # Only send the latest conversation history.
        history = st.session_state.eco_messages[-12:]

        conversation = "\n".join(
            f'{m["role"]}: {m["content"]}'
            for m in history
        )

        instructions = """
        You are EcoChat, a helpful sustainability assistant.
        Answer in clear, friendly language.
        Give practical advice about waste segregation,
        recycling, composting, pollution and the environment.
        Never claim that a material is recyclable everywhere.
        Mention that local waste-management rules can differ.
        If uncertain, explain the uncertainty.
        """

        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking green... 🌱"):
                    response = client.models.generate_content(
                        model=MODEL,
                        contents=conversation,
                        config=types.GenerateContentConfig(
                            system_instruction=instructions,
                            temperature=0.5,
                            max_output_tokens=900,
                        ),
                    )

                    answer = response.text or (
                        "I couldn't generate a response. "
                        "Please try asking another question."
                    )

                    st.markdown(answer)

            st.session_state.eco_messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as exc:
            st.error(
                "EcoChat couldn't reach Gemini. "
                "Please try again in a moment."
            )
            print(f"EcoChat API error: {exc}")
