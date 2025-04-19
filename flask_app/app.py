
from flask import Flask, request, jsonify
from utils import search_articles, concatenate_content, generate_answer
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query():
    """
    Handles the POST request to '/query'. Extracts the query from the request,
    processes it through the search, concatenate, and generate functions,
    and returns the generated answer.
    """
    query = request.json.get('query')
    
    try:
        
        articles = search_articles(query[0])
        full_text = concatenate_content(articles) 
        answer = generate_answer(full_text, query[0])
        
        return jsonify({"answer": answer}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
