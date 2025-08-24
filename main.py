import os
from io import BytesIO
from textwrap import dedent

from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

# ----------------------------
# Optional PDF export
# ----------------------------
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# Load environment variables
load_dotenv()


# ----------------------------
# Utilities & LLM setup
# ----------------------------
def _get_api_key() -> str:
    """Fetch API key from environment variables."""
    return os.getenv("GROQ_API_KEY") or os.getenv("key") or ""


@st.cache_resource(show_spinner=False)
def get_llm():
    """Load Groq LLM instance with API key."""
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError("Missing GROQ API key. Set GROQ_API_KEY (or 'key') in your .env")
    return ChatGroq(model="openai/gpt-oss-20b", groq_api_key=api_key)


def call_llm(prompt: str) -> str:
    """Call LLM with given prompt and return response text."""
    llm = get_llm()
    parser = StrOutputParser()
    chain = llm | parser
    return chain.invoke(prompt)


# ----------------------------
# Prompt Builders
# ----------------------------
def build_lesson_prompt(subject, topic, grade, duration,
    learning_objectives, customization,
    difficulty, language) -> str:
    """Build prompt for lesson plan generation."""
    difficulty_guidance = {
        "Easy": "Use simple language, foundational explainers, and concrete everyday examples.",
        "Medium": "Use balanced depth, some technical vocabulary, and 1–2 brief real-world examples.",
        "Hard": "Use advanced terminology, deeper conceptual links, and include extension tasks for high achievers.",
    }.get(difficulty, "Use balanced language and depth.")

    prompt = f"""
    You are an expert instructional designer and teacher. Create a detailed, classroom-ready LESSON PLAN.

    Constraints & format:
    - Write the ENTIRE output in {language}.
    - Tailor to grade/level: {grade}
    - Total duration: {duration}
    - Difficulty level: {difficulty}. {difficulty_guidance}
    - The lesson must be fun, practical, and interactive.
    - Return ONLY Markdown (no code fences). Use headings, bullets, and tables where helpful.

    Required sections (use clear Markdown headings):
    1. Title & Overview (1–2 sentences)
    2. Learning Objectives (bulleted, measurable)
    3. Required Materials (bulleted)
    4. Prior Knowledge (short)
    5. Lesson Flow with Time Boxes (table: Step | Time | What to do | Teacher notes)
    6. Interactive Activities (2–3 activities; include clear instructions)
    7. Differentiation & Accommodations (for mixed ability learners)
    8. Assessment (formative + one quick exit ticket)
    9. Homework or Extension
    10. Safety/Notes (if applicable)

    Subject: {subject}
    Topic: {topic}
    Learning Objectives: {learning_objectives}
    Customization request: {customization}
    """
    return dedent(prompt)


def build_quiz_prompt(lesson_plan_md, grade, language, difficulty, num_questions) -> str:
    """Build prompt for quiz generation based on lesson plan."""
    prompt = f"""
    You are an assessment designer. Based ONLY on the lesson plan content below, create a quiz.

    - Number of questions: {num_questions}
    - Difficulty: {difficulty}
    - Grade/Level: {grade}
    - Language: {language}
    - Mix question types: multiple choice, short answer, and 1 challenge question.
    - For multiple choice, include 4 options labeled A–D.
    - Provide an **Answer Key** at the end under a collapsible details block.
    - Return the quiz as clean Markdown (no code fences).

    LESSON PLAN START
    ---
    {lesson_plan_md}
    ---
    LESSON PLAN END
    """
    return dedent(prompt)


# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="AI Lesson Planner Plus", page_icon="🗓️", layout="wide")
st.title("🗓️ AI Lesson Planner Plus")
st.caption("Generate polished, classroom-ready lesson plans with quizzes. Powered by Groq + LangChain.")

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Settings")
    language = st.selectbox("Output language", ["English", "Urdu", "Arabic", "French", "Spanish"], index=0)
    difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"], value="Medium")
    num_questions = st.slider("Quiz questions", min_value=3, max_value=15, value=7, step=1)
    use_example = st.toggle("Use example inputs", value=False, help="Prefill fields for a quick demo")

    # 💡 Tips Section
    with st.expander("ℹ️ Click for Tips"):
        st.write(
            "- Select **output language** (e.g., Urdu, English).\n"
            "- Choose the **difficulty level**.\n"
            "- Adjust the number of **quiz questions**.\n"
            "- Click **Generate Lesson Plan**.\n"
            "- Use **Download buttons** to save (Markdown, TXT, PDF).\n"
            "- Press **Reset** to start fresh."
        )


