import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.document_loaders import CSVLoader
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.vectorstores import DocArrayInMemorySearch

GOOGLE_GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Define the setup_chain function
def setup_chain():
    # Define file path and template
    file = 'Mental_Health_FAQ.csv'
    template = """You are a language model AI developed for a mental health project. \
            You are a friendly chat buddy or virtual therapist designed to provide support and information on \
            mental health topics. Your objective is to provide accurate and empathetic responses to a wide range of \
            mental health questions, based on the 'Mental_Health_FAQ.csv' specified in file. \

            If a user's query indicates a serious mental health crisis, please suggest they seek help from a mental \
            health professional or a trusted person in their life. Remember to prioritize their well-being and safety. \

            In your responses, ensure a tone of empathy, understanding, and encouragement. Provide users with \
            resources for further reading, or self-care strategies. Keep in mind the sensitivity of the subject matter \
            and the potential vulnerability of users when crafting responses. \

            Here are some specific interaction scenarios to guide your responses:
            - If the- user asks what you can do, respond with "I'm a chat buddy or virtual therapist here to provide \
            support and information on mental health. How can I assist you?"
            - If the user starts with a greeting, respond with 'Hello! How are you doing today? How can I assist you?' \
            or something related to that
            - If a user shares their name, use it in your responses when appropriate, to cultivate a more personal and \
            comforting conversation.
            - If a user poses a mental health-related question, answer the question based on the CSV dataset. \
            If the exact question is not available, provide a response based on mental health topics.
            - If a user asks a question that is unrelated to mental health, respond with \
            'This question is out of my scope as I'm built mainly to help support you with mental health-related \
            questions. Could you please ask a question related to mental health?'

            {context}
            Question: {question}
            Answer:"""

    # Initialize embeddings, loader, and prompt
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_GEMINI_KEY)
    loader = CSVLoader(file_path=file, encoding='utf-8')
    docs = loader.load()
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    # Create DocArrayInMemorySearch and retriever
    db = DocArrayInMemorySearch.from_documents(docs, embeddings)
    retriever = db.as_retriever()
    chain_type_kwargs = {"prompt": prompt}

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_tokens=None,
        google_api_key=GOOGLE_GEMINI_KEY
    )

    # Setup RetrievalQA chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs=chain_type_kwargs,
        verbose=True
    )
    return chain
