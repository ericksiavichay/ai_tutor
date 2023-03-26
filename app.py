import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = "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"
engine = "gpt-4"
conversation_history = [
            {"role": "system", "content": "You are a helpful assistant, and an expert in all things."}, # you can change this to 'You are an expert programmer that only outputs code" etc
        ]

@app.route('/check_answer', methods=['POST'])
def check_answer():
    """
    The input is a json with the question and the students answer.
    This function determines if the answer is correct
    :param: question - the question that was asked 
    :param: answer - the user answer to the question
    :response: answer - [yes, no] Check if the user response is correct
    """
    data = request.get_json()
    question = data.get('question')
    answer = data.get('answer')
    prompt = "Suppose a question a student is trying to answer is the following: '" + question + "'\n" + ". The student's answer is: '" + answer + "'\n Is the above answer to the question correct \n Think really hard before you answer"
    context = [item.copy() for item in conversation_history]
    if not prompt:
        return jsonify({'error': 'Invalid input. Please provide a prompt.'}), 400
    if not context:
        return jsonify({'error': 'Invalid input. Please provide a context.'}), 400
    # context.append({"role": "system", "content": "You can only say correct or incorrect, exclusively."})
    response = call_openai_api(prompt, context)
    prompt = "Answer in one word is the students answer 'correct' or 'incorrect'?"
    response = call_openai_api(prompt, response["context"])
    answer = response["ai_message"].lower()
    if answer not in ["correct", "incorrect"]:
        return {"error": "Invalid response from the GPT-4 model."}

    if 'error' in response:
        return jsonify(response), 400

    return jsonify({"answer": answer}), 200

def call_openai_api(prompt, context):
    try:
        context.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Replace with the appropriate model name for GPT-4
            messages=context,
            # max_tokens=8192,
            n=1,
            stop=None,
            temperature=0.5,
        )
        ai_message = response['choices'][0]['message']['content'].strip()
        context.append({"role": "assistant", "content": ai_message})

        return {"ai_message": ai_message, "context": context}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@app.route('/generate_question', methods=['POST'])
def generate_question():
    data = request.get_json()
    context = data.get('context')
    system_content = """
        Given that the student has not answered the question correctly, create a follow-up question that will aid the student in achieving the final objective that was stated earlier in the context. Ask the student a question to probe if they are confused with this follow-up response. Do not give the student the final answer either; only guide them.
        Start with the sentence, 'Here is a follow-up question to help you reach the next step: '. Afterwards, generate a follow-up question after the colon.
    """
    context.append({"role": "system", "content": {system_content}})
    ai_contents = call_openai_api("", context) # ai_message, context
    
    return ai_contents

if __name__ == '__main__':
    app.run()
