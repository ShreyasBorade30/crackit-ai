from groq import Groq
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import time


st.set_page_config(page_title="Streamlit Chat", page_icon="")
st.title(" CrackIT AI 🚀")


placeholder = st.empty()
text = "by Shreyas B"
cursor = "<span style='opacity:0.5;'>|</span>"

typed = ""
for char in text:
    typed += char
    placeholder.markdown(
        f"""
        <pre style="
            font-family: 'Courier New', monospace;
            font-size: 22px;
            font-weight: 700;
            color: #00eaff;
            text-shadow: 0px 0px 8px #00eaff;
            margin: 0;
        ">{typed}{cursor}</pre>
        """,
        unsafe_allow_html=True
    )
    time.sleep(0.05)

placeholder.markdown(
    f"""
    <pre style="
        font-family: 'Courier New', monospace;
        font-size: 22px;
        font-weight: 700;
        color: #00eaff;
        text-shadow: 0px 0px 8px #00eaff;
        margin: 0;
    ">{text}</pre>
    """,
    unsafe_allow_html=True
)


if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False

if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0

if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
    
if "messages" not in st.session_state:
    st.session_state.messages =[]

if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False  

def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

if not st.session_state.setup_complete:

    st.subheader('Personal information', divider = 'rainbow')

    if "name" not in st.session_state:
        st.session_state["name"]=""
    if "experience" not in st.session_state:
        st.session_state["experience"]=""
    if "skills" not in st.session_state:
        st.session_state["skills"]=""

    st.session_state["name"] = st.text_input(label = "Name", max_chars =40,value = st.session_state["name"] ,placeholder = "Enter your name")

    st.session_state["experience"] = st.text_area(label = "Experience", value=st.session_state["experience"], height = None, max_chars=200, placeholder = "Describe your experience")

    st.session_state["skills"] = st.text_area(label = "Skills", value= st.session_state["skills"], height = None, max_chars=200, placeholder = "List your skills")

    st.subheader('Company and Position', divider = 'rainbow')

    if "level" not in st.session_state:
        st.session_state["level"]="Junior"
    if "position" not in st.session_state:
        st.session_state["position"]="Data Scientist"
    if "comapany" not in st.session_state:
        st.session_state["company"]="Amazon"

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["level"] = st.radio(
        "Choose level",
        key="visibility",
        options=["Junior","Mid-level","Senior"]
        )

    with col2:
        st.session_state["position"] = st.selectbox(
        "Choose a position",
        ("Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst", "AI Engineer")
        )

    st.session_state["company"] = st.selectbox(
        "Choose a Company",
        ("Amazon", "Meta", "Google", "Udemy", "Microsoft", "Netflix")
        )

    st.write(f"**Your are interviewing for**: {st.session_state['company']} {st.session_state['position']} at {st.session_state['company']}")

    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup complete, Starting interview...")

if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:

    st.info(
        """
        Start by introducing yourself!
        """,
        icon = "😊"
    )

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    if "groq_model" not in st.session_state:
        st.session_state["groq_model"] = "llama-3.1-8b-instant"

    if not st.session_state.messages:
        st.session_state.messages = [
            {
                "role": "system",
                "content": (
                    f"You are an HR executive that interviews an interviewee called {st.session_state['name']}. "
                    f"With experience {st.session_state['experience']} and skills {st.session_state['skills']}. "
                    f"You should interview him for the position {st.session_state['level']} {st.session_state['position']} "
                    f"at the company {st.session_state['company']}."
                )
            }
        ]



    def stream_groq_response(stream):
        full_response = ""
        for chunk in stream:
            delta = chunk.choices[0].delta

            if delta and delta.content:
                token = delta.content
                full_response += token
                yield token   # stream token-by-token

        return full_response

    if st.session_state.user_message_count < 5 :
        if prompt := st.chat_input("Your answer.", max_chars = 1000):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)
            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model=st.session_state["groq_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )

                    # FIXED: use custom stream handler
                    response = st.write_stream(stream_groq_response(stream))

                st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.user_message_count += 1

    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click = show_feedback):
        st.write("Fetching Feedback...")

if st.session_state.feedback_shown:
    st.subheader("Feedback")

    conversation_history = "\n\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages]
    )

    feedback_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    feedback_completion = feedback_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system",
             "content": """You are a helpful tool that provides feedback on an interviewee performance.
             Before the feedback, give a score of 1 to 10.
             Follow this format:
             Overall Score: // Your score  
             Feedback: // Here you put your feedback
             Give ONLY the feedback. Do NOT ask any additional questions.
             """},
            {
                "role": "user",
                "content": f"This is the interview you need to evaluate. Keep in mind that you are only a tool. And you should only provide a score and feedback:\n\n{conversation_history}"
            }
        ]
    )

    st.write(feedback_completion.choices[0].message.content)

    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
