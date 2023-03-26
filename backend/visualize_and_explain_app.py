import openai
from flask import Flask, request, jsonify

# Set up OpenAI API credentials
openai.api_key = "YOUR_API_KEY_HERE"
PREFIX_MSG= "generate some html, css and javascript code to explain a 4th grader, give me answer in code block no explanation. How to: "
SUFFIX_MSG =  " provide me an input to test my understanding of each single sub step, and correct me after each substep"
# Initialize Flask app
app = Flask(__name__)

# Define endpoint for visualizing and explaining input text
@app.route('/visualize_and_explain', methods=['POST'])
def visualize_and_explain():
    # Get input text from request body
    input_question = request.json['input_text']
    prompt = PREFIX_MSG + input_question + SUFFIX_MSG
    messages = [{"role": "user", "content": prompt}]

    # Call GPT-3.5 API to generate response
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages)

    # Extract and return generated text from API response
    generated_text = response.choices[0].message.strip()
    return jsonify({'generated_text': generated_text})

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)