# ----------------------------
# Inputs
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    subject = st.text_input("Subject", value=("Science" if use_example else ""))
    topic = st.text_input("Topic", value=("The Solar System" if use_example else ""))
    grade = st.text_input("Grade / Level", value=("5" if use_example else ""))
    duration = st.text_input("Duration", value=("1 hour" if use_example else ""))

with col2:
    learning_objectives = st.text_area(
        "Learning Objectives (measurable outcomes)",
        value=(
            "Students will be able to list the eight planets, describe their order from the sun, "
            "and compare two planets by size and composition." if use_example else ""
        ),
        height=120,
    )
    customization = st.text_area(
        "Customization (tone, activities, classroom context)",
        value=("Make it fun and interactive with a quick game and a hands-on mini-model activity." if use_example else ""),
        height=120,
    )


# ----------------------------
# Lesson Plan Generator
# ----------------------------
generate = st.button("✨ Generate Lesson Plan", type="primary")

if generate:
    if not all([subject, topic, grade, duration, learning_objectives]):
        st.warning("⚠️ Please fill out Subject, Topic, Grade, Duration, and Learning Objectives.")
    else:
        with st.spinner("Generating lesson plan…"):
            try:
                prompt = build_lesson_prompt(subject, topic, grade, duration,
                                             learning_objectives, customization,
                                             difficulty, language)
                lesson_md = call_llm(prompt)
                st.session_state["lesson_md"] = lesson_md
                st.session_state.pop("quiz_md", None)  
            except Exception as e:
                st.error(f"LLM error: {e}")


# ----------------------------
# Display Lesson Plan & Actions
# ----------------------------
if "lesson_md" in st.session_state:
    st.subheader("📘 Lesson Plan")
    st.markdown(st.session_state["lesson_md"])

    # Quiz Generator
    st.divider()
    st.subheader("🧠 Quiz Generator")

    if st.button("Create Quiz from this Lesson"):
        with st.spinner("Generating quiz…"):
            try:
                quiz_prompt = build_quiz_prompt(
                    st.session_state["lesson_md"], grade, language, difficulty, num_questions
                )
                quiz_md = call_llm(quiz_prompt)
                st.session_state["quiz_md"] = quiz_md
            except Exception as e:
                st.error(f"LLM error: {e}")

    if "quiz_md" in st.session_state:
        st.markdown("### 📝 Quiz")
        st.markdown(st.session_state["quiz_md"])

    # Export Options
    st.divider()
    st.subheader("📥 Export")

    # Download Markdown
    md_bytes = st.session_state["lesson_md"].encode("utf-8")
    st.download_button("Download Lesson (Markdown)", data=md_bytes,
                       file_name="lesson_plan.md", mime="text/markdown")

    # Download TXT
    txt_bytes = st.session_state["lesson_md"].encode("utf-8")
    st.download_button("Download Lesson (TXT)", data=txt_bytes,
                       file_name="lesson_plan.txt", mime="text/plain")

    # Download PDF (if available)
    if REPORTLAB_AVAILABLE:
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer)
            styles = getSampleStyleSheet()
            story = []

            # Convert Markdown newlines into Paragraph-friendly format
            text = st.session_state["lesson_md"].replace("\n\n", "<br/><br/>").replace("\n", "<br/>")
            story.append(Paragraph(text, styles["BodyText"]))
            story.append(Spacer(1, 12))

            doc.build(story)
            buffer.seek(0)

            st.download_button("Download Lesson (PDF)", data=buffer,
                               file_name="lesson_plan.pdf", mime="application/pdf")
        except Exception as e:
            st.info("⚠️ PDF export encountered an issue. You can still download Markdown/TXT.")
            st.caption(f"Details: {e}")

    # Reset Button (only after output exists)
    st.divider()
    if st.button("🔄 Reset for New Work"):
        st.session_state.clear()
        st.rerun()
