import streamlit as st
import uuid
from langgraph.types import Command
from models.llms import create_llm
from linkedin_post_generator2 import app

st.set_page_config(page_title="LinkedIn Post Generator", page_icon="💼")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("💼 LinkedIn Post Generator")
st.write("Generate polished and engaging LinkedIn posts instantly using AI.")

# Sidebar
st.sidebar.header("Configuration")
temperature = st.sidebar.slider("Creativity (Temperature)", 0.0, 1.0, 0.3)

for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"]) 


linkedin_topic = st.chat_input("Enter LinkedIn Topic (e.g. AI in Education)")


def _process_stream_until_interrupt(thread_config, initial_state):
    """Run the langraph stream until we hit an interrupt or finish.
    Updates session state with latest model output and whether we're waiting for feedback.
    """
    # Ensure flags exist
    st.session_state.waiting_for_feedback = False
    st.session_state.finished = False

    for chunk in app.stream(initial_state, thread_config):
        for node_id, value in chunk.items():
            if node_id == "model":
                st.session_state.generated_post = value["generated_post"][-1].content
            elif node_id == "__interrupt__":
                # Pause the loop and ask user for feedback
                st.session_state.waiting_for_feedback = True
                return

    # If we finished the stream without an interrupt
    st.session_state.waiting_for_feedback = False
    st.session_state.finished = True


# Buttons / actions
if "thread_config" not in st.session_state:
    st.session_state.thread_config = None
if "generated_post" not in st.session_state:
    st.session_state.generated_post = None
if "waiting_for_feedback" not in st.session_state:
    st.session_state.waiting_for_feedback = False
if "finished" not in st.session_state:
    st.session_state.finished = False



if not linkedin_topic:
    st.warning("Please enter a topic first.")
else:
    st.info("Generating your LinkedIn post...")
    st.chat_message("user").write(linkedin_topic)
    st.session_state.chat_history.append({"role": "user", "content": linkedin_topic})

    llm = create_llm(temperature=temperature)

    thread_config = {"configurable": {"thread_id": uuid.uuid4()}}
    st.session_state.thread_config = thread_config

    initial_state = {
            "linkedin_topic": linkedin_topic,
            "generated_post": [],
            "human_feedback": []
    }

    _process_stream_until_interrupt(thread_config, initial_state)


# Show generated or updated post if available
if st.session_state.generated_post:
    st.subheader("✨ Generated LinkedIn Post")
    st.write(st.session_state.generated_post)

# If langraph asked for feedback, show a single text_input + button to submit it
if st.session_state.waiting_for_feedback and st.session_state.thread_config:
    feedback_key = f"feedback_{st.session_state.thread_config['configurable']['thread_id']}"
    user_feedback = st.text_input("Enter feedback or type 'done' if finished:", key=feedback_key)
    if st.button("Submit feedback"):
        if user_feedback:
            result = app.invoke(Command(resume=user_feedback), config=st.session_state.thread_config)
            # If invoke returned a model update, show it
            if "model" in result:
                st.session_state.generated_post = result["model"]["generated_post"][-1].content
            # If user finished, mark finished and clear waiting flag
            if user_feedback.lower() in ["done", "d"]:
                st.session_state.waiting_for_feedback = False
                st.session_state.finished = True
            else:
                # Continue processing the stream until next interrupt or finish
                # Pass an empty state here since langraph keeps the thread internally
                _process_stream_until_interrupt(st.session_state.thread_config, {})

# When finished, add assistant message and offer download
if st.session_state.finished and st.session_state.generated_post:
    st.session_state.chat_history.append({"role": "assistant", "content": st.session_state.generated_post})
    st.download_button("Download Post as Text", st.session_state.generated_post, file_name="linkedin_post.txt")



        