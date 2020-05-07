import bcrypt
from psycopg2.extras import RealDictCursor

import database_common


@database_common.connection_handler
def get_questions(cursor: RealDictCursor, order_by_col=2, order="asc") -> list:
    which = {
        'title': 5, 'submission_time': 2, 'message': 6, 'view_number': 3, 'vote_number': 4,
        None: 2}
    if not order:
        order = "desc"
    if order == "desc":
        query = """
            SELECT id, submission_time,
            view_number, vote_number, title, message, 
            image, user_id
            FROM question
            ORDER BY %(ceca)s DESC"""
    else:
        query = """
            SELECT id, submission_time,
            view_number, vote_number, title, message, 
            image, user_id
            FROM question
            ORDER BY %(ceca)s"""
    cursor.execute(query, {'ceca': which[order_by_col]})

    return cursor.fetchall()


@database_common.connection_handler
def get_vote_number(cursor: RealDictCursor, q_id: int) -> list:
    query = """
        SELECT vote_number
        FROM question
        WHERE id = %(q_id)s"""
    cursor.execute(query, {'q_id': q_id})
    return cursor.fetchall()


@database_common.connection_handler
def write_vote_number(cursor: RealDictCursor, q_id: int, v_number):
    query = """
        UPDATE question SET vote_number = %(vote_number)s
        WHERE id = %(q_id)s"""
    cursor.execute(query, {'vote_number': v_number, 'q_id': q_id})


