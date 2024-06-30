import streamlit as st
import os
import sys
import json

sys.path.append(os.path.abspath('../../'))
from tasks.task_3.task_3_solution import DocumentProcessor
from tasks.task_4.task_4_solution import EmbeddingClient
from tasks.task_5.task_5_solution import ChromaCollectionCreator
from tasks.task_8.task_8_solution import QuizGenerator
from tasks.task_9.task_9_solution import QuizManager

if __name__ == "__main__":

    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "my-first-project-424120",
        "location": "us-central1"
    }

    if 'page' not in st.session_state:
        st.session_state.page = 0
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    def next_page():
        st.session_state.page += 1

    def previous_page():
        st.session_state.page -= 1

    def go_home():
        st.session_state.page = 0
        st.session_state['question_bank'] = []
        st.session_state['display_quiz'] = False
        st.session_state['question_index'] = 0
        st.session_state.correct_answers = 0
        

    # Sidebar for navigation
    with st.sidebar.expander("Navigation", expanded=True):
        st.button("Home", on_click=go_home)

    if st.session_state.page == 0:
        if 'question_bank' not in st.session_state or len(st.session_state['question_bank']) == 0:
            if 'question_bank' not in st.session_state:
                st.session_state['question_bank'] = []

            screen = st.empty()
            with screen.container():
                st.header("Quiz Builder")

                with st.form("Load Data to Chroma"):
                    st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")
                    processor = DocumentProcessor()
                    processor.ingest_documents()

                    embed_client = EmbeddingClient(**embed_config)

                    chroma_creator = ChromaCollectionCreator(processor, embed_client)

                    topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
                    questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)

                    submitted = st.form_submit_button("Submit")

                    if submitted:
                        chroma_creator.create_chroma_collection()

                        if len(processor.pages) > 0:
                            st.write(f"Generating {questions} questions for topic: {topic_input}")

                        generator = QuizGenerator(topic_input, questions, chroma_creator)
                        question_bank = generator.generate_quiz()
                        st.session_state['question_bank'] = question_bank
                        st.session_state['display_quiz'] = True
                        st.session_state['question_index'] = 0
                        next_page()
                        st.rerun()

    if st.session_state.page == 1:
        if st.session_state['display_quiz']:
            screen = st.empty()
            with screen.container():
                st.header("Generated Quiz Question: ")
                question_bank = st.session_state['question_bank']
                quiz_manager = QuizManager(question_bank)

                index_question = quiz_manager.get_question_at_index(st.session_state["question_index"])

                choices = [f"{choice['key']}) {choice['value']}" for choice in index_question['choices']]

                st.write(f"{st.session_state['question_index'] + 1}. {index_question['question']}")
                with st.form("MCQ"):
                    answer = st.radio("Choose an answer", choices, index=None, disabled=st.session_state["question_index"] in st.session_state.answers)
                

                    if st.form_submit_button("Next Question"):
                        quiz_manager.next_question_index(direction=1)
                        st.rerun()

                    if st.form_submit_button("Previous Question"):
                        quiz_manager.next_question_index(direction=-1)
                        st.rerun()

                    if st.form_submit_button("Submit Answer") and answer is not None:
                        st.session_state.answers[st.session_state["question_index"]] = answer
                        correct_answer = index_question['answer']
                        if answer.startswith(correct_answer):
                            st.success("Correct!", icon="✅")
                            st.session_state.correct_answers += 1
                        else:
                            st.error("Incorrect!",icon="❌")
                        st.write(f"Explanation: {index_question['explanation']}")
                        st.rerun()
                    if st.form_submit_button("Review"):
                        next_page()
                        st.rerun()

    if st.session_state.page == 2:
        if st.session_state['display_quiz']:
            screen = st.empty()
            with screen.container():
                st.header("Quiz Results")
                correct_count = st.session_state.correct_answers
                total_questions = len(st.session_state['question_bank'])
                percentage = (correct_count / total_questions) * 100
                with st.form("Review Answers"):
                    st.write(f"You got {percentage:.2f}%")
                    st.write(f"You answered {correct_count} out of {total_questions} questions correctly.")
                    for idx, question in enumerate(st.session_state['question_bank']):
                        if idx in st.session_state.answers:
                            st.write(f"Question {idx + 1}: {question['question']}")
                            user_answer = st.session_state.answers[idx]
                            correct_answer = question['answer']
                            if user_answer.startswith(correct_answer):
                                st.success("Correct!", icon="✅")
                                st.write(f"Your answer: {user_answer}")
                                st.write(f"Correct answer: {correct_answer}")
                            else:
                                st.error("Incorrect!", icon="❌")
                                st.write(f"Your answer: {user_answer}")
                                st.write(f"Correct answer: {correct_answer}")
                            st.write(f"Explanation: {question['explanation']}")
                            st.write("---")

                    if st.form_submit_button("Back to questions"):
                        previous_page()
                        st.rerun()
