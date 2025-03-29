from langchain.memory.buffer import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)

def get_conversation_chain(vectorstore):
    """Initializes the conversation chain."""
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        safety_settings={HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE},
    )
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )