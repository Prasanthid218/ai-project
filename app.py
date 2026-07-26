import streamlit as st
import PyPDF2
import re
from collections import Counter
import random
import time
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
load_dotenv("keys.env")

api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

def ai_generate(prompt):

    try:
        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.4,
            max_tokens=900
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ AI Error:\n\n{str(e)}"
def ai_summary(text, mode):

    if mode == "Detailed":
        prompt = f"""
Generate a detailed summary.

Rules:
- Explain every important concept.
- 10-12 bullet points.
- Student-friendly language.

Content:
{text}
"""

    elif mode == "Smart Summary":
        prompt = f"""
Generate a smart summary.

Rules:
- Only 5 important bullet points.
- Short and crisp.
- Revision friendly.

Content:
{text}
"""

    elif mode == "Exam Notes":
        prompt = f"""
Generate exam notes.

Rules:
- Use headings.
- Use bullet points.
- Highlight important keywords.
- No paragraphs.

Content:
{text}
"""

    elif mode == "Beginner":
        prompt = f"""
Explain this topic like a teacher explaining to a beginner.

Rules:
- Very simple English.
- Give examples.
- Easy to understand.

Content:
{text}
"""

    elif mode == "Advanced":
        prompt = f"""
Explain this topic for engineering students.

Rules:
- Use technical terms.
- Explain concepts deeply.
- Professional style.

Content:
{text}
"""

    else:
        prompt = f"""
Generate last minute revision notes.

Rules:
- Maximum 10 bullets.
- Only key facts.
- Very short.

Content:
{text}
"""

    return ai_generate(prompt)
if api_key:
    st.success("✅ Hugging Face API Connected")
else:
    st.error("❌ API Key Not Found")
