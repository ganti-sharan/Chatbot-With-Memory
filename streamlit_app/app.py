import streamlit as st
import requests
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))  # Connect to a remote address to get the local IP
        local_ip = s.getsockname()[0]
    except:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

FLASK_API_URL = f"http://{get_local_ip()}:5000/query"

st.title("LLM-based RAG Search")

query = st.text_input("Enter your query:")

if st.button("Search"):
    if query:
        response = requests.post(FLASK_API_URL, json={"query": [query]})
        
        if response.status_code == 200:
            response_data = response.json()
            if "error" in response_data:
                st.error(response_data["error"])
            else:
                st.subheader("Agent Response")
                st.markdown(f"**Final Response:** {response_data['answer']}")
        else:
            st.error(f"Error: Something went wrong with the backend! Status code: {response.status_code}")
    else:
        st.warning("Please enter a query before searching.")
