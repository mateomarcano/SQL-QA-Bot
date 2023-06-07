from flask import Flask, request, jsonify
import json
import os
from database_qa import database_qa
from replit import db

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello from Flask!'

@app.route('/database_qa', methods=['POST'])
def qa_data():
    body_unicode = request.data.decode('utf-8')
    print(body_unicode)
    request_data = json.loads(body_unicode)
    question = request_data['question']
    api_key = request_data['api_key']
    if api_key != os.environ['TEST_KEY']:
        return jsonify({"result": "Invalid API key"})
    else:
        answer = database_qa(question)
        db['saves'].append({'answer' : answer['result'], 'question' : question, 'query' : answer['intermediate_steps'][0]})
        return jsonify({"result": answer['result']})



app.run(host='0.0.0.0', port=81)