dark_mode = st.toggle("🌗 Dark Mode")
if dark_mode:
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: white;
        }
        h1, h2, h3, h4 {
            color: #ffffff;
        }
        .stButton>button {
            background-color: #262730;
            color: white;
        }
        .stTextInput>div>div>input {
            background-color: #262730;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Card style */
.card {
    background-color: #1e1e1e;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
}

/* Headings */
h1, h2, h3 {
    font-family: 'Segoe UI', sans-serif;
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    height: 3em;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)
    
if "run_clicked" not in st.session_state:
    st.session_state.run_clicked = False

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
st.title("📘 Intelligent Content Transformer")
st.markdown("""
<div style="
    color: white;
    background-color: #262730;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    font-size: 16px;
    font-weight: 500;
">
📄 Transform your content into <b>Summaries</b>, <b>Notes</b>, and <b>Detailed Explanations</b> instantly.
</div>
""", unsafe_allow_html=True)


# PDF Upload
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

text = ""

# Extract text from PDF
if uploaded_file:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + " "
    
    if not text:
        st.error("Could not read text from this PDF. Try another file.")

# Manual text input
if not uploaded_file:
    text = st.text_area("Enter your text")

# Action selection
option = st.selectbox("Choose action", ["Summarize", "Expand", "Smart Notes", "Quiz", "Study Planner"])

# Mode selection
mode = st.selectbox(
    "Select Mode",
    [
        "Detailed",
        "Smart Summary",
        "Exam Notes",
        "Beginner",
        "Advanced",
        "Last Minute Revision"
    ]
)


# ---------------- FUNCTIONS ---------------- #





def ai_smart_notes(text):

    prompt = f"""
You are an AI Study Assistant.

Generate Smart Notes from the following content.

Rules:
- Use clear headings.
- Use bullet points.
- Highlight important keywords.
- Keep the notes concise and revision-friendly.
- Do not miss important concepts.

Content:
{text}
"""

    return ai_generate(prompt)




def ai_study_plan(text):

    prompt = f"""
You are an AI Study Planner.

Create a study plan from the following content.

Rules:
- Divide into Day 1, Day 2, Day 3...
- Mention topics to study each day.
- Include revision day.
- Mention estimated study time.
- Keep it practical for students.

Content:
{text}
"""

    return ai_generate(prompt)

def ai_expand(text):

    prompt = f"""
You are an expert teacher.

Expand the following topic.

Rules:
- Explain every important concept.
- Use simple English.
- Give examples wherever possible.
- Use headings and bullet points.
- Do not skip any important information.

Content:
{text}
"""

    return ai_generate(prompt)


def ai_generate_quiz(text):

    prompt = f"""
You are an AI Teacher.

Generate exactly 10 MCQs from the content.

Return ONLY a JSON array.

Format:

[
  {{
    "question":"...",
    "options":["A","B","C","D"],
    "answer":"..."
  }}
]

Rules:
- Exactly 10 questions.
- Exactly 4 options.
- answer must exactly match one option.
- No explanation.
- Return only JSON.

Content:
{text}
"""

    response = ai_generate(prompt)

    if response.startswith("❌"):
        return response

    try:
        return json.loads(response)
    except:
        return []
# ---------------- RUN ---------------- #

if st.button("Run"):
    st.session_state.run_clicked = True

    # 🔥 FIXED: reset quiz properly
    st.session_state.quiz = None
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.submitted = False
    st.session_state.start_time = time.time()

if st.session_state.run_clicked:
    if text:
        with st.spinner("AI is generating your content..."):

            st.divider()

            if option == "Summarize":
                st.success("✅ Summary Generated")
                result = ai_summary(text, mode)

                st.markdown(result)

                st.download_button("📥 Download Summary", result, file_name="summary.txt")

            elif option == "Smart Notes":
                st.success("📌 Smart Notes Generated")

                notes = ai_smart_notes(text)

                st.markdown(notes)

                st.download_button(
                    "📥 Download Notes",
                    notes,
                    file_name="notes.txt"
                )
            elif option == "Quiz":

                st.success("🧪 Interactive AI Quiz")

                if st.session_state.quiz is None:
                    st.session_state.quiz = ai_generate_quiz(text)

                quiz = st.session_state.quiz

                if isinstance(quiz, str):
                    st.error(quiz)

                elif not quiz:
                    st.warning("Could not generate quiz.")
                else:

                    if st.session_state.q_index >= len(quiz):
                        st.success(
                            f"🏁 Quiz Completed! Score: {st.session_state.score}/{len(quiz)}"
                        )

                        if st.button("Restart Quiz"):
                            st.session_state.quiz = None
                            st.session_state.q_index = 0
                            st.session_state.score = 0
                            st.session_state.submitted = False
                            st.session_state.start_time = time.time()
                            st.rerun()

                        st.stop()

                    q = quiz[st.session_state.q_index]

                    st.subheader(f"Question {st.session_state.q_index + 1}")

                    st.write(q["question"])

                    time_elapsed = time.time() - st.session_state.start_time
                    time_left = int(15 - time_elapsed)

                    st.warning(f"⏱ Time Left: {max(0, time_left)} sec")

                    st.info(f"📊 Score: {st.session_state.score}")

                    if time_left <= 0:
                        st.session_state.q_index += 1
                        st.session_state.start_time = time.time()
                        st.session_state.submitted = False
                        st.rerun()

                    selected = st.radio(
                        "Choose your answer:",
                        q["options"],
                        key=f"radio_{st.session_state.q_index}"
                    )

                    if st.button("Submit Answer") and not st.session_state.submitted:

                        st.session_state.submitted = True

                        if selected == q["answer"]:
                            st.success("🎉 Correct!")
                            st.session_state.score += 1
                        else:
                            st.error(f"❌ Correct Answer: {q['answer']}")

                    if st.session_state.submitted:

                        if st.button("Next Question"):

                            st.session_state.q_index += 1

                            st.session_state.submitted = False

                            st.session_state.start_time = time.time()

                            st.rerun()
            elif option == "Expand":
                st.success("✅ Expanded Content Generated")

                result = ai_expand(text)

                st.markdown(result)

                st.download_button(
                    "📥 Download Expanded Notes",
                    result,
                    file_name="expanded_notes.txt"
                )

            elif option == "Study Planner":
                st.success("📅 Study Plan Generated")

                plan = ai_study_plan(text)

                st.markdown(plan)

                st.download_button(
                    "📥 Download Study Plan",
                    plan,
                    file_name="study_plan.txt"
                )

    else:
        st.warning("Please enter text or upload a PDF")