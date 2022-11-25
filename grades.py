from flask import request, session, redirect, url_for, render_template, flash, Blueprint
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv, find_dotenv

# Start environment variables #

load_dotenv(find_dotenv())

#Database info below:

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

grades = Blueprint("grades", __name__)

@grades.route('/grade_ASC', methods=['GET'])
def grade_ASC():

    if 'loggedin' in session: # This orders the students by grade (lowest - highest)

        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute('SELECT * FROM users WHERE id = %s;', [session['id']])
        account = cursor.fetchone()

        cursor.execute("SELECT * FROM classes WHERE class_creator = %s ORDER BY student_grade ASC;", [session['email']])
        records_2 = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('class_roster.html', records_2=records_2, account=account, username=session['username'], class_name = session['class_name'])

    return redirect(url_for('login'))

@grades.route('/grade_DESC', methods=['GET'])
def grade_DESC():

    if 'loggedin' in session: # This orders the students by grade (highest - lowest)

        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute('SELECT * FROM users WHERE id = %s;', [session['id']])
        account = cursor.fetchone()

        cursor.execute("SELECT * FROM classes WHERE class_creator = %s ORDER BY student_grade DESC;", [session['email']])
        records_2 = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('class_roster.html', records_2=records_2, account=account, username=session['username'], class_name=session['class_name'])

    return redirect(url_for('login'))

@grades.route('/update_grade/<id>', methods=['PATCH', 'GET', 'POST'])
def update_grade(id):

    if 'loggedin' in session: # This updates the student grade via user input.

        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute('SELECT * FROM users WHERE id = %s;', [session['id']])
        account = cursor.fetchone()

        updated_grade = request.form.get("update grade")

        if not updated_grade:
            flash("Please enter a new grade if you wish to update the student's grade.")
            cursor.close()
            conn.close()
            return redirect(url_for('student_info_for_teachers.query'))
        if updated_grade.isalpha():
            flash("Please enter a new grade number if you wish to update the student's grade.")
            cursor.close()
            conn.close()
            return redirect(url_for('student_info_for_teachers.query'))
        else:
            cursor.execute('SELECT student_first_name FROM classes WHERE id = %s;', (id,))
            student_first_name = cursor.fetchone()
            cursor.execute('SELECT student_last_name FROM classes WHERE id = %s;', (id,))
            student_last_name = cursor.fetchone()
            cursor.execute('SELECT student_grade FROM classes WHERE id = %s;', (id,))
            student_grade = cursor.fetchone()

            cursor.execute("""UPDATE classes 
            SET student_grade = %s 
            WHERE id = %s;""", (updated_grade, id))

            for first_name, last_name, grade in zip(student_first_name, student_last_name, student_grade):
                flash(f"Grade updated from {grade} to {updated_grade} for {first_name} {last_name}!")

            conn.commit()

            cursor.execute("SELECT * FROM classes WHERE class_creator = %s;", [session['email']])
            records_2 = cursor.fetchall()

            cursor.close()
            conn.close()
            return redirect(url_for('student_info_for_teachers.query', records_2=records_2, account=account, username=session['username'], class_name=session['class_name']))

    return redirect(url_for('login'))

@grades.route('/edit_assignment_grade/<string:id>', methods=['GET'])
def edit_assignment_grade(id):

    if 'loggedin' in session: # This routes the user to the edit assignment grade page.

        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()

        cur = conn.cursor()

        cur.execute("SELECT assignment_name FROM assignments WHERE id = {0} AND assignment_creator = %s;".format(id), (session['email'],))
        records_2 = cur.fetchall()

        cur.execute('SELECT * FROM classes WHERE class_creator = %s;', [session['email']])
        records_3 = cur.fetchall()

        cur.execute("SELECT id FROM assignments WHERE id = {0} AND assignment_creator = %s;".format(id), (session['email'],))
        records_4 = cur.fetchone()

        session['assignment_id'] = records_4

        cur.execute("SELECT due_date FROM assignments WHERE id = {0} AND assignment_creator = %s;".format(id), (session['email'],))
        due_date = cur.fetchall()

        cur.execute("SELECT category FROM assignments WHERE id = {0} AND assignment_creator = %s;".format(id), (session['email'],))
        category = cur.fetchall()

        cur.execute("SELECT * FROM assignments WHERE id = {0} AND assignment_creator = %s;".format(id), (session['email'],))
        records_5 = cur.fetchone()
        session['assignment_id'] = records_5[0]
        session['assignment_name'] = records_5[1]

        cursor.close()
        conn.close()

        return render_template('edit_assignment_score.html', due_date=due_date, category=category, account=account, records_2=records_2, records_3=records_3, records_4=records_4, username=session['username'], class_name=session['class_name'])

    return redirect(url_for('login'))

