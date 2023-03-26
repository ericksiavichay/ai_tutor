import streamlit as st
import requests
import random

def fetch_modules():
    return ["math", "cs", "Module 3"]
    try:
        response = requests.get("http://localhost:5000/get_modules_with_progress")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching modules: {e}")
        return []

def fetch_questions(module):
    return ["Question 1", "Question 2", "Question 3"]
    try:
        response = requests.get(f"http://localhost:5000/get_questions?module={module}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching questions: {e}")
        return []

def check_answer(question, answer):
    value = random.choice(["correct", "not correct"])
    print(value)
    return value
    try:
        response = requests.post("http://localhost:5000/check_answer", json={"question": question, "answer": answer})
        response.raise_for_status()
        return response.json().get("result")
    except requests.exceptions.RequestException as e:
        st.error(f"Error checking answer: {e}")
        return None

def freeform_query(question, user_query):
    return "Answer"
    try:
        response = requests.post("http://localhost:5000/student_query", json={"question": question, "student_query": user_query})
        response.raise_for_status()
        return response.json().get("response")
    except requests.exceptions.RequestException as e:
        st.error(f"Error sending freeform query: {e}")
        return None

def display_module_selection(modules):
    st.subheader("Select a module:")
    for module in modules:
        if st.button(module):
            st.session_state.module_selected = module
            st.session_state.question_index = 0

def visualize_and_explain(question, answer):
    return {"explanation": "Explanation", "html": "<html><h1>This shit crazy</h1></html>"}
    try:
        response = requests.post("http://localhost:5000/visualize_and_explain", json={"question": question, "answer": answer})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching visualization and explanation: {e}")
        return None

def generate_question():
    return "Generated Question"
    try:
        response = requests.get("http://localhost:5000/generate_question")
        response.raise_for_status()
        return response.json().get("question")
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating question: {e}")
        return None


def display_questions_page(module):
    questions = fetch_questions(module)
    if not questions:
        st.warning("No questions available.")
        return

    question_index = st.session_state.get("question_index", 0)

    # if "show_wrong" in st.session_state and st.session_state.show_wrong:
    #     st.write("Wrong answer!")

    #     if st.button("Next"):
    #         generated_question = generate_question()
    #         st.session_state.generated_question = generated_question
    #         if question_index + 1 < len(questions):
    #             st.session_state.question_index = question_index + 1
    #         else:
    #             st.session_state.question_index = 0
    #         st.session_state.show_wrong = False

    #     visualization_data = visualize_and_explain(questions[question_index], st.session_state.user_answer)
    #     if visualization_data:
    #         st.write(visualization_data["explanation"])
    #         st.write("Visualization:")
    #         st.components.v1.html(visualization_data["html"], height=1000)
    current_question = st.session_state.generated_question if "generated_question" in st.session_state else questions[question_index]
    if "been_wrong" not in st.session_state:
        st.session_state.been_wrong = False
    if "generated_question" in st.session_state:
        del st.session_state.generated_question
    # print(1)
    with st.sidebar:
        st.write("Ask Questions")
        user_query = st.text_input("Your question:")
        if st.button("Ask", key="ask_button", help="Click to ask your question") or user_query:
            response = freeform_query(current_question, user_query)
            if response is not None:
                st.write(response)
    
    # st.write(f"Question {question_index + 1}/{len(questions)}:")
    st.write(current_question)
    user_answer = st.text_input("Your answer:")

    if st.button("Submit"):
        result = check_answer(current_question, user_answer)
        if result is not None:
            if result == "correct":
                # print(2, st.session_state.been_wrong)
                if "been_wrong" in st.session_state and st.session_state.been_wrong:
                    generated_question = generate_question()
                    print(generated_question)
                    st.session_state.generated_question = generated_question
                # if "generated_question" in st.session_state:
                #     del st.session_state.generated_question
                elif question_index + 1 < len(questions):
                    if "generated_question" in st.session_state:
                        del st.session_state.generated_question
                    st.session_state.question_index = question_index + 1
                else:
                    if "generated_question" in st.session_state:
                        del st.session_state.generated_question 
                    st.session_state.question_index = 0
            else:
                st.session_state.been_wrong = True
                # print(3)
                if module == "math":
                    visualization_data = visualize_and_explain(current_question, user_answer)
                    if visualization_data:
                        st.write(visualization_data["explanation"])
                        st.write("Visualization:")
                        st.components.v1.html(visualization_data["html"], height=1000)
                elif module == "cs":
                    hint = requests.get("http://localhost:5000/get_hint?question={question}&answer={answer}")
                    st.write(hint)



def display_teacher_mode():
    st.subheader("Create a Learning Module:")
    module_name = st.text_input("Module Name:")

    st.write("Enter questions for the module:")
    questions = []
    count = int(st.number_input("Number of questions:", min_value=1, max_value=10, value=1, step=1, help="Enter the number of questions for the module"))

    for i in range(count):
        question = st.text_input(f"Question {i + 1}:")
        if question:
            questions.append(question)

    if st.button("Submit Module"):
        try:
            response = requests.post("http://localhost:5000/create_learning_module", json={"module_name": module_name, "questions": questions})
            response.raise_for_status()
            st.success("Learning module created successfully.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error creating learning module: {e}")

def main():
    st.title("Questions App")

    st.sidebar.title("Mode")
    mode = st.sidebar.radio("Select a mode:", options=["Student", "Teacher"])

    

    if mode == "Student":
        modules = fetch_modules()
        if not modules:
            st.warning("No modules available.")
            return

        if "module_selected" not in st.session_state:
            display_module_selection(modules)
        else:
            selected_module = st.session_state.module_selected
            st.subheader(f"Module: {selected_module}")
            display_questions_page(selected_module)
            if st.button("Back to module selection"):
                del st.session_state.module_selected
                del st.session_state.question_index
    else:
        display_teacher_mode()

if __name__ == "__main__":
    main()

