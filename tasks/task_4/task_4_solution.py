# embedding_client.py

from langchain_google_vertexai import VertexAIEmbeddings
from google.oauth2 import service_account

class EmbeddingClient:
    """
    This class initializes a connection to Google Cloud's VertexAI for text embeddings.

    The EmbeddingClient class is capable of initializing an embedding client with specific configurations
    for model name, project, and location, allowing the class to utilize Google Cloud's VertexAIEmbeddings for processing text queries.

    Steps:
    1. Implement the __init__ method to accept 'model_name', 'project', and 'location' parameters.
       These parameters are crucial for setting up the connection to the VertexAIEmbeddings service.
    2. Within the __init__ method, initialize the 'self.client' attribute as an instance of VertexAIEmbeddings
       using the provided parameters. This attribute will be used to embed queries.

    Parameters:
    - model_name: A string representing the name of the model to use for embeddings.
    - project: The Google Cloud project ID where the embedding model is hosted.
    - location: The location of the Google Cloud project, such as 'us-central1'.
    """
    
    def __init__(self, model_name, project, location):
        # Initialize the VertexAIEmbeddings client with the given parameters
        credentials = service_account.Credentials.from_service_account_file(
            'D:\\Radical AI test\\mission-quizify\\Authentication.json'
        )
        self.client = VertexAIEmbeddings(
            model_name=model_name,
            project=project,
            location=location,
            credentials=credentials
        )
        
    def embed_query(self, query):
        """
        Uses the embedding client to retrieve embeddings for the given query.

        :param query: The text query to embed.
        :return: The embeddings for the query or None if the operation fails.
        """
        vectors = self.client.embed_query(query)
        return vectors
    
    def embed_documents(self, documents):
        """
        Retrieve embeddings for multiple documents.

        :param documents: A list of text documents to embed.
        :return: A list of embeddings for the given documents.
        """
        try:
            return self.client.embed_documents(documents)
        except AttributeError:
            print("Method embed_documents not defined for the client.")
            return None

if __name__ == "__main__":
    model_name = "textembedding-gecko@003"
    project = "my-first-project-424120"
    location = "us-central1"

    embedding_client = EmbeddingClient(model_name, project, location)
    vectors = embedding_client.embed_query("Hello World!")
    if vectors:
        print(vectors)
        print("Successfully used the embedding client!")

# For more information on how to use VertexAIEmbeddings, refer to:
# https://python.langchain.com/docs/integrations/text_embedding/google_generative_ai
