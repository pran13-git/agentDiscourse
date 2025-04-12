import streamlit as st
from main import run_debate
import traceback

st.set_page_config(page_title="AI Debate", page_icon="🧠", layout="centered")

st.title("AI Debate")
st.markdown("Engage two AI personas in a discussion and see if they reach common ground.")

with st.form("debate_form"):
    topic = st.text_input("Debate Topic", value="Should social media be regulated more strictly?")

    col1, col2 = st.columns(2)
    with col1:
        personality1 = st.text_input("Personality 1", value="Skeptic")
    with col2:
        personality2 = st.text_input("Personality 2", value="Optimist")

    submitted = st.form_submit_button("Start Debate")

if submitted:
    with st.spinner("🤖 Warming up the agents and starting debate... Please wait."):
        try:
            # Run the debate with internal retry handling
            debate_result = run_debate(topic, personality1, personality2)

            st.success("Debate complete!")

            st.divider()
            st.subheader("Debate Transcript")

            for turn in debate_result["transcript"]:
                speaker = personality1 if turn["speaker"] == "agent1" else personality2

                st.markdown(
                    f"<div style='margin-bottom:0.25rem'><strong style='font-size: 1.25rem'>{speaker}:</strong></div>"
                    f"<div style='margin-bottom:1.5rem; font-size: 1.05rem'>{turn['text']}</div>",
                    unsafe_allow_html=True
                )

            st.divider()
            st.subheader("Convergence Evaluation")
            st.write(debate_result["evaluation"])

            st.subheader("Final Summary")
            st.write(debate_result["summary"])

        except Exception as e:
            st.error("Oops! The debate failed due to a timeout or an API issue.")
            with st.expander("See error details"):
                st.text(traceback.format_exc())
