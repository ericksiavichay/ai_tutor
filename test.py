import openai
import prompt_toolkit
import os

engine = "gpt-4"
openai.api_key = os.environ["OPENAI_API_KEY"] # you might have to change this to your key
teacher_goal = "to learn string manipulation"
context = [
            {"role": "system", "content": f"You are a helpful tutor teaches students {teacher_goal}"}, # you can change this to 'You are an expert programmer that only outputs code" etc
        ]
main_objective = "Given a string s, find the length of the longest substring without repeating characters."

def call_openai_api(context, prompt=None):
    if prompt:
        context.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
        model=engine,  # Replace with the appropriate model name for GPT-4
        messages=context,
        # max_tokens=8192,
        n=1,
        stop=None,
        temperature=0.5,
    )
    ai_message = response['choices'][0]['message']['content'].strip()
    context.append({"role": "assistant", "content": ai_message})
    return ai_message

def check_answer(student_answer=None, correct_answer=None, question=main_objective):
    """
    The input is a json with the question and the students answer.
    This function determines if the answer is correct
    :param: question - the question that was asked 
    :param: answer - the user answer to the question
    :response: answer - [yes, no] Check if the user response is correct
    """
    # data = request.get_json()
    # question = data.get('question')
    # answer = data.get('answer')
    # context = [item.copy() for item in context]
    # if not prompt:
    #     return jsonify({'error': 'Invalid input. Please provide a prompt.'}), 400
    # if not context:
    #     return jsonify({'error': 'Invalid input. Please provide a context.'}), 400
    context.append({"role": "system", "content": "Suppose a question a student is trying to answer is the following: '" + question + "'\n" + ". The student's answer is: '" + student_answer + "'\n Is the above answer to the question correct? \n Think really hard before you answer. You can only say 'correct' or 'incorrect' as your response in regards to the current context."})
    response = call_openai_api(context, student_answer)
    # prompt = "Answer in one word is the students answer 'correct' or 'incorrect'?"
    # response = call_openai_api(prompt, response["context"])
    # answer = response["ai_message"].lower()
    # if answer not in ["correct", "incorrect"]:
    #     return {"error": "Invalid response from the GPT-4 model."}

    # if 'error' in response:
    #     return jsonify(response), 400
    return response

# def generate_similar_question()

print(f"Hello student! Here is your question to answer: {main_objective}")
current_objective = main_objective
# 1. First objective
debug_answer = """
def lengthOfLongestSubstring(self, s):
    mx, start, chars = 0, 0, \{\}
    for i in range(len(s)):
        if s[i] in chars and start <= chars[s[i]]: start = chars[s[i]] + 2
        else: mx = max(mx, i - start + 1)
        chars[s[i]] = i
    return mx
"""
while True:
    # student_answer = input("You: ")
    student_answer = debug_answer
    if check_answer(student_answer, main_objective) == "correct":
        print("Done. Congrats")
        break

    context.append({'role': 'system', 'content': "You are now a helpful tutor that asks a single helpful, follow-up question to help the student answer the original question in a guided manner. You give encouraging messages when the student answers the follow-up questions correctly."})
    follow_up_question = call_openai_api(context)
    print(f"\nGPT-4: {follow_up_question}\n")


print("Congrats! You answered the question correctly")

context.append({'role': 'system', 'content': f"You will now generate a similar question that also satisfies the original objective: {teacher_goal}."})
main_objective = call_openai_api(context)

print(main_objective)

# 2. Second concept question
while True:
    student_answer = input("You: ")
    if check_answer(student_answer, main_objective) == "correct":
        print("Done. Congrats")
        break

    context.append({'role': 'system', 'content': "You are now a helpful tutor that asks a single helpful, follow-up question to help the student answer the original question in a guided manner. You give encouraging messages when the student answers the follow-up questions correctly."})
    follow_up_question = call_openai_api(context)
    print(f"\nGPT-4: {follow_up_question}\n")

print("Second question correct. Done.")


    # while 
    # if check_answer(student_answer=student_answer, question=current_objective) == "correct":
    #     print("Congrats! You answered the current objective correctly")
    # elif check_answer(student_answer, question=current_objective) == "incorrect":
        

    # else:
    #     print("Invalid GPT-4 response")
    #     break


    # print(f"\nGPT-4: {response}\n")


"""
Potential problems

make sure the message history is stored/accessed/used efficiently """