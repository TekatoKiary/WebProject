import datetime
import os
from flask import Flask, render_template, redirect, request
from flask_login import login_required, login_user, logout_user, LoginManager, current_user

from data.db import db_session
from data.db.__all_models import User, Genre, Book
from forms.registration_user import UserRegisterForm
from forms.login import LoginForm

db_session.global_init("data/db/db_files/explorer.sqlite")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
login_manager = LoginManager()
login_manager.init_app(app)


# for i in ['Фэнтези', 'Фантастика', 'Детектив', 'Романтика', 'Наука', 'Психология']:
#     db_sess = db_session.create_session()
#     genre = Genre(i)
#     db_sess.add(genre)
#     db_sess.commit()

@app.route('/')
def index():
    return redirect('/profile')


@app.route('/profile')
def profile():
    db_sess = db_session.create_session()
    like_genres = []
    if current_user.is_authenticated:
        like_genres_user = list(map(int, current_user.like_genres_of_books.split(', ')))
        for genre in db_sess.query(Genre).filter(Genre.id.in_(like_genres_user)):
            like_genres.append(genre.name)
    return render_template('profile.html', like_genres=', '.join(like_genres))


@app.route('/registration_account', methods=['GET', 'POST'])
def registration_account():
    form = UserRegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration_account.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration_account.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        like_genres = []
        for genre in db_sess.query(Genre).filter(Genre.genre_name.in_(form.like_genres_of_books.data)):
            like_genres.append(str(genre.id))
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            age=form.age.data,
            like_genres_of_books=', '.join(like_genres)
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=True)
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


@app.route(f'/my_library', methods=['GET', 'POST'])
# @login_required
def my_library():
    if request.method == 'POST':
        print(request.form['users_comment'])
    db_sess = db_session.create_session()
    books = []
    for book in db_sess.query(Book).filter(Book.user_id == current_user.id):
        temp_dictionary = dict()
        temp_dictionary['title'] = book.title
        temp_dictionary['genre'] = book.genre.name
        temp_dictionary['brief_retelling'] = book.brief_retelling
        temp_dictionary['feedback'] = book.feedback
        temp_dictionary['author'] = str(book.user.surname) +' '+ str(book.user.name)
        temp_dictionary['comments'] = [
            {'name_user': 'Tom Taylor', 'datetime_creation': datetime.datetime.now(),
             'content': 'That\'s the cool fairy tale'}]
        books.append(temp_dictionary)
    return render_template('my_library.html', books=books)


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
