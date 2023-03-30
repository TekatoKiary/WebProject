import datetime
import os
from flask import Flask, render_template, redirect, request, abort
from flask_login import login_required, login_user, logout_user, LoginManager, current_user

from data.db import db_session
from data.db.__all_models import User, Genre, Book
from forms.registration_user import UserRegisterForm
from forms.login import LoginForm
from forms.add_book import BookForm

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
    if current_user.is_authenticated:
        return redirect(f'/profile/{current_user.surname}_{current_user.name}')
    else:
        return render_template('base')


@app.route('/profile/<username>')
def profile(username):
    username = username.split('_')
    db_sess = db_session.create_session()
    user_profile = db_sess.query(User).filter(User.surname == username[0], User.name == username[1])[0]
    like_genres = []
    like_genres_user = list(map(int, user_profile.like_genres_of_books.split(', ')))
    for genre in db_sess.query(Genre).filter(Genre.id.in_(like_genres_user)):
        like_genres.append(genre.name)
    return render_template('profile.html', like_genres=', '.join(like_genres), user=user_profile)


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
        return redirect('/profile/{current_user.surname}_{current_user.name}')
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


@app.route(f'/my_library/<username>', methods=['GET', 'POST'])
def my_library(username):
    username = username.split('_')
    if request.method == 'POST':
        print(request.form['users_comment'])
    db_sess = db_session.create_session()
    books = []
    user = db_sess.query(User).filter(User.surname == username[0], User.name == username[1])[0]
    for book in db_sess.query(Book).filter(Book.user_id == user.id):
        temp_dictionary = dict()
        temp_dictionary['id'] = book.id
        temp_dictionary['title'] = book.title
        temp_dictionary['genre'] = book.genre.name
        temp_dictionary['brief_retelling'] = book.brief_retelling
        temp_dictionary['feedback'] = book.feedback
        temp_dictionary['author'] = str(book.user.surname) + ' ' + str(book.user.name)
        temp_dictionary['comments'] = [
            {'name_user': 'Tom Taylor', 'datetime_creation': datetime.datetime.now(),
             'content': 'That\'s the cool fairy tale'}]
        books.append(temp_dictionary)
    return render_template('my_library.html', books=books, user=user)


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        genre_id = db_sess.query(Genre).filter(form.genre.data == Genre.name)[0].id
        book = Book(
            user_id=current_user.id,
            title=form.title.data,
            genre_id=genre_id,
            brief_retelling=form.brief_retelling.data,
            feedback=form.feedback.data
        )
        db_sess.add(book)
        db_sess.commit()
        return redirect(f'/my_library/{current_user.surname}_{current_user.name}')
    return render_template('book.html', form=form)


@app.route('/book/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    form = BookForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        book = db_sess.query(Book).filter(Book.id == id).first()
        if book:
            form.title.data = book.title
            form.genre.data = book.genre.name
            form.brief_retelling.data = book.brief_retelling
            form.feedback.data = book.feedback
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        book = db_sess.query(Book).filter(Book.id == id, ).first()
        if book:
            book.title = form.title.data
            book.genre.name = form.genre.data
            book.brief_retelling = form.brief_retelling.data
            book.feedback = form.feedback.data
            db_sess.commit()
            return redirect(f'/my_library/{current_user.surname}_{current_user.name}')
        else:
            abort(404)
    return render_template('book.html', form=form)


@app.route('/book_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def book_delete(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id, Book.user_id == current_user.id).first()
    print(id)
    if book:
        db_sess.delete(book)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/my_library/{current_user.surname}_{current_user.name}')


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
