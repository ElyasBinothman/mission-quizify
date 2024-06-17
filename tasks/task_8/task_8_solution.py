import streamlit as st
import os
import sys
import json

from sympy import true
sys.path.append(os.path.abspath('../../'))
from tasks.task_3.task_3_solution import DocumentProcessor
from tasks.task_4.task_4_solution import EmbeddingClient
from tasks.task_5.task_5_solution import ChromaCollectionCreator
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI

class QuizGenerator:
    def __init__(self, topic=None, num_questions=1, vectorstore=None):
        """
        Initializes the QuizGenerator with a required topic, the number of questions for the quiz,
        and an optional vectorstore for querying related information.

        :param topic: A string representing the required topic of the quiz.
        :param num_questions: An integer representing the number of questions to generate for the quiz, up to a maximum of 10.
        :param vectorstore: An optional vectorstore instance (e.g., ChromaDB) to be used for querying information related to the quiz topic.
        """
        if not topic:
            self.topic = "General Knowledge"
        else:
            self.topic = topic

        if num_questions > 10:
            raise ValueError("Number of questions cannot exceed 10.")
        self.num_questions = num_questions

        self.vectorstore = vectorstore
        self.llm = None
        self.question_bank = []
        self.system_template = """
            You are a subject matter expert on the topic: {topic}
            
            Follow the instructions to create a quiz question:
            1. Generate a question based on the topic provided and context as key "question"
            2. Provide 4 multiple choice answers to the question as a list of key-value pairs "choices"
            3. Provide the correct answer for the question from the list of answers as key "answer"
            4. Provide an explanation as to why the answer is correct as key "explanation"
            
            You must respond as a JSON object with the following structure:
            {{
                "question": "<question>",
                "choices": [
                    {{"key": "A", "value": "<choice>"}},
                    {{"key": "B", "value": "<choice>"}},
                    {{"key": "C", "value": "<choice>"}},
                    {{"key": "D", "value": "<choice>"}}
                ],
                "answer": "<answer key from choices list>",
                "explanation": "<explanation as to why the answer is correct>"
            }}
            
            Context: {context}
            """
        self.json_output_parser = JsonOutputParser()
    
    def init_llm(self):
        """
        Initializes and configures the Large Language Model (LLM) for generating quiz questions.

        This method should handle any setup required to interact with the LLM, including authentication,
        setting up any necessary parameters, or selecting a specific model.

        :return: An instance or configuration for the LLM.
        """
        self.llm = VertexAI(
            model_name = "gemini-pro",
            temperature = 0.8, 
            max_output_tokens = 500
        )

    def generate_question_with_vectorstore(self):
        """
        Generates a quiz question based on the topic provided using a vectorstore

        :return: A JSON object representing the generated quiz question.
        """
        if self.llm is None:
            self.init_llm()
        if self.vectorstore is None:
            raise ValueError("Vectorstore not provided.")
        
        from langchain_core.runnables import RunnablePassthrough, RunnableParallel

        retriever = self.vectorstore.as_retriever()
        
        prompt = PromptTemplate.from_template(self.system_template)
        
        setup_and_retrieval = RunnableParallel(
            {"context": retriever, "topic": RunnablePassthrough()}
        )
        chain = setup_and_retrieval | prompt | self.llm | self.json_output_parser

        response = chain.invoke(self.topic)
        return response

    def generate_quiz(self) -> list:
        """
        Task: Generate a list of unique quiz questions based on the specified topic and number of questions.

        This method orchestrates the quiz generation process by utilizing the `generate_question_with_vectorstore` method to generate each question and the `validate_question` method to ensure its uniqueness before adding it to the quiz.

        Steps:
            1. Initialize an empty list to store the unique quiz questions.
            2. Loop through the desired number of questions (`num_questions`), generating each question via `generate_question_with_vectorstore`.
            3. For each generated question, validate its uniqueness using `validate_question`.
            4. If the question is unique, add it to the quiz; if not, attempt to generate a new question (consider implementing a retry limit).
            5. Return the compiled list of unique quiz questions.

        Returns:
        - A list of dictionaries, where each dictionary represents a unique quiz question generated based on the topic.

        Note: This method relies on `generate_question_with_vectorstore` for question generation and `validate_question` for ensuring question uniqueness. Ensure `question_bank` is properly initialized and managed.
        """
        self.question_bank = []

        for _ in range(self.num_questions):
            question_str = self.generate_question_with_vectorstore()
            
            # Check if the response is already a dictionary
            if isinstance(question_str, dict):
                question = question_str
            else:
                try:
                    question = json.loads(question_str)
                except json.JSONDecodeError:
                    print("Failed to decode question JSON.")
                    continue

            if self.validate_question(question):
                print("Successfully generated unique question")
                self.question_bank.append(question)
            else:
                print("Duplicate or invalid question detected.")

        return self.question_bank

    def validate_question(self, question: dict) -> bool:
        if 'question' not in question:
            return False

        question_text = question['question']

        for existing_question in self.question_bank:
            if question_text == existing_question['question']:
                return False
            
        return True

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
                
                generator = QuizGenerator(topic_input, questions, chroma_creator)
                question_bank = generator.generate_quiz()
                question = question_bank[0]

    if question_bank:
        screen.empty()
        with st.container():
            st.header("Generated Quiz Question: ")
            for question in question_bank:
                st.write(question)
