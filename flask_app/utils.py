import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory


load_dotenv()
# Load API keys from environment variables
SERPER_API_KEY = os.environ.get('SERPAPI_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def search_articles(query):
    """
    Searches for articles related to the query using Serper API.
    Returns a list of dictionaries containing article URLs, headings, and text.
    """
    search_url = f"https://serpapi.com/search?q={query}&api_key={SERPER_API_KEY}&engine=google&n=3"

    response = requests.get(search_url)
    if response.status_code != 200:
        raise Exception("Error: Unable to retrieve search results from SerpAPI")

    search_results = response.json()
    
    articles = []
    excluded_domains = ["tiktok.com", "linkedin.com", "facebook.com", "x.com"]

   
    for result in search_results.get('organic_results', []):
        url = result.get('link')
        if not any(domain in url for domain in excluded_domains):
            articles.append(url)
    

    return articles


def fetch_article_content(url):
    """
    Fetches the article content, extracting headings and text.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive'
    }
    
    response = requests.get(url, headers= headers)
    if response.status_code != 200:
        raise Exception(f"Error: Unable to fetch content from {url}. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')

    content = ""

    for element in soup.find_all(['h1', 'h2', 'h3', 'p']):
        if element.name == 'h1' or element.name == 'h2' or element.name == 'h3':
            content += f"\n## {element.get_text(strip=True)}\n\n"
        elif element.name == 'p':
            text = element.get_text(strip=True) + "\n"
            if text:  # Skip empty paragraphs
                content += f"{text}\n\n"
    
    return content.strip()



def concatenate_content(articles):
    """
    Concatenates the content of the provided articles into a single string.
    """
    full_text = ""
    
    if not articles:
        return "Answer Based On Your Knowledge Only"
    
    for index, url in enumerate(articles, 1):
        try:
            
            # Fetching content from the url
            content = fetch_article_content(url)
            
            # Putting Number for each article for formatting purpose
            full_text += f"\n\n### Article {index}\n\n"
            
            # Adding conent fto full text
            full_text += content
            
            full_text += f"\n\n### End of Article {index}\n\n"
            
        except Exception as e:
            print(f"\n\nError fetching content for {url}: {str(e)}\n\n")

    return full_text


## Generating Answer from LLM with memory buffer of length 5
conversation_buffer = []

def get_history(session_id: str) -> BaseChatMessageHistory:
    """
    Retrieves the last 5 messages from the conversation buffer.
    """
    global conversation_buffer
    history = ChatMessageHistory()
    
    # Add the last 5 messages to the history
    for message in conversation_buffer[-5:]:
        if message['type'] == 'human':
            history.add_user_message(message['content'])
        elif message['type'] == 'ai':
            history.add_ai_message(message['content'])
    
    return history

def update_conversation_buffer(message_type: str, content: str):
    """
    Updates the conversation buffer with a new message.
    Keeps only the last 5 messages.
    """
    global conversation_buffer
    conversation_buffer.append({'type': message_type, 'content': content})
    
    if len(conversation_buffer) > 5:
        conversation_buffer.pop(0)

def generate_answer(content, query):
    """
    Generates an answer from the concatenated content using GPT-4.
    The content and the user's query are used to generate a contextual answer.
    """
    prompt = PromptTemplate(
        input_variables=["chat_history", "articles", "question"],
        template="""
            You are an intelligent and smart AI assistant. Use the article content provided below to answer the user query clearly and accurately.
            If articles is empty then just look at the question and answer it based on your intelligence.
            Here's the chat so far:
                {chat_history}
            ---------------------
            ARTICLES:
                {articles}
            ---------------------

            QUESTION:
                {question}

            Give a factual and concise response:
        """
    )

    print('Im here inside generate answer')
    llm = ChatGroq(model="llama-3.3-70b-versatile")

    chain = (prompt | llm).with_config({"run_name": "generate_answer_chain"})
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_history,
        input_messages_key="question",
        history_messages_key="chat_history"
    )
    
    # Update the buffer with the user's query
    update_conversation_buffer('human', query)

    response = chain_with_history.invoke({
        "articles": content,
        "question": query
    }, config={"configurable": {"session_id": "user-session-001"}})

    # Update the buffer with the AI's response
    ai_response = response.content if hasattr(response, 'content') else str(response)
    update_conversation_buffer('ai', ai_response)

    print(ai_response)
    return ai_response
