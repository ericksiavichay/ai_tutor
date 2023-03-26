import openai
import prompt_toolkit
import os

engine = "gpt-4"
openai.api_key = "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" # you might have to change this to your key

def generate_response(prompt, conversation_history):
    conversation_history.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Replace with the appropriate model name for GPT-4
        messages=conversation_history,
        # max_tokens=8192,
        n=1,
        stop=None,
        temperature=0.5,
    )
    ai_message = response['choices'][0]['message']['content'].strip()
    conversation_history.append({"role": "assistant", "content": ai_message})
    return ai_message

conversation_history = [
            {"role": "system", "content": "You are a helpful assistant."}, # you can change this to 'You are an expert programmer that only outputs code" etc
        ]
while True:
    user_input = input("You: ")
    if user_input.lower() == "bye":
        print("Assistant: Goodbye!")
        break
   
    response = generate_response(user_input, conversation_history)
    print(f"GPT-4: {response}")


"""
Potential problems

make sure the message history is stored/accessed/used efficiently """