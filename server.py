from flask import Flask, render_template, url_for, request, redirect, send_from_directory
# import os
import data_manager
from collections import OrderedDict
from datetime import datetime
import bcrypt

app = Flask(__name__)

#
# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                                'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/", methods=['GET', 'POST'])
def get_five():
    if request.method == 'GET':
        latest_questions = data_manager.get_latest_questions()
        return render_template("landing.html", all_data_reversed=latest_questions)
    elif request.method == "POST":
        search_text = request.form.get('search_text')
        return redirect(url_for('searched_question', search_text=search_text))


@app.route("/search_result/<search_text>")
def searched_question(search_text):
    search_result = data_manager.search_questions(search_text)
    return render_template('search_result.html', search_result=search_result)

"""
test
"""

@app.route("/list")
def get_question_list():
    order_by = request.args.get('order_by')
    order = request.args.get('order_direction')
    all_questions = data_manager.get_questions(order_by, order)
    return render_template("list.html", all_data_reversed=all_questions)


@app.route("/list/<question_id>", methods=['GET', 'POST'])
def q_id(question_id):
    question = data_manager.get_question_by_id(question_id)
    if request.method == 'GET':
        message = question['message']
        title = question['title']
        question_id = question['id']
        answers = data_manager.get_answer_by_question_id(question_id)
        if answers:
            answer_id = answers[0]['id']
        else:
            answer_id = 0
        print(answer_id)
        comments_questions = data_manager.get_question_comments(question_id)
        comments_answers = data_manager.get_answer_comments()
        print(comments_answers)
        return render_template("question_id.html", message=message, title=title, answers=answers,
                               question_id=question_id, comments_questions=comments_questions,
                               comments_answers=comments_answers, answer_id=answer_id)
    elif request.method == 'POST':
        if request.form["btn"] == "Send answer":
            answer = OrderedDict()
            answer['submission_time'] = datetime.now()
            answer['vote_number'] =	0
            answer['question_id'] = question_id
            answer['message'] = request.form.get('comment')
            answer['image'] = None
            data_manager.add_answer(answer)
            return redirect(url_for('get_question_list'))
        elif request.form['btn'] == "Delete question":
            data_manager.delete_question(question_id)
            data_manager.delete_answer(question_id)
            return redirect(url_for('get_question_list'))
        elif request.form['btn'] == "Edit question":
            return redirect(url_for('edit', question_id=question_id))


@app.route('/answer/<answer_id>/delete', methods=['POST'])
def delete_answer(answer_id):
    question_id = request.form.get('question_id')
    data_manager.delete_answer_by_id(answer_id)
    return redirect(url_for('q_id', question_id=question_id))


@app.route('/<question_id>/edit', methods=['GET', 'POST'])
def edit(question_id):
    question = data_manager.get_question_by_id(question_id)
    if request.method == 'GET':
        message = question['message']
        title = question['title']
        return render_template('edit.html', message=message, title=title)
    elif request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        data_manager.update_question(question_id, message, title)
        return redirect(url_for('get_question_list'))


@app.route("/add_question",  methods=['GET', 'POST'])
def add_question():
    if request.method == 'GET':
        return render_template('add_question.html')
    if request.method == 'POST':
        question = {'submission_time': datetime.now(), 'view_number': 0, 'vote_number': 0,
                    'title': request.form.get('title'), 'message': request.form.get('message'), 'image': None}
        data_manager.insert_question(question)
        return redirect(url_for('get_question_list'))


@app.route("/question/<question_id>/vote_up", methods=['GET', 'POST'])
def vote_question_up(question_id):
    vote_number = data_manager.get_vote_number(question_id)
    vote_number[0]['vote_number'] += 1
    data_manager.write_vote_number(question_id, vote_number[0]['vote_number'])
    return redirect('/list')


@app.route("/question/<question_id>/vote_down", methods=['GET', 'POST'])
def vote_question_down(question_id):
    vote_number = data_manager.get_vote_number(question_id)
    vote_number[0]['vote_number'] -= 1
    data_manager.write_vote_number(question_id, vote_number[0]['vote_number'])
    return redirect('/list')


@app.route("/question/<question_id>/new-comment", methods=['GET', 'POST'])
def add_question_comment(question_id):
    if request.method == 'GET':
        return render_template('add_comment.html')
    if request.method == 'POST':
        comment = request.form.get('comment')
        data_manager.write_comment_to_question(question_id, datetime.now(), comment)
    return redirect(url_for('q_id', question_id=question_id))


@app.route("/answer/<question_id>/<answer_id>/new-comment", methods=['GET', 'POST'])
def add_answer_comment(question_id, answer_id):
    if request.method == 'GET':
        return render_template('add_answer_comment.html', answer_id=answer_id)
    if request.method == 'POST':
        comment = request.form.get('comment')
        data_manager.write_comment_to_answer(answer_id, datetime.now(), comment)
        print(question_id)
    return redirect(url_for('q_id', question_id=question_id))


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    if request.method == 'POST':
        password = request.form.get('password')
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed = hashed.decode('utf-8')
        users = {'email': request.form.get('email'), 'user_name': request.form.get('user_name'), 'password': hashed}
        data_manager.insert_registration(users)
    latest_questions = data_manager.get_latest_questions()
    return render_template("landing.html", all_data_reversed=latest_questions)



if __name__ == "__main__":
    app.run(debug=True)
