import streamlit as st
import pandas as pd
from openai import OpenAI
from streamlit.runtime.uploaded_file_manager import UploadedFile

# ==============================================================================
# CONFIGURATION AND CONSTANTS
# ==============================================================================

AVAILABLE_DOMAINS: list[str] = ["Fitness",
                                "Travel", "Biology", "Personal Finance"]

PREBUILT_QUESTIONS: dict[str, list[str]] = {
    "Fitness": [
        "Create a beginner workout plan",
        "What should I eat before training?",
        "How do I stay consistent with fitness?",
        "How much protein do I need daily?"
        "How many exercies should I do per session?"
    ],
    "Travel": [
        "Plan a 1-day city itinerary",
        "What are the best budget travel tips?",
        "How do I stay safe while traveling solo?",
        "What should I pack for international travel?"
    ],
    "Biology": [
        "Explain how photosynthesis works",
        "What is the difference between mitosis and meiosis?",
        "How does the immune system fight infections?",
        "What are the main functions of DNA?"
    ],
    "Personal Finance": [
        "How do I create a monthly budget?",
        "What should I know about investing?",
        "How do I build an emergency fund?",
        "Explain compound interest"
    ]
}

TONE_OPTIONS: list[str] = ["Friendly", "Professional", "Casual"]
LENGTH_OPTIONS: list[str] = ["Brief", "Moderate", "Detailed"]
AUDIENCE_OPTIONS: list[str] = ["Beginner", "Intermediate", "Advanced"]

REQUIRED_CSV_COLUMNS: list[str] = ["topic", "information"]


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def is_setup_complete() -> bool:
    """Returns True if both domain and knowledge base are configured."""
    return (
        st.session_state.selected_domain is not None
        and st.session_state.knowledge_base is not None
    )


def render_setup_status() -> None:
    """
    Shows a status bar indicating completed setup steps.
    If setup is incomplete, shows a message pointing to the Setup tab.
    """
    domain_done: bool = st.session_state.selected_domain is not None
    kb_done: bool = st.session_state.knowledge_base is not None

    if domain_done and kb_done:
        st.success(
            f"Ready — Domain: **{st.session_state.selected_domain}** | "
            f"Knowledge Base: **{st.session_state.uploaded_filename}**"
        )
    else:
        missing: list[str] = []
        if not domain_done:
            missing.append("select a domain")
        if not kb_done:
            missing.append("upload a knowledge base")
        st.warning(f"Go to the **Setup** tab to {' and '.join(missing)}.")


# ==============================================================================
# CORE FUNCTIONS
# ==============================================================================

def load_knowledge_base(uploaded_file: UploadedFile) -> str:
    """
    Loads and validates a CSV knowledge base file.

    Args:
        uploaded_file: A Streamlit UploadedFile object containing CSV data.

    Returns:
        A formatted string with all knowledge base content, or an error
        message starting with "Error:" if loading fails.
    """
    try:
        # Reset file position
        if uploaded_file is not None:
            uploaded_file.seek(0)

        # Read CSV to a DataFrame
        df: pd.DataFrame = pd.read_csv(uploaded_file)

        # Validate: Required columns are present
        for col in REQUIRED_CSV_COLUMNS:
            if col not in df.columns:
                return f"Error: CSV is missing required column '{col}'!"

        # Check: CSV file empty or not
        if df.empty:
            return "Error: No data rows!"

        # Iterate through rows + build formatted string
        knowledge_base = ""
        for _, row in df.iterrows():
            knowledge_base += f"Topic: {row['topic']}\nInformation: {row['information']}\n\n"

        return knowledge_base

    except pd.errors.EmptyDataError:
        return "Error: The CSV file is empty."
    except pd.errors.ParserError as e:
        return f"Error parsing CSV: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


def build_prompt(
    domain: str,
    knowledge_base: str,
    tone: str,
    length: str,
    audience: str,
    user_question: str
) -> str:
    """
    Builds the full prompt to send to the AI, incorporating the domain,
    knowledge base, style preferences, and user question.

    Args:
        domain: The selected specialty domain (e.g. "Fitness").
        knowledge_base: The full knowledge base text from the CSV.
        tone: The desired response tone (e.g. "Friendly").
        length: The desired response length (e.g. "Moderate").
        audience: The target audience level (e.g. "Beginner").
        user_question: The user's question to answer.

    Returns:
        A complete prompt string ready to send to the AI API.
    """
    return f"""
    You are a {domain} expert.

    RULES:
    Only answer questions about {domain}. If asked about other topics,
    politely decline.

    KNOWLEDGE BASE:
    {knowledge_base}

    STYLE:
    - Tone: {tone}
    - Length: {length}
    - Audience: {audience}

    QUESTION:
    {user_question}

    Answer based ONLY on the knowledge base above.
    """


def get_ai_response(prompt: str) -> str:
    """
    Sends a prompt to the OpenAI API and returns the response.

    Args:
        prompt: The complete prompt string to send to OpenAI.

    Returns:
        The AI's response text, or an error message if the call fails.
    """
    try:
        if not st.session_state.get("openai_api_key"):
            return "Error: No API key provided."

        # Create a client with OpenAI key
        client: OpenAI = OpenAI(api_key=st.session_state.get("openai_api_key"))

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"


