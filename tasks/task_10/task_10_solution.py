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

# Main script for the Quiz Builder application
if __name__ == "__main__":
    
    # Configuration for the EmbeddingClient
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "my-first-project-424120",
        "location": "us-central1"
    }
    
    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = 0
        
    # Function to navigate to the next page
    def next_page():
        st.session_state.page += 1
    
    # Function to navigate to the previous page
    def previous_page():
        st.session_state.page -= 1
    
    # Function to reset to the home page
    def go_home():
        st.session_state.page = 0
        st.session_state['question_bank'] = []
        st.session_state['display_quiz'] = False
        st.session_state['question_index'] = 0
    
    # Home page: Quiz Builder form
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
                        
                        # Generate quiz questions using the QuizGenerator class
                        generator = QuizGenerator(topic_input, questions, chroma_creator)
                        question_bank = generator.generate_quiz()
                        st.session_state['question_bank'] = question_bank
                        st.session_state['display_quiz'] = True
                        st.session_state['question_index'] = 0
                        next_page()  # Move to the next page to display the quiz
                        st.rerun()
        
    # Page 1: Display generated quiz questions
    if st.session_state.page == 1:
        if st.session_state['display_quiz']:
            screen = st.empty()
            with screen.container():
                st.header("Generated Quiz Question:")
                question_bank = st.session_state['question_bank']
                quiz_manager = QuizManager(question_bank)
                
                # Get the current question based on the session state index
                index_question = quiz_manager.get_question_at_index(st.session_state["question_index"])
                
                # Format the choices for display
                choices = [f"{choice['key']}) {choice['value']}" for choice in index_question['choices']]
                
                st.write(f"{st.session_state['question_index'] + 1}. {index_question['question']}")
                with st.form("MCQ"):
                    answer = st.radio("Choose an answer", choices, index=None)
                    
                    # Navigate to the next question
                    if st.form_submit_button("Next Question"):
                        quiz_manager.next_question_index(direction=1)
                        st.rerun()
                        
                    # Navigate to the previous question
                    if st.form_submit_button("Previous Question"):
                        quiz_manager.next_question_index(direction=-1)
                        st.rerun()
                        
                    # Submit the selected answer
                    if st.form_submit_button("Submit Answer") and answer is not None:
                        correct_answer_key = index_question['answer']
                        if answer.startswith(correct_answer_key):
                            st.success("Correct!")
                        else:
                            st.error("Incorrect!")
                        st.write(f"Explanation: {index_question['explanation']}")
                    
                    # Navigate back to the home page
                    if st.form_submit_button("Home"):
                        go_home()
                        st.rerun()

# For more information on Streamlit, refer to:
# https://docs.streamlit.io/
