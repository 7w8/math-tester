from flask import Flask, render_template, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import random
from answers import all_dicts, all_dicts2


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

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
test_obj = TestRandom()


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
        return redirect('/')
    return render_template('login.html', title='Авторизация', form=form)

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
    app.run(port=5000, host='127.0.0.1')