# ==============================================================================
# TAB RENDERING FUNCTIONS
# ==============================================================================

def render_setup_tab() -> None:
    """Renders the Setup tab for domain selection and knowledge base upload."""
    st.header("Setup")

    # Initialize the selected_domain key if not found
    if "selected_domain" not in st.session_state:
        st.session_state.selected_domain = AVAILABLE_DOMAINS[0]

    # Display the widget and link it to th selected_domain key
    st.radio("Domains:", AVAILABLE_DOMAINS, key="selected_domain")

    st.markdown("---")

    # Upload file (csv - restricted)
    uploaded_file = st.file_uploader(
        "Upload a file", type=["csv"], help="Select a CSV file", key="input_file"
    )

    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Save the filename string to state
        st.session_state.uploaded_filename = uploaded_file.name
        knowledge_base_result = load_knowledge_base(uploaded_file)

        # Check for Errors and display, otherwise store in session state with success feedback
        if "error" in knowledge_base_result.lower():
            st.error(knowledge_base_result)
        else:
            st.session_state.knowledge_base = knowledge_base_result
            st.success(
                f"'{st.session_state.uploaded_filename}': file uploaded successfully")

        # Preview Expander
        with st.expander("Preview Knowledge Base"):
            st.text(st.session_state.knowledge_base)


def render_chat_tab() -> None:
    """Renders the Chat tab for submitting questions and displaying AI responses."""
    # st.session_state.last_tab = "chat"/////////////////////////////////////////////

    # Check if setup is configured
    render_setup_status()
    if not is_setup_complete():
        return

    st.markdown("---")

    # Get user question
    st.text_input(
        "Question:",
        value=st.session_state.get("_chat_question", ""),
        placeholder=f"Ask anything about {st.session_state.selected_domain}...",
        key="chat_question"
    )

    # Get style inputs
    with st.expander("Response style options"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.selectbox("Tone:", TONE_OPTIONS, key="tone")
        with col2:
            st.selectbox("Length:", LENGTH_OPTIONS, key="length")
        with col3:
            st.selectbox("Audience:", AUDIENCE_OPTIONS, key="audience")

    # Get Answer btn action - API call
    if st.button("Get Answer", type="primary"):
        st.session_state.answer = None

        question = st.session_state.chat_question
        if question.strip():
            prompt = build_prompt(
                domain=st.session_state.selected_domain,
                knowledge_base=st.session_state.knowledge_base,
                tone=st.session_state.tone,
                length=st.session_state.length,
                audience=st.session_state.audience,
                user_question=question
            )
            with st.spinner("Processing..."):
                st.session_state.answer = get_ai_response(prompt)
        else:
            return

    # Display Q&A if there's an answer already generated (last questions & answer)
    if "answer" in st.session_state and st.session_state.answer:
        st.divider()
        st.write(f"Question: {st.session_state.chat_question}")
        st.write(f"Answer: {st.session_state.answer}")


def render_quick_questions_tab() -> None:
    """Renders the Quick Questions tab with domain-specific preset questions."""

    # Set a default value for the active question
    if "chat_question" not in st.session_state:
        st.session_state.chat_question = None

    # Check if setup is configured
    render_setup_status()
    if not is_setup_complete():
        return

    st.caption(f"""
        Here are some Prebuilt {st.session_state.selected_domain} Questions for you to get started!\n
        Please select one and get the answer from the - Chat Tab.
        """)

    questions = PREBUILT_QUESTIONS.get(st.session_state.selected_domain, [])

    def select_question(q: str) -> None:
        st.session_state.chat_question = q

    for question in questions:
        # Check if THIS specific question is the active one
        # Change the style: secondary -> primary of the selected button to look "active"
        is_active = (st.session_state.chat_question == question)
        btn_type = "primary" if is_active else "secondary"

        st.button(question, key=f"preset_{st.session_state.selected_domain}_{question}",
                  on_click=select_question, args=(question,), type=btn_type)

        # Information text asking user to procced to the chat tab once a question is selected
        if is_active:
            st.info("Question selected. Please proceed to - Chat Tab")


# ==============================================================================
# APP ENTRY POINT
# ==============================================================================

def initialize_session_state() -> None:
    """Initializes all session state variables with default values."""
    defaults: dict[str, str | None] = {
        "selected_domain": None,
        "knowledge_base": None,
        "uploaded_filename": None,
        "last_question": None,
        "last_answer": None,
        "openai_api_key": None,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def main() -> None:
    """Main application entry point. Sets up the page and renders all tabs."""
    st.title("Domain Q&A Assistant")
    st.caption(
        "A specialist assistant that only answers questions within its selected domain")

    initialize_session_state()

    # Sidebar: API key input
    with st.sidebar:
        st.header("Settings")
        st.text_input(
            "OpenAI API Key",
            type="password",
            key="openai_api_key",
            help="Enter your OpenAI API key to get real AI responses"
        )

    # Setup tab is first so users complete it before chatting
    tab_setup, tab_chat, tab_quick = st.tabs(
        ["Setup", "Chat", "Quick Questions"])

    with tab_setup:
        render_setup_tab()

    with tab_chat:
        render_chat_tab()

    with tab_quick:
        render_quick_questions_tab()


if __name__ == "__main__":
    main()
