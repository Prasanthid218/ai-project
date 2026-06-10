import streamlit as st
import PyPDF2
import re
from collections import Counter
import random
import time
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

st.title(" Intelligent Content Transformer")
st.markdown("""
<div style="
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

def summarize(text, mode):

    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)

    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 25]

    if not sentences:
        return "No meaningful content found."

    if mode == "Detailed":

        step = max(1, len(sentences)//8)

        selected = []

        for i in range(0, len(sentences), step):
            selected.append(sentences[i])

            if len(selected) >= 8:
                break

        return ". ".join(selected) + "."

    elif mode == "Smart Summary":

        important = []

        important.append(sentences[0])

        if len(sentences) > 4:
            important.append(sentences[len(sentences)//4])

        if len(sentences) > 6:
            important.append(sentences[len(sentences)//2])

        if len(sentences) > 8:
            important.append(sentences[(3*len(sentences))//4])

        important.append(sentences[-1])

        return ". ".join(important) + "."

    elif mode == "Exam Notes":

        notes = ""

        step = max(1, len(sentences)//5)

        count = 0

        for i in range(0, len(sentences), step):

            notes += f"📌 {sentences[i]}\n\n"

            count += 1

            if count == 5:
                break

        return notes

    elif mode == "Beginner":

        first = sentences[0]

        return (
            "👉 In simple words:\n\n"
            + first
            + ".\n\nThis topic explains the basic idea in an easy-to-understand way."
        )

    elif mode == "Advanced":

        step = max(1, len(sentences)//6)

        selected = []

        for i in range(0, len(sentences), step):

            selected.append(sentences[i])

            if len(selected) == 6:
                break

        return (
            "Advanced Explanation:\n\n"
            + ". ".join(selected)
            + "."
        )

    elif mode == "Last Minute Revision":

        step = max(1, len(sentences)//6)

        revision = ""

        count = 0

        for i in range(0, len(sentences), step):

            revision += f"✔ {sentences[i]}\n\n"

            count += 1

            if count == 6:
                break

        return revision


def smart_notes(text):
    sentences = text.split(".")
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return "No meaningful content found."
    
    notes = ""
    i = 0
    
    while i < len(sentences):
        group = sentences[i:i+3]
        first = re.sub(r"\[.*?\]|\(.*?\)", "", group[0])
        words = first.split()

        stopwords = [
            "the","is","was","and","of","to","in","a","it","on",
            "for","with","also","called","due","their","were","has",
            "these","this","which","where","when","they","are","most","according"
        ]

        meaningful = [w for w in words if w.lower() not in stopwords and len(w) > 3 and w.isalpha()]

        if not meaningful:
            i += 3
            continue

        heading = " ".join(meaningful[:2]).title()

        notes += f"### 📌 {heading}\n"

        for line in group:
            clean_line = re.sub(r"\[.*?\]|\(.*?\)", "", line)
            notes += f"🧾 {clean_line.strip()}\n"

        notes += "\n"
        i += 3

    return notes


def generate_quiz_data(text):
    sentences = text.split(".")
    sentences = [s.strip() for s in sentences if s.strip()]
    
    quiz_data = []

    # 🔥 FIXED: use full text (not only 5 sentences)
    for sentence in sentences:
        words = sentence.split()

        if len(words) < 6:
            continue

        keywords = [w for w in words if w.isalpha() and len(w) > 4]

        if len(keywords) < 4:
            continue

        answer = keywords[0]

        options = random.sample(keywords, 3)
        options.append(answer)
        random.shuffle(options)

        quiz_data.append({
            "question": f"What is the key concept in:\n'{sentence}'?",
            "options": options,
            "answer": answer
        })

    return quiz_data[:10]   # 🔥 FIXED: max 10 questions

def generate_study_plan(text):
    sentences = text.split(".")
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return "No content available"

    topics = []

    for s in sentences[:5]:
        words = s.split()
        topic = " ".join(words[:3])  # small heading
        topics.append(topic)

    plan = ""

    days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]

    for i in range(min(len(topics), 5)):
        plan += f"📅 {days[i]}: {topics[i]}\n"
        plan += "   👉 Study concepts and understand basics\n\n"

    return plan

def expand(text):
    return text + " This topic can be further understood by analyzing its key concepts, applications, and real-world examples in detail."


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
        with st.spinner("Processing..."):

            st.divider()

            if option == "Summarize":
                st.success("✅ Summary Generated")
                result = summarize(text, mode)

                st.markdown(result)

                st.download_button("📥 Download Summary", result, file_name="summary.txt")

            elif option == "Smart Notes":
                st.success("📌 Smart Notes Generated")

                notes = smart_notes(text)
                st.markdown(notes)

                st.download_button("📥 Download Notes", notes, file_name="notes.txt")

            elif option == "Quiz":
                st.success("🧪 Interactive Quiz")

                if st.session_state.quiz is None:
                    st.session_state.quiz = generate_quiz_data(text)

                quiz = st.session_state.quiz

                if not quiz:
                    st.warning("Not enough content to generate quiz")
                else:
                    if st.session_state.q_index >= len(quiz):
                        st.success(f"🏁 Quiz Completed! Score: {st.session_state.score}/{len(quiz)}")

                        if st.button("Restart Quiz"):
                            st.session_state.quiz = None
                            st.session_state.q_index = 0
                            st.session_state.score = 0
                            st.session_state.start_time = time.time()

                        st.stop()

                    q = quiz[st.session_state.q_index]

                    st.subheader(f"Question {st.session_state.q_index + 1}")
                    st.write(q["question"])

                    # 🔥 FIXED TIMER (stable)
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

                    # 🔥 FIXED: prevent double scoring
                    if st.button("Submit Answer") and not st.session_state.submitted:
                        st.session_state.submitted = True

                        if selected == q["answer"]:
                            st.success("🎉 Correct!")
                            st.session_state.score += 1
                        else:
                            st.error(f"Wrong! Answer: {q['answer']}")

                    if st.session_state.submitted:
                        if st.button("Next Question"):
                            st.session_state.q_index += 1
                            st.session_state.submitted = False
                            st.session_state.start_time = time.time()
                            st.rerun()

            elif option == "Expand":
                st.success("✅ Expanded Content Generated")
                st.markdown(expand(text))
            elif option == "Study Planner":
                st.success("📅 Study Plan Generated")

                plan = generate_study_plan(text)

                st.text(plan)

                st.download_button(
        "📥 Download Study Plan",
        plan,
        file_name="study_plan.txt"
    )

    else:
        st.warning("Please enter text or upload a PDF")