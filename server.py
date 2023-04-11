import random
from flask import Flask, render_template, redirect, request, abort
from flask_login import login_required, login_user, logout_user, LoginManager, current_user

from data.db import db_session
from data.db.__all_models import User, Genre, Book
from forms.user_form import UserForm
from forms.login import LoginForm
from forms.book_form import BookForm

db_session.global_init("data/db/db_files/explorer.sqlite")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
login_manager = LoginManager()
login_manager.init_app(app)

db_sess = db_session.create_session()


# for i in ['Фэнтези', 'Фантастика', 'Детектив', 'Романтика', 'Наука', 'Психология']:
#     db_sess = db_session.create_session()
#     genre = Genre(i)
#     db_sess.add(genre)
#     db_sess.commit()

def get_books(range_books=db_sess.query(Book).all()):
    books = []
    for book in range_books:
        temp_dictionary = dict()
        temp_dictionary['id'] = book.id
        temp_dictionary['title'] = book.title
        temp_dictionary['genre'] = book.genre.name
        temp_dictionary['brief_retelling'] = book.brief_retelling
        temp_dictionary['feedback'] = book.feedback
        temp_dictionary['author'] = str(book.user.surname) + ' ' + str(book.user.name)
        temp_dictionary['is_favorite'] = current_user.favorites and str(book.id) in current_user.favorites.split()

        books.append(temp_dictionary)

    return books


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(f'/profile/{current_user.surname}_{current_user.name}')
    else:
        return render_template('base.html', title='Книжное Мировоззрение')


@app.route('/profile/<username>')
def profile(username):
    surname, name = username.split('_')
    user_profile = db_sess.query(User).filter(User.surname == surname, User.name == name)[0]
    like_genres = []
    like_genres_user = list(map(int, user_profile.like_genres_of_books.split(', ')))
    for genre in db_sess.query(Genre).filter(Genre.id.in_(like_genres_user)):
        like_genres.append(genre.name)

    if current_user.friends and str(user_profile.id) in current_user.friends.split() and \
            user_profile.id != current_user.id:
        is_friend = True
    else:
        is_friend = False

    return render_template('profile.html', like_genres=', '.join(like_genres), user=user_profile,
                           title='Профиль читателя', is_friend=is_friend)


@app.route('/registration_account', methods=['GET', 'POST'])
def registration_account():
    form = UserForm('Зарегистрировать')
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration_account.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
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

        db_sess.commit()

        message = 'Сохранено'
        login_user(user, remember=True)

    elif request.method == "GET":
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        form.age.data = current_user.age
    return render_template('edit_account.html', form=form, message=message, title='Редактирование профиля')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route(f'/library/<username>')
def library(username):
    surname, name = username.split('_')
    user = db_sess.query(User).filter(User.surname == surname, User.name == name)[0]

    books = get_books(db_sess.query(Book).filter(Book.user_id == user.id))

    return render_template('library.html', books=books, user=user, title=f'Библиотека читателя {username}')


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
        return redirect(f'/my_library/{current_user.surname}_{current_user.name}')
    return render_template('book.html', form=form, title='Добавление книги')


@app.route('/book/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    form = BookForm('Сохранить')
    if request.method == "GET":
        book = db_sess.query(Book).filter(Book.id == id).first()
        if book:
            form.title.data = book.title
            form.genre.data = book.genre.name
            form.brief_retelling.data = book.brief_retelling
            form.feedback.data = book.feedback
        else:
            abort(404)
    if form.validate_on_submit():
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
    return render_template('book.html', form=form, title='Изменение книги')


@app.route('/book_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def book_delete(id):
    book = db_sess.query(Book).filter(Book.id == id, Book.user_id == current_user.id).first()
    if book:
        db_sess.delete(book)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/my_library/{current_user.surname}_{current_user.name}')


@app.route('/random_books')
def random_books():
    books = get_books(db_sess.query(Book).all()[:50])
    random.shuffle(books)
    return render_template('random_books.html', title='Случайные книги', books=books)


@app.route('/add_friend')
@login_required
def add_friend():
    friend_id = request.args.get('friend_id')

    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.friends += ' ' + str(friend_id)

    db_sess.commit()
    login_user(user, remember=True)

    friend = db_sess.query(User).filter(User.id == friend_id).first()

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

    return redirect(f'/friends/{user.surname}_{user.name}')


@app.route('/add_favorite_book')
@login_required
def add_favorite_book():
    book_id = request.args.get('book_id')
    page = request.args.get('page')
    user_id = request.args.get('user_id')

    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.favorites += ' ' + str(book_id)

    db_sess.commit()
    login_user(user, remember=True)
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
    friends = []
    try:
        for friend in db_sess.query(User).filter(User.id.in_(user.friends.split())):
            temp_dictionary = dict()
            temp_dictionary['id'] = friend.id
            temp_dictionary['surname'] = friend.surname
            temp_dictionary['name'] = friend.name
            temp_dictionary['age'] = friend.age
            temp_dictionary['email'] = friend.email

            like_genres = []
            like_genres_user = list(map(int, friend.like_genres_of_books.split(', ')))
            for genre in db_sess.query(Genre).filter(Genre.id.in_(like_genres_user)):
                like_genres.append(genre.name)
            temp_dictionary['like_genres'] = like_genres
            friends.append(temp_dictionary)
        return render_template('friends.html', title=f'Друзья читателя {surname} {name}', friends=friends)
    except AttributeError:
        return render_template('friends.html', title=f'Друзья читателя {surname} {name}', friends=[])


@app.route('/favorites')
@login_required
def favorites():
    books = get_books(db_sess.query(Book).filter(Book.id.in_(current_user.favorites.split())))
    return render_template('favorites.html', books=books)


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
