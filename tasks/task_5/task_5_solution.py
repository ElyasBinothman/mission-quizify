import sys
import os
from annotated_types import doc
from posthog import page
import streamlit as st
sys.path.append(os.path.abspath('../../'))
from tasks.task_3.task_3_solution import DocumentProcessor
from tasks.task_4.task_4_solution import EmbeddingClient

# Import Task libraries
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from google.cloud import aiplatform

class ChromaCollectionCreator:
    """
    This class handles the creation of a Chroma collection using documents processed by a DocumentProcessor instance
    and embeddings provided by an EmbeddingClient instance.

    Steps:
    1. Check if any documents have been processed by the DocumentProcessor instance. If not, display an error message using Streamlit's error widget.
    2. Split the processed documents into text chunks suitable for embedding and indexing using the CharacterTextSplitter from Langchain.
    3. Create a Chroma collection in memory with the text chunks and the embeddings model initialized in the class.
    """

    def __init__(self, processor, embed_model):
        """
        Initializes the ChromaCollectionCreator with a DocumentProcessor instance and embeddings configuration.
        
        :param processor: An instance of DocumentProcessor that has processed documents.
        :param embed_model: An embedding client for embedding documents.
        """
        self.processor = processor  # Holds the DocumentProcessor from Task 3
        self.embed_model = embed_model  # Holds the EmbeddingClient from Task 4
        self.db = None  # Holds the Chroma collection

    def create_chroma_collection(self):
        """
        Creates a Chroma collection from the documents processed by the DocumentProcessor instance.
        """

        # Step 1: Check for processed documents
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return

        # Step 2: Split documents into text chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        texts = text_splitter.split_documents(self.processor.pages)

        if texts:
            st.success(f"Successfully split pages to {len(texts)} documents!", icon="✅")
        else:
            st.error("Failed to split documents.", icon="🚨")
            return

        # Step 3: Create the Chroma Collection
        self.db = Chroma.from_documents(texts, self.embed_model)
        if self.db:
            st.success("Successfully created Chroma Collection!", icon="✅")
        else:
            st.error("Failed to create Chroma Collection!", icon="🚨")

    def query_chroma_collection(self, query) -> Document:
        """
        Queries the created Chroma collection for documents similar to the query.
        
        :param query: The query string to search for in the Chroma collection.
        :return: The first matching document from the collection with similarity score.
        """
        if self.db:
            docs = self.db.similarity_search_with_relevance_scores(query)
            if docs:
                return docs[0]
            else:
                st.error("No matching documents found!", icon="🚨")
        else:
            st.error("Chroma Collection has not been created!", icon="🚨")

    def as_retriever(self):
        """
        Converts the ChromaCollectionCreator into a retriever.
        
        :return: A retriever object from the Chroma collection.
        """
        if self.db:
            return self.db.as_retriever()
        else:
            raise AttributeError("Chroma Collection has not been created!")

if __name__ == "__main__":
    processor = DocumentProcessor()  # Initialize from Task 3
    processor.ingest_documents()

    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "my-first-project-424120",
        "location": "us-central1"
    }

    embed_client = EmbeddingClient(**embed_config)  # Initialize from Task 4
    chroma_creator = ChromaCollectionCreator(processor, embed_client)

    with st.form("Load Data to Chroma"):
        st.write("Select PDFs for Ingestion, then click Submit")

        submitted = st.form_submit_button("Submit")
        if submitted:
            chroma_creator.create_chroma_collection()

# For more information on CharacterTextSplitter, refer to:
# https://python.langchain.com/docs/modules/data_connection/document_transformers/character_text_splitter
# For more information on Chroma, refer to:
# https://docs.trychroma.com/getting-started
