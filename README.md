# 🔍 LLM-based RAG Search System (with Memory)

This project combines a **Flask backend** and a **Streamlit frontend** to build a **Retrieval-Augmented Generation (RAG)** application powered by LLMs. It allows users to input queries, fetches relevant web articles using SerpAPI, processes the content, and generates intelligent responses using Groq's LLaMA-3. It also maintains a **memory buffer of the last 5 messages** to retain context across interactions.

---

## 🚀 Features

- 🔎 Searches the web for relevant content using SerpAPI  
- 📄 Scrapes and cleans article content using BeautifulSoup  
- 🧠 Generates contextual responses with Groq's LLaMA-3 model  
- 🗂️ Maintains a 5-message memory buffer for conversational history  
- 🧪 Streamlit frontend for simple user interaction  
- 🌐 Flask-based backend for API processing

---

## 📦 Requirements

Install dependencies via:

```bash
pip install -r requirements.txt
