import streamlit as st
import os
import sys
import json
sys.path.append(os.path.abspath('../../'))
from tasks.task_3.task_3_solution import DocumentProcessor
from tasks.task_4.task_4_solution import EmbeddingClient
from tasks.task_5.task_5_solution import ChromaCollectionCreator
from tasks.task_8.task_8_solution import QuizGenerator

class QuizManager:
    """
    This class manages the quiz questions, providing functionalities to retrieve questions by index
    and navigate through the quiz.

    :param questions: A list of dictionaries, where each dictionary represents a quiz question along with its choices, correct answer, and an explanation.
    """
    def __init__(self, questions: list):
        self.questions = questions
        self.total_questions = len(self.questions)

    def get_question_at_index(self, index: int):
        """
        Retrieves the quiz question object at the specified index. If the index is out of bounds,
        it restarts from the beginning index.

        :param index: The index of the question to retrieve.
        :return: The quiz question object at the specified index, with indexing wrapping around if out of bounds.
        """
        valid_index = index % self.total_questions
        return self.questions[valid_index]
    
    def next_question_index(self, direction=1):
        """
        Adjusts the current quiz question index based on the specified direction.

        :param direction: An integer indicating the direction to move in the quiz questions list (1 for next, -1 for previous).
        """
        curIndex = st.session_state["question_index"]
        newIndex = (curIndex + direction) % self.total_questions
        st.session_state["question_index"] = newIndex

# Test Generating the Quiz
if __name__ == "__main__":
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "my-first-project-424120",
        "location": "us-central1"
    }
    
    screen = st.empty()
    with screen.container():
        st.header("Quiz Builder")
        processor = DocumentProcessor()
        processor.ingest_documents()

        embed_client = EmbeddingClient(**embed_config)
        chroma_creator = ChromaCollectionCreator(processor, embed_client)

        question = None
        question_bank = None

        with st.form("Load Data to Chroma"):
            st.subheader("Quiz Builder")
            st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")

            topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
            questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)

            submitted = st.form_submit_button("Submit")
            if submitted:
                chroma_creator.create_chroma_collection()
                st.write(topic_input)

                # Test the Quiz Generator
                generator = QuizGenerator(topic_input, questions, chroma_creator)
                question_bank = generator.generate_quiz()

    if question_bank:
        screen.empty()
        with st.container():
            st.header("Generated Quiz Question:")
            
            quiz_manager = QuizManager(question_bank)
            with st.form("Multiple Choice Question"):
                index_question = quiz_manager.get_question_at_index(0)
                
                choices = []
                for choice in index_question['choices']:
                    formatted_choice = f"{choice['key']}) {choice['value']}"
                    choices.append(formatted_choice)
                
                st.write(f"Question: {index_question['question']}")
                
                answer = st.radio(
                    'Choose the correct answer',
                    choices
                )
                form_submitted = st.form_submit_button("Submit")
            
                if form_submitted:
                    correct_answer_key = index_question['answer']
                    if answer.startswith(correct_answer_key):
                        st.success("Correct!")
                    else:
                        st.error("Incorrect!")

# For more information on Streamlit, refer to:
# https://docs.streamlit.io/
