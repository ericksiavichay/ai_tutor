import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = "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"
engine = "gpt-4"
originial_context = [
            {"role": "system", "content": "You are a helpful assistant, and an expert in all things."}, # you can change this to 'You are an expert programmer that only outputs code" etc
        ]
context = originial_context
modules = ["fractions", "python basics"]
questions = {"fractions": ["What is sum of the fractions 3/4 and 8/12?", "What is the difference of the fractions 3/4 and 8/12?"], 
"python basics":["Given the radius return the circumference of a circle", "write a class with an init function that takes in the radius of a circle and a circumference function that returns the circumference of the circle"] }
goals = {"fractions": ["Learn how to add two fractions", "Learn how to subtract two fractions"],
"python_basics": ["Learn how to define functions in python that accept arguments and returns values", "Learn how to define and uses classes in python"]
}
@app.route('/get_modules', methods=['GET'])
def get_modules():
    return jsonify({"modules": modules}), 200

@app.route('/get_questions', methods=['GET'])
def get_questions():
    global context
    data = request.get_json()
    questions = data.get('module')
    context = originial_context
    return jsonify({"questions": questions[modules]}), 200

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
    student_answer = data.get('answer')
    question = data.get('question')
    check_context = [item.copy() for item in context]
    check_context.append({"role": "system", "content": "Suppose a question a student is trying to answer is the following: '" + question + "'\n" + ". The student's answer is: '" + student_answer + "'\n Is the above answer to the question correct? \n Think really hard before you answer. You can only say 'correct' or 'incorrect' as your response in regards to the current context."})

    # if not prompt:
    #     return jsonify({'error': 'Invalid input. Please provide a prompt.'}), 400
    if not context:
        return jsonify({'error': 'Invalid input. Please provide a context.'}), 400
    # context.append({"role": "system", "content": "You can only say correct or incorrect, exclusively."})
    '''ask correct or incorrect one more time and choose the second answer'''
    response = call_openai_api(check_context, student_answer)
    # prompt = "Answer in one word is the students answer 'correct' or 'incorrect'?"
    # response (prompt, response["context"])
    # answer = response["ai_message"].lower()
    if response not in ["correct", "incorrect"]:
        return {"error": "Invalid response from the GPT-4 model."}

    if 'error' in response:
        return jsonify(response), 400

    return jsonify({"answer": student_answer}), 200


def call_openai_api(context, prompt=None):
    try:
        if prompt:
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


@app.route('/student_query', methods=['POST'])
def student_query():
    data = request.get_json()
    system_content = """
    You are a helpful AI assistant. Provide a detailed explanation to the questions that the student asks you. Let's take it one step at a time 
    """
    context.append({"role": "system", "content": {system_content}})
@app.route('/generate_question', methods=['POST'])
def generate_question():
    # data = request.get_json()
    # context = data.get('context')
    system_content = f"You will now generate a similar question that also satisfies the original objective: {teacher_goal}."
    context.append({"role": "system", "content": {system_content}})
    ai_contents = call_openai_api(context) # ai_message, context
    
    return ai_contents

# Define endpoint for visualizing and explaining input text
@app.route('/visualize_and_explain', methods=['POST'])
def visualize_and_explain():
    # Get input text from request body
    question = request.json['question']
    PREFIX_MSG = "generate some html, css and javascript code to explain a 4th grader, give me answer in code block no explanation. How to: "
    SUFFIX_MSG =  "provide me an input to test my understanding of each single sub step. And correct me after each substep Don’t provide any text. CODE ONLY Start with <html> End with </html>"
    context = [
            {"role": "system", "content": "You are an expert programmer that only outputs code in a single file"}, # you can change this to 'You are an expert programmer that only outputs code" etc
        ]
    prompt = PREFIX_MSG + question + SUFFIX_MSG
    response = call_openai_api(prompt, context)
    code = response["ai_message"]
    context = [
                {"role": "system", "content": "You are an expert at explaining simple math concepts"}, # you can change this to 'You are an expert programmer that only outputs code" etc
            ]
    PREFIX_MSG = "Explain the answer to the following question to a 4th grader: "
    SUFFIX_MSG = "\nLet's take it one step at a time."
    prompt = PREFIX_MSG + question + SUFFIX_MSG
    response = call_openai_api(prompt, context)
    explanation  = response["ai_message"]
    return jsonify({"html": code, "explanation": explanation}), 200

if __name__ == '__main__':
    app.run()
