import sys
import os
import streamlit as st
sys.path.append(os.path.abspath('../../'))
from tasks.task_3.task_3_solution import DocumentProcessor
from tasks.task_4.task_4_solution import EmbeddingClient
from tasks.task_5.task_5_solution import ChromaCollectionCreator

"""
Task: Build a Quiz Builder with Streamlit and LangChain

Overview:
Create a "Quiz Builder" application using Streamlit. This interactive application enables users to upload documents, specify a quiz topic, select a number of questions, and generate a quiz based on the uploaded document contents.

Components to Integrate:
- DocumentProcessor: Class for processing uploaded PDF documents.
- EmbeddingClient: Class for embedding queries.
- ChromaCollectionCreator: Class for creating a Chroma collection from processed documents.

Step-by-Step Instructions:
1. Initialize a `DocumentProcessor` instance and call `ingest_documents()` to process uploaded PDF documents.
2. Configure and initialize the `EmbeddingClient` with the model, project, and location details in `embed_config`.
3. Instantiate the `ChromaCollectionCreator` using the `DocumentProcessor` and `EmbeddingClient`.
4. Use Streamlit to create a form that captures the quiz topic and the number of questions via a slider.
5. After form submission, use the `ChromaCollectionCreator` to create a Chroma collection from the processed documents.
6. Allow users to input a query related to the quiz topic and use the Chroma collection to generate quiz questions.

Implementation Guidance:
- Use Streamlit's widgets such as `st.header`, `st.subheader`, `st.text_input`, and `st.slider` to create the form.
- Post form submission, verify document processing and Chroma collection creation, providing feedback through Streamlit.
- Add a query input field post-Chroma collection creation to gather user queries for generating quiz questions.
"""

if __name__ == "__main__":
    # Configuration for EmbeddingClient
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "my-first-project-424120",
        "location": "us-central1"
    }
    
    screen = st.empty()  # Screen 1: ingest documents
    with screen.container():
        st.header("Quizzify")

        # Initialize DocumentProcessor and ingest documents
        processor = DocumentProcessor()  # From Task 3
        processor.ingest_documents()

        # Initialize EmbeddingClient with embed config
        embed_client = EmbeddingClient(**embed_config)  # From Task 4

        # Initialize ChromaCollectionCreator
        chroma_creator = ChromaCollectionCreator(processor, embed_client)

        with st.form("Load Data to Chroma"):
            st.subheader("Quiz Builder")
            st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")
            text_field = st.text_input("Type the subject of the quiz")
            slider = st.slider("Number of questions", min_value=1, max_value=10, value=1, step=1)
            
            submitted = st.form_submit_button("Generate a Quiz!")
            if submitted:
                # Create Chroma collection from processed documents
                chroma_creator.create_chroma_collection()
                document = chroma_creator.query_chroma_collection(text_field)

    if document:
        screen.empty()  # Screen 2
        with st.container():
            st.header("Query Chroma for Topic, top Document:")
            st.write(document)

# For more information on Streamlit, refer to:
# https://docs.streamlit.io/
