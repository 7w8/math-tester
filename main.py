from flask import Flask, render_template, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user, login_required, logout_user
import random
from answers import all_dicts2
from data import db_session
from data.users import User
import sqlite3
import hashlib
from answers import all_dicts, all_dicts2


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class TestRandom:
    def __init__(self):
        self.questions = random.sample(list(all_dicts2.keys()), 10)

    def new_questions(self):
        self.questions = random.sample(list(all_dicts2.keys()), 10)

    def check_answers(self):
        grade, mistakes = 0, []
        for i in range(len(self.questions)):
            answer = "ans" + str(i + 1)
            if request.form[answer] == all_dicts2[self.questions[i]]:
                grade += 10
            else:
                mistakes.append((self.questions[i], request.form[answer], all_dicts2[self.questions[i]]))
        self.new_questions()
        result = (str(grade) + "%", mistakes)
        return result


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
test_obj = TestRandom()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    user = "Ученик Яндекс.Лицея"
    return render_template('index.html', title='Домашняя страница',
                           username=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and hashlib.md5(form.password.data.encode()).hexdigest() == user.password:
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user:
            return render_template('register.html',
                                   message="Этот логин уже занят",
                                   form=form)
        user = User()
        user.username = form.username.data
        user.password = hashlib.md5(form.password.data.encode()).hexdigest()
        user.done_count, user.mistakes_count, user.total_grade = 0, 0, 0
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect("/")
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/test', methods=['POST', 'GET'])
def test():
    if request.method == 'GET':
        return render_template('test.html', q1=test_obj.questions[0], q2=test_obj.questions[1],
                               q3=test_obj.questions[2], q4=test_obj.questions[3], q5=test_obj.questions[4],
                               q6=test_obj.questions[5], q7=test_obj.questions[6], q8=test_obj.questions[7],
                               q9=test_obj.questions[8], q10=test_obj.questions[9])
    elif request.method == 'POST':
        return render_template("result.html", result=test_obj.check_answers())


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(port=5000, host='127.0.0.1')
