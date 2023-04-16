import random
import os
from flask import Flask, render_template, redirect, request, abort, url_for
from flask_login import login_required, login_user, logout_user, LoginManager, current_user
from flask_restful import Api

from data.db import db_session
from data.db.__all_models import User, Genre, Book
from forms.user_form import UserForm
from forms.login_form import LoginForm
from forms.book_form import BookForm
from forms.seacrh_form import SearchForm
from data.resources import genres_resources, users_resources, books_resources

db_session.global_init("data/db/db_files/explorer.sqlite")
db_sess = db_session.create_session()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)

api.add_resource(users_resources.UsersListResource, '/api/v2/users')
api.add_resource(users_resources.UserResource, '/api/v2/users/<int:user_id>')

api.add_resource(books_resources.BooksListResource, '/api/v2/books')
api.add_resource(books_resources.BookResource, '/api/v2/books/<int:book_id>')

api.add_resource(genres_resources.GenresListResource, '/api/v2/genres')
api.add_resource(genres_resources.GenreResource, '/api/v2/genres/<int:genre_id>')


def get_books(range_books=db_sess.query(Book).all()):
    books = []
    for book in range_books:
        temp_dictionary = dict()
        temp_dictionary['id'] = book.id
        temp_dictionary['title'] = book.title
        temp_dictionary['genre'] = book.genre.name
        temp_dictionary['brief_retelling'] = book.brief_retelling
        temp_dictionary['feedback'] = book.feedback
        temp_dictionary['author'] = book.user.surname + ' ' + book.user.name if book.user_id != -1 else \
            'Удалённый Пользователь'
        temp_dictionary['is_favorite'] = current_user.favorites and str(book.id) in current_user.favorites.split()

        books.append(temp_dictionary)

    return books


def get_users(range_users=db_sess.query(User).all()):
    users = []
    for user in range_users:
        temp_dictionary = dict()
        temp_dictionary['id'] = user.id
        temp_dictionary['surname'] = user.surname
        temp_dictionary['name'] = user.name
        temp_dictionary['age'] = user.age
        temp_dictionary['email'] = user.email

        temp_dictionary['like_genres'] = get_genres(db_sess.query(Genre).filter(Genre.id.in_(user.like_genres.split())))

        temp_dictionary['is_friend'] = (current_user.friends and str(user.id) in current_user.friends.split() and
                                        user.id != current_user.id)

        users.append(temp_dictionary)

    return users


def get_genres(range_genres=db_sess.query(Genre).all(), get_name=True, get_id=False):
    genres = []
    for genre in range_genres:
        if get_name and get_id:
            genres.append((genre.id, genre.name))
        elif get_name:
            genres.append(genre.name)
        else:
            genres.append(genre.id)
    return genres


@app.errorhandler(401)
def unauthorized(error):
    return render_template('welcome.html', title='Добро Пожаловать в Книжное Мировоззрение')


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(f'/profile/{current_user.surname}_{current_user.name}')
    else:
        return render_template('welcome.html', title='Добро Пожаловать в Книжное Мировоззрение')


@app.route('/profile/<username>')
@login_required
def profile(username):
    surname, name = username.split('_')
    user_profile = get_users([db_sess.query(User).filter(User.surname == surname, User.name == name).first()])[0]
    if os.access(f'static/image/users_icon/{user_profile["id"]}_{user_profile["surname"]}_{user_profile["name"]}.png',
                 os.F_OK):
        filename_image = f'image/users_icon/{user_profile["id"]}_{user_profile["surname"]}_{user_profile["name"]}.png'
    else:
        filename_image = 'image/users_icon/default.jpg'

    image = url_for('static', filename=filename_image)
    user_profile['like_genres'] = ', '.join(user_profile['like_genres'])

    return render_template('profile.html', user=user_profile, title='Профиль читателя', image=image)