@database_common.connection_handler
def get_question_by_id(cursor: RealDictCursor, question_id):
    query = """
        SELECT id, to_char(submission_time, 'dd-Mon-YYYY hh:mm:ss') as submission_time,
            view_number, vote_number, title, message, 
            image, user_id FROM question WHERE id = %(qid)s;"""
    cursor.execute(query, {'qid': question_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_answers(cursor: RealDictCursor) -> list:
    query = """
        SELECT *
        FROM answer
        ORDER BY id;"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_accepted_by_answer_id(cursor: RealDictCursor, answer_id) -> list:
    query = """
        SELECT accepted
        FROM answer WHERE id = %(aid)s;"""
    cursor.execute(query, {'aid': answer_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_by_question_id(cursor: RealDictCursor, question_id):
    query = """
        SELECT * FROM answer WHERE question_id = %(qid)s;"""
    cursor.execute(query, {'qid': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def add_answer(cursor: RealDictCursor, answer_details):
    query = """
        INSERT INTO answer  (submission_time, vote_number, question_id, message, user_id)
        VALUES(%(s_t)s, %(v_n)s, %(q_i)s, %(m_g)s, %(u_id)s);"""
    cursor.execute(query, {
        's_t': answer_details['submission_time'],
        'v_n': answer_details['vote_number'],
        'q_i': answer_details['question_id'],
        'm_g': answer_details['message'],
        'u_id': answer_details['user_id']
    })
    return


@database_common.connection_handler
def delete_question(cursor: RealDictCursor, qid: int):
    query = """
        DELETE FROM question WHERE id = %(qid)s;"""
    cursor.execute(query, {'qid': qid})
    return


@database_common.connection_handler
def delete_answer(cursor: RealDictCursor, question_id: int):
    query = """
        DELETE FROM answer WHERE question_id = %(q_id)s;"""
    cursor.execute(query, {'q_id': question_id})
    return


@database_common.connection_handler
def insert_registration(cursor: RealDictCursor, users: dict):
    query = """
        INSERT INTO users (registration_time, email, user_name, password)
        VALUES (%(registration_time)s, %(email)s, %(u_name)s, %(p_word)s);"""
    cursor.execute(query, {
        'u_name': users['user_name'],
        'p_word': users['password'],
        'email': users['email'],
        'registration_time': users['registration_time']
    })
    return


@database_common.connection_handler
def select_user_by_username(cursor: RealDictCursor, username):
    query = """
            SELECT id, email, user_name, password, 
            to_char(registration_time, 'dd-Mon-YYYY hh:mm:ss') as registration_time, 
            reputation FROM users WHERE user_name = %(username)s;"""
    cursor.execute(query, {'username': username})
    return cursor.fetchall()


@database_common.connection_handler
def update_question(cursor: RealDictCursor, question_id: int, message: str, title: str):
    query = """
        UPDATE question 
        SET title = %(tt)s, message = %(msg)s
        WHERE id = %(qid)s;"""
    cursor.execute(query, {'tt': title, 'msg': message, 'qid': question_id})
    return


@database_common.connection_handler
def insert_question(cursor: RealDictCursor, question: dict):
    query = """
        INSERT INTO question (submission_time, title, message, vote_number, view_number, user_id)
        VALUES (%(st)s, %(ttl)s, %(msg)s, %(vo_n)s, %(vi_n)s, %(u_id)s) ;"""
    cursor.execute(query, {
        'st': question['submission_time'],
        'msg': question['message'],
        'ttl': question['title'],
        'vo_n': question['vote_number'],
        'vi_n': question['view_number'],
        'u_id': question['user_id']

    })
    return


@database_common.connection_handler
def delete_answer_by_id(cursor: RealDictCursor, answer_id: int):
    query = """
        DELETE FROM answer WHERE id = %(aid)s;"""
    cursor.execute(query, {'aid': answer_id})
    return


@database_common.connection_handler
def update_answer_by_id(cursor: RealDictCursor, answer_id: int, accepted):

    query = """
        UPDATE answer SET accepted = %(acp)s WHERE id = %(aid)s;"""
    cursor.execute(query, {'acp': accepted, 'aid': answer_id})
    return


@database_common.connection_handler
def write_comment_to_question(cursor: RealDictCursor, q_id, s_time, ct, u_id):
    query = """
    INSERT INTO comment(question_id, submission_time, message, user_id)
    VALUES (%(q_id)s, %(s_time)s, %(ct)s, %(u_id)s);"""
    cursor.execute(query, {'q_id': q_id, 's_time': s_time, 'ct': ct, 'u_id': u_id})


@database_common.connection_handler
def get_question_comments(cursor: RealDictCursor, qid) -> list:
    query = """
        SELECT *
        FROM comment WHERE question_id = %(qid)s
        ORDER BY submission_time"""
    cursor.execute(query, {'qid': qid})
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_comments(cursor: RealDictCursor) -> list:
    query = """
        SELECT *
        FROM comment WHERE answer_id is not null
        ORDER BY submission_time"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def write_comment_to_answer(cursor: RealDictCursor, a_id, s_time, ct, u_id):
    query = """
    INSERT INTO comment(answer_id, submission_time, message, user_id)
    VALUES (%(a_id)s, %(s_time)s, %(ct)s, %(u_id)s);"""
    cursor.execute(query, {'a_id': a_id, 's_time': s_time, 'ct': ct, 'u_id': u_id})


@database_common.connection_handler
def get_latest_questions(cursor: RealDictCursor) -> list:
    query = """
        SELECT id, submission_time,
        view_number, vote_number, title, message, 
        image, user_id
        FROM question
        ORDER BY 2 DESC LIMIT 5"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def search_questions(cursor: RealDictCursor, s_t) -> list:
    search_expression = f"%{s_t}%"
    query = """
        SELECT *
        FROM question
        WHERE message ILIKE %(search)s
        ORDER BY submission_time"""
    cursor.execute(query, {'search': search_expression})
    return cursor.fetchall()


@database_common.connection_handler
def get_user(cursor: RealDictCursor, username):
    query = """
        SELECT id, email, user_name, password, 
            to_char(registration_time, 'dd-Mon-YYYY hh:mm:ss') as registration_time, 
            reputation
        FROM users
        WHERE user_name = %(usern)s"""
    cursor.execute(query, {'usern': username})
    return cursor.fetchone()


@database_common.connection_handler
def get_user_by_id(cursor: RealDictCursor, user_id):
    query = """
        SELECT user_name
        FROM users
        WHERE id = %(usi)s"""
    cursor.execute(query, {'usi': user_id})
    return cursor.fetchall()


def verify_password(plain_text_password, hashed_pw):
    hashed_bytes_password = hashed_pw.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


@database_common.connection_handler
def update_visited(cursor: RealDictCursor, q_id, view_number):
    query = """
        UPDATE question SET view_number = %(view_number)s
        WHERE id = %(q_id)s"""
    cursor.execute(query, {'view_number': view_number, 'q_id': q_id})


@database_common.connection_handler
def get_users(cursor: RealDictCursor):
    query = """
        SELECT users.id, to_char(registration_time, 'dd-Mon-YYYY hh:mm:ss') as registration_time,
        user_name, 
        COUNT(DISTINCT question.id) AS question_count,
        COUNT(DISTINCT answer.id) AS answer_count,
        COUNT(DISTINCT comment.id) AS comment_count
        FROM users
        LEFT JOIN question ON question.user_id = users.id
        LEFT JOIN answer ON answer.user_id = users.id
        LEFT JOIN comment ON comment.user_id = users.id
        GROUP BY users.id"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_question_per_user_id(cursor: RealDictCursor, user_id):
    query = """
            SELECT id, title, message
            FROM question
            WHERE user_id = %(user_id)s"""
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_per_user_id(cursor: RealDictCursor, user_id):
    query = """
            SELECT id, message, question_id
            FROM answer
            WHERE user_id = %(user_id)s"""
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_comment_per_user_id(cursor: RealDictCursor, user_id):
    query = """
            SELECT id, message
            FROM comment
            WHERE user_id = %(user_id)s"""
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_id_by_username(cursor: RealDictCursor, username):
    query = """
            SELECT id
            FROM users
            WHERE user_name = %(usern)s"""
    cursor.execute(query, {'usern': username})
    return cursor.fetchall()


@database_common.connection_handler
def comment_number_by_user(cursor: RealDictCursor, user_id):
    query = """
            SELECT COUNT(user_id)
            FROM comment
            WHERE user_id = %(user_id)s"""
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()



@database_common.connection_handler
def question_number_by_user(cursor: RealDictCursor, user_id):
    query = """
            SELECT COUNT(user_id)
            FROM question
            WHERE user_id = %(user_id)s"""
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@database_common.connection_handler
def answer_number_by_user(cursor: RealDictCursor, user_id):
    query = """
            SELECT COUNT(user_id)
            FROM answer
            WHERE user_id = %(user_id)s"""
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@database_common.connection_handler
def bind_answer(cursor: RealDictCursor):
    query = """
            SELECT user_id, COUNT(id) 
            FROM answer
            GROUP BY user_id
            ORDER BY user_id"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_userid_by_question(cursor: RealDictCursor, question_id):
    query = """
                SELECT user_id
                FROM question
                WHERE id = %(question_id)s """
    cursor.execute(query, {'question_id' : question_id})
    return cursor.fetchall()

@database_common.connection_handler
def update_reputation(cursor: RealDictCursor, user_id, change):
    query = """
                UPDATE users 
                SET reputation = reputation + %(change)s
                WHERE id = %(id)s """
    cursor.execute(query, {'id' : user_id, 'change' : change})
    return

@database_common.connection_handler
def get_userid_by_answer(cursor: RealDictCursor, answer_id):
    query = """
                SELECT user_id
                FROM answer
                WHERE id = %(answer_id)s """
    cursor.execute(query, {'answer_id' : answer_id})
    return cursor.fetchall()

