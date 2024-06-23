# Gemeni Quizify Quiz Generator

## Description
Gemeni Quizify is an AI-powered bot that generates questions based on a topic entered by the user from a document they have uploaded. This project leverages state-of-the-art natural language processing techniques to create quizzes that are tailored to specific topics within the provided documents.

## Installation

To set up Gemeni Quizify, you'll need to install the following dependencies:

1. **Streamlit**:
   ```
   pip install streamlit
   ```

2. **Chromadb**:
   ```
   pip install chromadb
   ```

3. **Langchain**:
   ```
   pip install langchain
   ```

4. **Langchain Google VertexAI**:
   ```
   pip install langchain-google-vertexai
   ```

5. **PyPDF**:
   ```
   pip install pypdf
   ```

Additionally, download and install [Git for Windows](https://gitforwindows.org/).

## Usage

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/gemeni-quizify.git
   ```

2. Navigate to the project directory:
   ```
   cd gemeni-quizify
   ```

3. Run the Streamlit application:
   ```
   streamlit run app.py
   ```

4. Upload a document through the web interface.

5. Choose a topic and specify the number of questions.

6. The AI bot will generate questions based on the topic from the uploaded document. If no specific topic is provided, it will generate general questions from the document.

## Features

- Upload any document (PDF format supported).
- Generate questions based on a specific topic within the document.
- Generate general questions if no specific topic is provided.

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.
