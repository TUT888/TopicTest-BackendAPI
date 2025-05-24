import re
import os
import requests
from dotenv import load_dotenv

from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()
app = Flask(__name__)

# ENV variable setup
API_URL = os.getenv('API_URL', '')
API_TOKEN = os.getenv('API_TOKEN', '')
MODEL = os.getenv('MODEL', '')

# Mongo setup
app.config["MONGO_URI"] = os.getenv('MONGO_URI', '')
if not app.config["MONGO_URI"]:
    raise ValueError("MONGO_URI environment variable not set")
mongo = PyMongo(app)
client = MongoClient(app.config["MONGO_URI"], server_api=ServerApi('1'))

# ========== AI model support functions ========== #
# API setup
HEADERS = {"Authorization": "Bearer {}".format(API_TOKEN)}

def fetchQuizFromLlama(student_topic):
    print("Fetching quiz from Hugging Face router API")
    payload = {
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Generate a quiz with 3 questions to test students on the provided topic. "
                    f"For each question, generate 3 options where only one of the options is correct. "
                    f"Format your response as follows:\n"
                    f"**QUESTION 1:** [Your question here]?\n"
                    f"**OPTION 1:** [First option]\n"
                    f"**OPTION 2:** [Second option]\n"
                    f"**OPTION 3:** [Third option]\n"
                    f"**ANS:** [Correct answer number]\n\n"
                    f"**QUESTION 2:** [Your question here]?\n"
                    f"**OPTION 1:** [First option]\n"
                    f"**OPTION 2:** [Second option]\n"
                    f"**OPTION 3:** [Third option]\n"
                    f"**ANS:** [Correct answer number]\n\n"
                    f"**QUESTION 3:** [Your question here]?\n"
                    f"**OPTION 1:** [First option]\n"
                    f"**OPTION 2:** [Second option]\n"
                    f"**OPTION 3:** [Third option]\n"
                    f"**ANS:** [Correct answer number]\n\n"
                    f"Ensure text is properly formatted. It needs to start with a question, then the options, and finally the correct answer. "
                    f"Follow this pattern for all questions. "
                    f"Here is the student topic:\n{student_topic}"
                )
            }
        ],
        "model": MODEL,
        "max_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.9
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        result = response.json()["choices"][0]["message"]["content"]
        print("=== [RECEIVED RESULT] ===")
        print(result)
        return result
    else:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

def process_quiz(quiz_text):
    questions = []
    # Updated regex to match bolded format with numbered questions
    pattern = re.compile(
        r'\*\*QUESTION \d+:\*\*\s+(.+?)\s+'
        r'\*\*OPTION 1:\*\*\s+(.+?)\s+'
        r'\*\*OPTION 2:\*\*\s+(.+?)\s+'
        r'\*\*OPTION 3:\*\*\s+(.+?)\s+'
        r'\*\*ANS:\*\*\s+(\d+)',
        re.DOTALL
    )
    matches = pattern.findall(quiz_text)

    for match in matches:
        question = match[0].strip()
        options = [match[1].strip(), match[2].strip(), match[3].strip()]
        correct_ans = match[4].strip()

        question_data = {
            "question": question,
            "options": options,
            "correct_answer": correct_ans
        }
        questions.append(question_data)

    return questions

def fetchReviewFromLlama(quizzes_result):
    print("Fetching quiz from Hugging Face router API")
    payload = {
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Provide a quick review on student performance based on completed quizzes result.\n"
                    f"Review should be in one paragraph only.\n"
                    f"Below are the result for each topic\n"
                    f"{'\n\n'.join(quizzes_result)}"
                )
            }
        ],
        "model": MODEL,
        "max_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.9
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        result = response.json()["choices"][0]["message"]["content"]
        print("=== [RECEIVED REVIEW RESULT] ===")
        print(result)
        return result
    else:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")
    
# ========== Test routes ========== #
# Route to test json response
@app.route('/test', methods=['GET'])
def run_test():
    return jsonify({'quiz': "test"}), 200

