from flask import Flask, request, jsonify, send_file
import sqlite3
import flask
import sqlalchemy as sqlalchemy
from flask import Flask, render_template, send_file, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user, logout_user, login_required
from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init("db/blogs.db")
login_manager = LoginManager()
login_manager.init_app(app)

data = {}
info = {}
id_counter = 1
now_working = []
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()


def save(file, id):
    name = f"{id}.png"
    k = id
    now_working.append(k)
    file.save(name)
    now_working.remove(k)


@app.route('/check_connection', methods=['GET'])
def check_connection():
    return jsonify({"message": "True"})


@app.route('/api', methods=['GET'])
def api():
    global id_counter
    if 'id' in request.args:
        if request.args['id'] == '0':
            # регистрируем пользователя
            new_id = id_counter
            id_counter += 1
            data[new_id] = [{}]
            info[new_id] = {}
            info[new_id]["os"] = request.args['os']
            data[new_id][0]["coords"] = (100, 100)
            data[new_id][0]["is_clicked"] = False
            data[new_id][0]["data"] = []
            data[new_id][0]["display"] = [1920, 1080]
            returned = {"message": "ID", 'id': new_id}
            return jsonify(returned)
    elif 'get_for_id' in request.args and request.args['get_for_id'].isdigit() and int(request.args['get_for_id']) > 0:
        # запрос на передвижение и клики
        returned = data[int(request.args['get_for_id'])].copy()
        data[int(request.args['get_for_id'])] = []
        return jsonify(returned)
    elif "get_image" in request.args:
        with open(f'{request.args["get_image"]}.png', 'rb') as f:
            img_data = f.read().decode('utf-8')
        returned = {'message': 'Returned', 'img': img_data}
        return jsonify(returned)
    returned = {'message': 'Invalid request'}
    return jsonify(returned)


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    name = file.filename
    download_id = request.args["id"]
    while download_id in now_working:
        pass
    save(file, download_id)
    return 'Файл успешно загружен'


@app.route('/test', methods=['POST'])
def test():
    args = request.get_json()
    return jsonify(args)


@app.route('/moving', methods=['POST'])
def moving():
    # сохраняем передвижение и клики мыши
    args = request.get_json(force=True)
    coords = args["coords"]
    is_clicked = bool(int(args["is_clicked"]))
    data_about_buttons = args["data"]
    display = args["display"]
    now = {}
    now["coords"] = coords
    now["is_clicked"] = is_clicked
    now["data"] = data_about_buttons
    now["display"] = display
    data[int(args['id'])].append(now)
    returned = {'message': 'Saved', "data": data[int(args['id'])][-1]}
    return jsonify(returned)


@app.route('/download')
def download_file():
    path = f'../{request.args["id"]}.png'
    download_id = request.args["id"]
    while download_id in now_working:
        pass
    now_working.append(download_id)
    file = send_file(path, as_attachment=True)
    now_working.remove(download_id)
    return file


@app.route('/get_data', methods=['GET'])
def get_data():
    returned = {}
    for e in info.keys():
        print(e)
        returned[int(e)] = info[e]["os"]
    return jsonify(returned)


@app.route("/check_login", methods=["GET"])
def check_login():
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (request.args["username"], request.args["password"]))
    if c.fetchone() is not None:
        return jsonify({"res": True})
    else:
        return jsonify({"res": False})


# __________________________________


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

db = SQLAlchemy(app)


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    email = EmailField('Эл. почта', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/download_main')
def download_main():
    path = '../main.py'
    return send_file(path, as_attachment=True)


@app.route('/download_server')
def download_server():
    path = 'server.py'
    return send_file(path, as_attachment=True)


@app.route('/download_receiving')
def download_receiving():
    path = '../receiving.zip'
    return send_file(path, as_attachment=True)


@app.route('/instruction')
def download_instruction():
    instr = """<body>
<p><pre>
╻                                                                                   ╻<br>
┃                           Hello. You use RemoteOS.                                ┃<br>
┃                                                                                   ┃<br>
┃┅ If you are developer, use <a href="https://github.com/in179/project_web/blob/master/server/server.py">server/server.py</a> for starting server.                  ┃<br>
┃┅ If you want to help us and provide us your computer, use                         ┃<br>
┃    <a href="https://github.com/in179/project_web/blob/master/receiving/client_receiving.py">receiving/client_receiving.py</a> for receive your os (also download <a href="https://github.com/in179/project_web/blob/master/receiving/cursor.png">cursor image</a>).┃<br>
┃┅ If you is user and you want to try our product - register                        ┃<br>
┃    in our <a href="https://dsfsdfdsf.pythonanywhere.com/">website</a>.                                                                ┃<br>
┃    and start <a href="https://github.com/in179/project_web/blob/master/main/client_main.py">main/client_main</a> to use project.                                     ┃<br>
┃                                                                                   ┃<br>
┃                             Thanks for reading!                                   ┃<br>
┃                                                                 GitHub - <a href="https://github.com/in179/project_web/tree/master/">Remote OS</a>┃
</p></pre>
</body>
"""
    return instr


@app.route('/profile/<username>')
def profile(username):
    return f"Пользователь: {username}"


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.username.data).first()
        if user and user.hashed_password == form.password.data:
            login_user(user, remember=form.remember_me.data)
            return redirect("/successlog")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        user = User()
        user.name = form.username.data
        user.hashed_password = form.password.data
        user.email = form.email.data
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=form.remember_me.data)
        return redirect('/successreg')

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/successreg')
def success():
    return render_template('successreg.html')


@app.route('/successlog')
def successlog():
    return render_template('successlog.html')


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(host='127.0.0.1', port=8080, debug=True)

#_____________________________________


if __name__ == '__main__':
    print("Starting server")
    app.run(debug=True)