@app.route('/registration_account', methods=['GET', 'POST'])
def registration_account():
    form = UserForm('Зарегистрировать')
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration_account.html', title='Регистрация',
                                   form=form, message="Пароли не совпадают")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration_account.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        like_genres = list(
            map(str, get_genres(db_sess.query(Genre).filter(Genre.name.in_(form.like_genres.data)), False, True)))

        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            age=form.age.data,
            like_genres=' '.join(like_genres)
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        if form.file.data:
            form.file.data.save('static/image/users_icon/' + f'{user.id}_{user.surname}_{user.name}.png')

        login_user(user, remember=True)
        return redirect(f'/profile/{form.surname.data}_{form.name.data}')
    return render_template('registration_account.html', form=form, title='Регистрация читателя')


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/login_account', methods=['GET', 'POST'])
def login_account():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login_account.html', message="Неправильный логин или пароль", form=form,
                               title='Авторизация читателя')
    return render_template('login_account.html', form=form, title='Авторизация читателя')


@app.route('/edit_account', methods=['GET', 'POST'])
@login_required
def edit_account():
    form = UserForm('Сохранить')
    message = ''
    form.password.data = form.password_again.data = '1'
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.age = form.age.data

        like_genres = list(
            map(str, get_genres(db_sess.query(Genre).filter(Genre.name.in_(form.like_genres.data)), False, True)))

        user.like_genres = ' '.join(like_genres)

        db_sess.commit()

        if form.file.data:
            form.file.data.save('static/image/users_icon/' + f'{user.id}_{user.surname}_{user.name}.png')

        message = 'Сохранено'
        login_user(user, remember=True)

    elif request.method == "GET":
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        form.age.data = current_user.age

        form.like_genres.data = get_genres(db_sess.query(Genre).filter(Genre.id.in_(current_user.like_genres.split())))
    return render_template('edit_account.html', form=form, message=message, title='Редактирование профиля')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route(f'/library/<username>')
@login_required
def library(username):
    surname, name = username.split('_')
    user = db_sess.query(User).filter(User.surname == surname, User.name == name).first()

    books = get_books(db_sess.query(Book).filter(Book.user_id == user.id))

    return render_template('library.html', books=books, user=user, title=f'Библиотека читателя {surname} {name}')


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm('Добавить')
    if form.validate_on_submit():
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
        return redirect(f'/library/{current_user.surname}_{current_user.name}')
    return render_template('book.html', form=form, title='Добавление книги')


@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    form = BookForm('Сохранить')
    if request.method == "GET":
        book = db_sess.query(Book).filter(Book.id == book_id).first()
        if book:
            form.title.data = book.title
            form.genre.data = book.genre.name
            form.brief_retelling.data = book.brief_retelling
            form.feedback.data = book.feedback
        else:
            abort(404)
    if form.validate_on_submit():
        book = db_sess.query(Book).filter(Book.id == book_id, ).first()
        if book:
            book.title = form.title.data
            book.genre.name = form.genre.data
            book.brief_retelling = form.brief_retelling.data
            book.feedback = form.feedback.data
            db_sess.commit()
            return redirect(f'/library/{current_user.surname}_{current_user.name}')
        else:
            abort(404)
    return render_template('book.html', form=form, title='Изменение книги')


@app.route('/book_delete/<int:book_id>', methods=['GET', 'POST'])
@login_required
def book_delete(book_id):
    book = db_sess.query(Book).filter(Book.id == book_id, Book.user_id == current_user.id).first()
    if book:
        for user in db_sess.query(User).filter(User.favorites.like(f'%{book_id}%')):
            favorites_group = user.favorites.split()
            del favorites_group[favorites_group.index(str(book_id))]
            user.favorites = ' '.join(favorites_group)
        db_sess.delete(book)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/library/{current_user.surname}_{current_user.name}')


@app.route('/random_books')
@login_required
def random_books():
    books = get_books(db_sess.query(Book).all())
    random.shuffle(books)
    return render_template('random_books.html', title='Случайные книги', books=books[:50])


