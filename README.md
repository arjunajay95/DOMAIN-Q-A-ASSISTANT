# Domain Q&A Assistant 🤖

A focused AI assistant that stays in its lane. You pick a domain, upload your own knowledge base, and ask questions. It answers within the constraints of what you gave it, nothing else.

Try it live 👉 **[Live Demo](https://domain-q-a-assistant-app.streamlit.app/)**

<br>

## Technologies & Libraries 🛠️

| Tools                                                                                                          | Purpose                                |
| -------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)          | Core language                          |
| ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white) | UI and session state management        |
| ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)          | (`gpt-4o-mini`) AI response generation |
| ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)          | CSV parsing and validation             |

<br>

## Features ✨

- **Domain locking.** The assistant only answers questions about the domain you've selected. Ask it something off-topic and it'll politely decline. No hallucinated answers from outside the scope.
- **Bring your own knowledge base.** Upload a CSV with `topic` and `information` columns and the assistant uses that as its source of truth.
- **Response style controls.** Adjust tone (Friendly, Professional, Casual), length (Brief, Moderate, Detailed), and audience level (Beginner, Intermediate, Advanced) before hitting send.
- **Quick Questions tab.** Pre-built starter questions for each domain so you don't have to start from scratch.
- **Knowledge base preview.** Expand and inspect your uploaded CSV right in the UI before asking anything.
- **Setup status bar.** Every tab tells you clearly if something's missing before you try to use it.

<br>

## The Process & Design Decisions ⚙️

The app is split into four clear layers: configuration/constants, helper functions, core logic, and tab rendering. That separation made the code easy to reason about and easy to change.

**Why tab-based layout?** The setup has to happen before anything else works. Putting it in its own tab makes the flow obvious. Users land on Setup, configure things, then move to Chat or Quick Questions. It's a natural left-to-right progression.

**Why session state everywhere?** Streamlit reruns the entire script on every interaction. Session state is what keeps things like the selected domain, the loaded knowledge base, and the last answer from disappearing on every click. Most of the early architectural decisions came down to figuring out exactly what needed to persist and where.

**Why validate the CSV on upload?** Failing early is better than failing mid-conversation. If the CSV file is missing a required column or is empty, you find out immediately at the upload step, not when you're already three questions in.

**Why `build_prompt()` as a separate function?** The prompt is the most important part of this whole thing. Keeping it isolated meant it was easy to tweak, test, and read. It takes all the style preferences and knowledge base content and assembles them cleanly, so `get_ai_response()` just has to fire the API call.

**Why the Quick Questions tab?** A blank text input is intimidating if you don't know what the knowledge base contains. The preset questions give users a starting point and double as a demonstration of what the assistant can actually do.

<br>

## What I Learned 📚

This project was less about building something complex and more about building something clean. A few things stuck with me.

**Session state management in Streamlit is its own skill.** The reactive model where every interaction reruns the script feels counterintuitive at first. Learning to be deliberate about what goes into session state, and when to initialize it, made the whole app more predictable.

**Prompt structure matters a lot.** Small changes to how the prompt is worded, what rules you give the model, and how you format the knowledge base all change the quality of responses noticeably. The domain-locking instruction especially, telling the model to decline off-topic questions, works well but only because it's stated clearly and directly.

**Good UX in data apps is mostly about clear feedback.** The status bar, the CSV validation errors, the "question selected, proceed to Chat" message on the Quick Questions tab, none of that is complicated code. But without it, users just get confused. Feedback is underrated.

<br>

## How It Can Be Improved 🚀

- **Multi-turn conversation.** Right now it's one question, one answer. Adding a proper chat history would make it feel much more like a real assistant.
- **Support more file types.** Right now only CSVs work. Supporting plain text files or PDFs would make the knowledge base much easier to build.
- **Better error messages.** The CSV validation catches common problems but could be more specific about what's wrong and how to fix it.
- **Conversation history export.** A download button for the Q&A session would be genuinely useful for people using this in a study or research context.
- **Model selection.** Currently hardcoded to `gpt-4o-mini`. Letting users pick the model would give them more control over cost vs. quality tradeoffs.

<br>

## Running It Locally 🖥️

### Prerequisites

- Python 3.14+
- An OpenAI API key

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/arjunajay95/DOMAIN-Q-A-ASSISTANT.git
cd DOMAIN-Q-A-ASSISTANT

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install streamlit openai pandas

# 4. Run the app
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

### Your CSV knowledge base needs two columns:

```
topic,information
Protein,Protein is essential for muscle repair and growth...
Cardio,Cardio training improves heart health and endurance...
```

Drop your OpenAI API key into the sidebar and you're good to go.

---

<br>
<p align="center">Built with Python3, Pandas, OpenAI and Streamlit &nbsp;·&nbsp; Arjuna Jayasinghe &nbsp;·&nbsp; Domain QA Assistant © 2026</p>