# Route to confirm MongoDB Atlas connection
@app.route("/ping", methods=["GET"])
def ping_mongodb():
    try:
        client.admin.command('ping')
        return jsonify({"message": "Successfully connected to MongoDB Atlas!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ========== AI API routes ========== #
# Get quiz
@app.route('/getQuiz', methods=['GET'])
def get_quiz():
    print("=== [RECEIVED REQUEST] ===")
    student_topic = request.args.get('topic')
    if not student_topic:
        return jsonify({'error': 'Missing topic parameter'}), 400
    try:
        quiz = fetchQuizFromLlama(student_topic)
        processed_quiz = process_quiz(quiz)
        
        print("=== [PROCESSED RESULT] ===")
        print(processed_quiz)
        if not processed_quiz:
            return jsonify({'error': 'Failed to parse quiz data', 'raw_response': quiz}), 500
        return jsonify({'quiz': processed_quiz}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== Page rendering routes ========== #
# For landing page
@app.route("/", methods=["GET"])
def welcome_page():
    return render_template("welcome.html")

# For profile sharing
@app.route("/share_profile", methods=["GET"])
def get_shared_profile():
    try:
        name = request.args['name'].upper()
        completed = request.args['completed']
        correct = request.args['correct']
        return render_template("profile.html", name=name, completed=completed, correct=correct)
    except Exception as e:
        return render_template("error.html")

# ========== Student routes ========== #
# Add a student
@app.route("/students", methods=["POST"])
def add_student():
    try:
        student_data = {
            "name": request.json["name"],
            "username": request.json["username"],
            "email": request.json["email"],
            "password": request.json["password"],
            "phone": request.json["phone"],
            "interest": request.json["interest"]
        }
        check_result = list(mongo.db.students.find({"username": student_data["username"]}))
        if (len(check_result)!=0):
            return jsonify({"message": "Username already existed", "status": "failed"}), 400
        
        result = mongo.db.students.insert_one(student_data)
        student_data["_id"] = str(result.inserted_id)
        return jsonify({"message": "Student added successfully", "student": student_data}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add new student: {str(e)}"}), 400

@app.route("/students/login", methods=["POST"])
def student_login():
    try:
        result = list(mongo.db.students.find({
            "username": request.json["username"] ,
            "password": request.json["password"]
        }))
        if (len(result)==0):
            return jsonify({"message": "Username or password is incorrect", "status": "failed"}), 400

        student = result[0]
        student["_id"] = str(student["_id"])
        return jsonify({"message": "Login successfully", "student": student}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to login: {str(e)}"}), 400

@app.route("/students/review", methods=["GET"])
def get_review():
    try:
        tasks = list(mongo.db.tasks.find({
            "student_id": ObjectId(request.args['student_id']),
            "finish": True
        }))
        
        questions = []
        for task in tasks:
            task_title = task["title"]
            correct = task["score"]
            total = len(task["listQuestions"])
            questions.append(f"Quiz topic: {task_title} -> {correct} correct out of {total} questions")
        
        received_review = fetchReviewFromLlama(questions)
        return jsonify({"message": "Get review successfully", "review": received_review}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to get review: {str(e)}"}), 400
    
# ========== Task routes ========== #
# Add a task
@app.route("/tasks", methods=["POST"])
def add_task():
    try:
        task_data = {
            "student_id": ObjectId(request.json["student_id"]),
            "title": request.json["title"],
            "description": request.json["description"],
            "finish": False,
            "score": 0,
            "listQuestions": request.json["listQuestion"]
        }
        result = mongo.db.tasks.insert_one(task_data)
        task_data["_id"] = str(result.inserted_id)
        return jsonify({"message": "Task added successfully", "task": task_data}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add new task: {str(e)}"}), 400

@app.route("/tasks/<id>", methods=["PUT"])
def update_task(id):
    try:
        task_data = {
            "finish": request.json["finish"],
            "score": request.json["score"],
            "listQuestions": request.json["listQuestion"]
        }
        print(id)
        print(task_data)
        result = mongo.db.tasks.update_one(
            {"_id": ObjectId(id)},
            {"$set": task_data}
        )
        if result.modified_count:
            task_data["_id"] = id
            return jsonify({"message": "Task updated successfully", "task": task_data}), 200
        return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to update task: {str(e)}"}), 400

@app.route("/tasks", methods=["GET"])
def get_all_tasks():
    try:
        tasks = list(mongo.db.tasks.find({
            "student_id": ObjectId(request.args['student_id']),
            "finish": request.args['finish'] == "1"
        }))
        
        for task in tasks:
            task["_id"] = str(task["_id"])
            task["student_id"] = str(task["student_id"])
        return jsonify({"message": "Get task data successfully", "tasks": tasks}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to get task data: {str(e)}"}), 400

@app.route("/tasks/<id>", methods=["DELETE"])
def delete_task(id):
    try:
        result = mongo.db.tasks.delete_one({"_id": ObjectId(id)})
        if result.deleted_count:
            return jsonify({"message": "Task deleted successfully"}), 200
        return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to delete task: {str(e)}"}), 400
    
# Launch server
if __name__ == '__main__':
    port_num = 5000
    print(f"App running on port {port_num}")
    app.run(port=port_num, host="0.0.0.0")