@grades.route('/edit_assignment_grade_2', methods=['POST', 'GET'])
def edit_assignment_grade_2():

    if 'loggedin' in session:

        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        grade_assignment = request.form.get("grade_assignment")
        student_id = request.form.get("student_id")

        cur = conn.cursor()

        conn.commit()

        if not grade_assignment:
            flash('Please input the updated grade here.')
            cursor.close()
            conn.close()
            return redirect(url_for('assignment'))
        elif not student_id:
            flash('Please confirm the student ID here (located in this row on the left).')
            cursor.close()
            conn.close()
            return redirect(url_for('assignment'))
        elif grade_assignment.isalpha():
            flash('Please enter an assignment grade (0-100).')
            cursor.close()
            conn.close()
            return redirect(url_for('assignment'))
        elif student_id.isalpha():
            flash('Please enter a grade number between 0 - 100.')
            cursor.close()
            conn.close()
            return redirect(url_for('assignment'))
        else:
            cur.execute("""INSERT INTO assignment_results
            (score, student_id, assignment_id) VALUES (%s, %s, %s) 
            """, (grade_assignment, student_id, session['assignment_id']))

            conn.commit()

            cursor.execute("""SELECT ROUND(AVG(score)) FROM assignment_results WHERE student_id = %s""", (student_id,))

            updated_grade_average = cursor.fetchone()[0]

            cursor.execute("""UPDATE classes 
                            SET student_grade = %s
                            WHERE id = %s;""", (updated_grade_average, student_id))

            conn.commit()

            flash('Assignment grade successfully updated!')

            cursor.close()
            conn.close()

            return redirect(request.referrer)

    return redirect(url_for('login'))

@grades.route('/view_assignment_scores', methods=['GET'])
def view_assignment_scores():

    if 'loggedin' in session:

        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()

        cursor.execute("""SELECT
        ci.id AS score_id,
        s.student_first_name,
        s.student_last_name,
        ci.score,
        cu.assignment_name
        FROM classes s
        INNER JOIN assignment_results AS ci
        ON ci.student_id = s.id
        INNER JOIN assignments cu  
        ON cu.id = ci.assignment_id
        WHERE class_creator = %s
        ORDER BY cu.assignment_name ASC;""", [session['email']])

        assignment_scores = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('assignment_scores.html', account=account, assignment_scores=assignment_scores, username=session['username'], class_name=session['class_name'])

    return redirect(url_for('login'))

@grades.route('/view_assignment_scores_by_student', methods=['POST', 'GET'])
def view_assignment_scores_by_student():

    if 'loggedin' in session:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()

        session['student_name'] = request.form['student_name']

        cursor.execute("""SELECT
        ci.id AS score_id,
        s.student_first_name,
        s.student_last_name,
        ci.score,
        cu.assignment_name
        FROM classes s
        INNER JOIN assignment_results AS ci
        ON ci.student_id = s.id
        INNER JOIN assignments cu  
        ON cu.id = ci.assignment_id
        WHERE class_creator = %s AND s.student_last_name = %s
        ORDER BY cu.assignment_name ASC;""", [session['email'], session['student_name']])

        assignment_scores_by_student = cursor.fetchall()

        cursor.close()
        conn.close()

        if not assignment_scores_by_student:
            flash('Student not enrolled in class.')
            cursor.close()
            conn.close()

            return redirect(url_for('assignment'))

        return render_template('view_assignment_scores_by_student.html', account=account, assignment_scores_by_student=assignment_scores_by_student, username=session['username'], class_name=session['class_name'], student_name=session['student_name'])

    return redirect(url_for('login'))
