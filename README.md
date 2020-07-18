# PinnacleParser
Тестовое задание к собеседованию.

## Стэк реализации
- Python 3.8.2 + virtualenv
- PostgreSQL + SQLAlchemy ORM
- requests

## Запуск
Для запуска парсера (если потребуется): 
1. Клонируете репозиторий 
2. Активируете env\Scripts\activate.bat (но на всякий случай в корне репозитория лежат requirements.txt)
3. Редактируйте под себя ***database.py***:
  Строку 
  ```
  engine = create_engine("postgresql+psycopg2://testDatabaseUser:ce*O[]~8d7qewqL!N@localhost/testDatabase")
  ```
  под следующий формат:
  ```
  engine = create_engine("postgresql+<коннектор>://<имя пользователя БД>:<пароль>@<хост>/<имя созданной на хосте БД>")
  ```
4. Запускайте
```
python parser.py
```