@app.route('/add_friend')
@login_required
def add_friend():
    friend_id = request.args.get('friend_id')
    page = request.args.get('page')

    current_user.add_friend(friend_id)

    db_sess.commit()

    friend = db_sess.query(User).filter(User.id == friend_id).first()

    if page == 'search':
        return redirect('/search')

    return redirect(f'/profile/{friend.surname}_{friend.name}')


@app.route('/del_friend')
@login_required
def del_friend():
    friend_id = request.args.get('friend_id')
    page = request.args.get('page')

    user = db_sess.query(User).filter(User.id == current_user.id).first()

    friends_group = user.friends.split()
    del friends_group[friends_group.index(str(friend_id))]
    user.friends = ' '.join(friends_group)

    db_sess.commit()
    login_user(user, remember=True)

    if page == 'profile':
        friend = db_sess.query(User).filter(User.id == friend_id).first()
        return redirect(f'/profile/{friend.surname}_{friend.name}')
    elif page == 'search':
        return redirect('/search')

    return redirect(f'/friends/{user.surname}_{user.name}')


@app.route('/add_favorite_book')
@login_required
def add_favorite_book():
    book_id = request.args.get('book_id')
    page = request.args.get('page')
    user_id = request.args.get('user_id')

    current_user.favorites += ' ' + str(book_id)

    db_sess.commit()

    if page == 'library':
        friend = db_sess.query(User).filter(User.id == user_id).first()
        return redirect(f'/{page}/{friend.surname}_{friend.name}')

    return redirect(f'/{page}')


@app.route('/del_favorite_book')
@login_required
def del_favorite_book():
    book_id = request.args.get('book_id')
    page = request.args.get('page')
    user_id = request.args.get('user_id')

    user = db_sess.query(User).filter(User.id == current_user.id).first()

    favorites_books_group = user.favorites.split()
    del favorites_books_group[favorites_books_group.index(str(book_id))]
    user.favorites = ' '.join(favorites_books_group)

    db_sess.commit()
    login_user(user, remember=True)

    if page == 'library':
        if int(user_id) != int(current_user.id):
            user = db_sess.query(User).filter(User.id == user_id).first()

        return redirect(f'/{page}/{user.surname}_{user.name}')

    return redirect(f'/{page}')


@app.route('/friends/<username>')
@login_required
def friends(username):
    surname, name = username.split('_')

    user = db_sess.query(User).filter(User.surname == surname, User.name == name).first()

    try:
        friends_list = get_users(db_sess.query(User).filter(User.id.in_(user.friends.split())))
        return render_template('friends.html', title=f'Друзья читателя {surname} {name}', friends=friends_list)
    except AttributeError:
        return render_template('friends.html', title=f'Друзья читателя {surname} {name}', friends=[])


@app.route('/favorites')
@login_required
def favorites():
    books = get_books(db_sess.query(Book).filter(Book.id.in_(current_user.favorites.split())))
    return render_template('favorites.html', books=books, title='Избранное')


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    results = []
    message = ''
    people_or_books = None
    if form.validate_on_submit() and form.user_text.data:
        if form.people_or_books.data == 'Человека':
            people_or_books = 'Человек'
            for text in form.user_text.data.split():
                text = f'%{text}%'
                results.extend([i for i in db_sess.query(User).filter(User.surname.like(text) | User.name.like(text))])
            results = get_users(results)
        elif form.people_or_books.data == 'Книгу':
            people_or_books = 'Книга'
            for text in form.user_text.data.split():
                text = f'%{text}%'
                results.extend([i for i in db_sess.query(Book).filter(Book.title.like(text))])
            results = get_books(results)
        if not results:
            message = 'К сожалению, поиск не дал результатов'

    return render_template('search.html', title='Поисковик', form=form, results=results, message=message,
                           people_or_books=people_or_books)


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
