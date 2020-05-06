from flask import Flask, render_template, url_for, request, redirect, send_from_directory, session, flash
import os
import data_manager
from collections import OrderedDict
from datetime import datetime
import bcrypt

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/", methods=['GET', 'POST'])
def get_five():
    user_name = session.get('username')
    if request.method == 'GET':
        latest_questions = data_manager.get_latest_questions()
        return render_template("landing.html", all_data_reversed=latest_questions, user_name=user_name)
    elif request.method == "POST":
        search_text = request.form.get('search_text')
        return redirect(url_for('searched_question', search_text=search_text))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    correct_password = False
    if request.method == 'POST':
        username = request.form.get('login_name')
        password_entered = request.form.get('password')
        user_data = data_manager.get_user(username)
        if user_data:
            hashed_password = user_data['password']
            correct_password = data_manager.verify_password(password_entered, hashed_password)
            if correct_password:
                session['username'] = username
                # flash('Success, you are now logged in!')
            else:
                error = "Invalid credentials!"
                return render_template('landing.html', error=error, user_name=username)
        else:
            error = "Invalid credentials!"
            return render_template('landing.html/', error=error, user_name=username)
        return redirect(url_for('get_five'))
    latest_questions = data_manager.get_latest_questions()
    if 'username' in session:
        flash('Please log out first, before logging in.')
        return render_template('landing.html', all_data_reversed=latest_questions, user_name=session.get('username'))
    return render_template('landing.html', all_data_reversed=latest_questions, user_name=session.get('username'))


@app.route("/search_result/<search_text>")
def searched_question(search_text):
    search_result = data_manager.search_questions(search_text)
    return render_template('search_result.html', search_result=search_result, user_name=session.get('username'))


@app.route("/list")
def get_question_list():
    order_by = request.args.get('order_by')
    order = request.args.get('order_direction')
    all_questions = data_manager.get_questions(order_by, order)
    return render_template("list.html", all_data_reversed=all_questions, user_name=session.get('username'))


@app.route("/list/<question_id>", methods=['GET', 'POST'])
def q_id(question_id):
    question = data_manager.get_question_by_id(question_id)
    if request.method == 'GET':
        if 'username' in session:
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
                                   comments_answers=comments_answers, answer_id=answer_id, user_name=session.get('username'))
        else:
            return redirect(url_for('login'))
    elif request.method == 'POST':
        username = session['username']
        user_data = data_manager.get_user(username)
        if request.form["btn"] == "Send answer":
            answer = OrderedDict()
            answer['submission_time'] = datetime.now()
            answer['vote_number'] =	0
            answer['question_id'] = question_id
            answer['message'] = request.form.get('comment')
            answer['image'] = None
            answer['user_id'] = user_data['id']
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
        return render_template('edit.html', message=message, title=title, user_name=session.get('username'))
    elif request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        data_manager.update_question(question_id, message, title)
        return redirect(url_for('get_question_list'))


@app.route("/add_question",  methods=['GET', 'POST'])
def add_question():
    if request.method == 'GET':
        if 'username' in session:
            return render_template('add_question.html', user_name=session.get('username'))
        else:
            return redirect(url_for('login'))
    if request.method == 'POST':
        username = session['username']
        user_data = data_manager.get_user(username)
        question = {'submission_time': datetime.now(), 'view_number': 0, 'vote_number': 0,
                    'title': request.form.get('title'), 'message': request.form.get('message'), 'image': None,
                    'user_id': user_data['id']}

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
    username = session['username']
    user_data = data_manager.get_user(username)
    if request.method == 'GET':
        if 'username' in session:
            return render_template('add_comment.html', user_name=session.get('username'))
        else:
            return redirect(url_for('login'))
    if request.method == 'POST':
        comment = request.form.get('comment')
        data_manager.write_comment_to_question(question_id, datetime.now(), comment, user_data['id'])
    return redirect(url_for('q_id', question_id=question_id))


@app.route("/answer/<question_id>/<answer_id>/new-comment", methods=['GET', 'POST'])
def add_answer_comment(question_id, answer_id):
    username = session['username']
    user_data = data_manager.get_user(username)
    if request.method == 'GET':
        if 'username' in session:
            return render_template('add_answer_comment.html', answer_id=answer_id, user_name=session.get('username'))
        else:
            return redirect(url_for('login'))
    if request.method == 'POST':
        comment = request.form.get('comment')
        data_manager.write_comment_to_answer(answer_id, datetime.now(), comment, user_data['id'])
    return redirect(url_for('q_id', question_id=question_id))


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    if request.method == 'POST':
        password = request.form.get('password')
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed = hashed.decode('utf-8')
        users = {'email': request.form.get('email'), 'user_name': request.form.get('user_name'), 'password': hashed, 'registration_time': datetime.now()}
        data_manager.insert_registration(users)
    latest_questions = data_manager.get_latest_questions()
    return render_template("landing.html", all_data_reversed=latest_questions, user_name=session.get('username'))


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    flash("You have logged out!")
    return redirect(url_for('login'))


@app.route('/user-profile')
def user_profile():
    username = session.get('username')
    if username is None:
        data = None
        return render_template('user-profile.html', user_id=None,
                               registration_time=None,
                               email=None,
                               username=None)
    else:
        user_data = data_manager.select_user_by_username(username)
        registration_time = user_data[0]['registration_time']
        email = user_data[0]['email']
        username = user_data[0]['user_name']
        user_id = data_manager.get_id_by_username(username)
        user_id = user_id[0]['id']
        question_data = data_manager.question_number_by_user(user_id)
        question_number = question_data[0]['count']
        answer_data = data_manager.answer_number_by_user(user_id)
        answer_number = answer_data[0]['count']
        question_per_user = data_manager.get_question_per_user_id(user_id)
        answer_per_user = data_manager.get_answer_per_user_id(user_id)
        comment_data = data_manager.comment_number_by_user(user_id)
        comment_number = comment_data[0]['count']
        comment_per_user = data_manager.get_comment_per_user_id(user_id)
        return render_template('user-profile.html', user_id=user_id,
                               registration_time=registration_time,
                               email=email,
                               username=username,
                               question_number=question_number,
                               answer_number=answer_number, comment_per_user=comment_per_user,
                               answer_per_user=answer_per_user, question_per_user=question_per_user, comment_number=comment_number)


@app.route('/users')
def users():
    all_user_data = data_manager.get_users()
    return render_template("users.html", all_users=all_user_data)


if __name__ == "__main__":
    app.run(debug=True)
