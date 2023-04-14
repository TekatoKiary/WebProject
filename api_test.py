from requests import get, post, delete

print(get('http://localhost:8080/api/v2/users').json())
print(get('http://localhost:8080/api/v2/users/1').json())
print(get('http://localhost:8080/api/v2/users/1000').json())
print()

print(get('http://localhost:8080/api/v2/books').json())
print(get('http://localhost:8080/api/v2/books/1').json())
print(get('http://localhost:8080/api/v2/books/1000').json())
print()

print(get('http://localhost:8080/api/v2/genres').json())
print(get('http://localhost:8080/api/v2/genres/1').json())
print(get('http://localhost:8080/api/v2/genres/1000').json())
print()

print(post('http://localhost:8080/api/v2/users',
           json={'surname': 'Api',
                 'name': 'Blueprint',
                 'age': 50,
                 'email': 'api@mail.ru',
                 'hashed_password': '44',
                 'like_genres_of_books': '1, 2'}).json())

print(post('http://localhost:8080/api/v2/users',
           json={'surname': 'Api',
                 'name': 'Blueprint',
                 'email': 'api@mail.ru',
                 'like_genres_of_books': '1, 2'}).json())  # Ошибка: не указан age

print(post('http://localhost:8080/api/v2/users',
           json={}).json())  # Ошибка: отправлен пустой json
print(delete('http://localhost:8080/api/v2/users/7').json())  # id написан на момент первых проверок разработчика
print()

print(post('http://localhost:8080/api/v2/books',
           json={'title': 'Api',
                 'user_id': 6,
                 'genre_id': 1,
                 'brief_retelling': 'Api is so cool',
                 'feedback': 'But do it so long'}).json())

print(post('http://localhost:8080/api/v2/books',
           json={'title': 'Api',
                 'genre_id': 1,
                 'brief_retelling': 'Api is so cool',
                 'feedback': 'But do it so long'}).json())  # Ошибка: не указан user_id

print(post('http://localhost:8080/api/v2/books',
           json={}).json())  # Ошибка: отправлен пустой json

print(delete('http://localhost:8080/api/v2/books/5').json())  # id написан на момент первых проверок разработчика
print()

print(post('http://localhost:8080/api/v2/genres',
           json={'name': 'Драма'}).json())

print(post('http://localhost:8080/api/v2/genres',
           json={}).json())  # Ошибка: отправлен пустой json

print(delete('http://localhost:8080/api/v2/genres/8').json())  # id написан на момент первых проверок разработчика
print()
