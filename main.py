from flask import Flask, render_template, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import random
import os
from answers import all_dicts, all_dicts2
from data import db_session
from data.users import User
import hashlib


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
    def __init__(self, num=None):
        self.id = num
        if self.id is None:
            self.questions = random.sample(list(all_dicts2.keys()), 10)
        else:
            self.questions = random.sample(list(all_dicts[self.id].keys()), 10)

    def new_questions(self):
        if self.id is None:
            self.questions = random.sample(list(all_dicts2.keys()), 10)
        else:
            self.questions = random.sample(list(all_dicts[self.id].keys()), 10)

    def check_answers(self, user):
        db_sess = db_session.create_session()
        grade, mistakes = 0, []
        for i in range(len(self.questions)):
            answer = "ans" + str(i + 1)
            if request.form[answer] == all_dicts2[self.questions[i]]:
                grade += 10
            else:
                if user.is_authenticated:
                    if self.questions[i] in all_dicts[0]:
                        user.mistakes_0 += 1
                    if self.questions[i] in all_dicts[1]:
                        user.mistakes_1 += 1
                    if self.questions[i] in all_dicts[2]:
                        user.mistakes_2 += 1
                    if self.questions[i] in all_dicts[3]:
                        user.mistakes_3 += 1
                    if self.questions[i] in all_dicts[4]:
                        user.mistakes_4 += 1
                    mistakes.append((self.questions[i], request.form[answer], all_dicts2[self.questions[i]]))
        if user.is_authenticated:
            user.total_grade += grade
            user.done_count += 1
            db_sess.merge(user)
            db_sess.commit()
        self.new_questions()
        result = (str(grade) + "%", mistakes)
        return result


advice = ["Старайтесь вставать и ложиться в одно и то же время. Спите 7-8 часов в сутки.",
          "Придерживайтесь правильного питания. В вашем рационе круглый год должны быть овощи и фрукты.",
          "Занимайтесь фитнесом. Некоторые необходимые мозгу белки интенсивно вырабатываются только"
          " при физической нагрузке. Необязательно ходить в спортзал. Простая зарядка и прогулка "
          "уже существенно улучшают познавательные функции.", "Делайте перерывы каждые 25-30 минут интенсивной "
                                                              "мыслительной деятельности. Только не стоит во время "
                                                              "отдыха открывать социальные сети или смотреть сериалы "
                                                              "— новый поток информации не позволит расслабиться. "
                                                              "Лучше выпить чаю или просто полежать с закрытыми "
                                                              "глазами.",
          "Чередуйте предметы и темы, чтобы учиться было легче.", "Сосредотачивайтесь на одной задаче.",
          "Освойте один или несколько методов конспектирования. Конспекты — вовсе не долго и нудно, а легко и полезно. "
          "Правильно сделанная запись поможет осмыслить и запомнить информацию, и учиться станет легче. ",
          "Тренируйте скорочтение. Медленное чтение приводит к отвлечениям, от которых устаёшь. "
          "А главное, медленно читающий человек не успевает за растущим объёмом информации."]

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
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
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
    if current_user.is_authenticated:
        return redirect("/")
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
        user.done_count, user.mistakes_0, user.mistakes_1, \
        user.mistakes_2, user.mistakes_3, user.mistakes_4, user.total_grade = 0, 0, 0, 0, 0, 0, 0
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
        test_id = request.args.get("test_id")
        if test_id is None:
            test_obj.id = test_id
        else:
            if not test_id.isnumeric():
                return redirect("/")
            else:
                if int(test_id) > 4:
                    return redirect("/")
            test_obj.id = int(test_id)
        test_obj.new_questions()
        return render_template('test.html', q1=test_obj.questions[0], q2=test_obj.questions[1],
                               q3=test_obj.questions[2], q4=test_obj.questions[3], q5=test_obj.questions[4],
                               q6=test_obj.questions[5], q7=test_obj.questions[6], q8=test_obj.questions[7],
                               q9=test_obj.questions[8], q10=test_obj.questions[9])
    elif request.method == 'POST':
        return render_template("result.html", result=test_obj.check_answers(current_user))


@app.route('/test_index')
def test_index():
    return render_template('test_index.html')


@app.route("/account")
@login_required
def account():
    if current_user.done_count == 0:
        average = "0%"
    else:
        average = str(int(current_user.total_grade / current_user.done_count)) + "%"
    return render_template("account.html", username=current_user.username,
                           average=average,
                           worst=current_user.find_worst(), advice=random.choice(advice))


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
