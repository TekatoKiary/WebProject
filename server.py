import os
from flask import Flask, render_template, redirect
from flask_login import login_required, login_user, logout_user, LoginManager

from data.db import db_session
from data.db.__all_models import User
from forms.registration_user import UserRegisterForm
from forms.login import LoginForm

db_session.global_init("data/db/db_files/explorer.sqlite")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    return redirect('/profile')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/registration_account', methods=['GET', 'POST'])
def registration_account():
    form = UserRegisterForm()
    if form.validate_on_submit():
        print(form.like_genres_of_books.data, type(form.like_genres_of_books.data))
        if form.password.data != form.password_again.data:
            return render_template('registration_account.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration_account.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            age=form.age.data,
            like_genres_of_books=', '.join(form.like_genres_of_books.data)
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/profile')
    return render_template('registration_account.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login_account', methods=['GET', 'POST'])
def login_account():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login_account.html', message="Неправильный логин или пароль", form=form)
    return render_template('login_account.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
