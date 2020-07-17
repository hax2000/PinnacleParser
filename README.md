# PinnacleParser
Тестовое задание к собеседованию.

## Стэк реализации
- Python 3.8.2 + virtualenv
- PostgreSQL + SQLAlchemy ORM
- Selenium (Chrome) + BeautifulSoup

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
python parse.py
```

## Пояснения к комментариям

### Страница с турнирами
![alt text](https://github.com/hax2000/PinnacleParser/blob/master/docPics/1.png?raw=true)

### Блок с заголовком турнира
![alt text](https://github.com/hax2000/PinnacleParser/blob/master/docPics/2.png?raw=true)

### Блок с матчем
![alt text](https://github.com/hax2000/PinnacleParser/blob/master/docPics/3.png?raw=true)

### Страница с полной инфой о матче
![alt text](https://github.com/hax2000/PinnacleParser/blob/master/docPics/4.png?raw=true)

### Закрытые дропбоксы
![alt text](https://github.com/hax2000/PinnacleParser/blob/master/docPics/5.png?raw=true)

### Открытые дропбоксы
![alt text](https://github.com/hax2000/PinnacleParser/blob/master/docPics/6.png?raw=true)

### Показатель линии
![alt text](https://github.com/hax2000/PinnacleParser/blob/master/docPics/7.png?raw=true)

### Текст линии
![alt text](https://github.com/hax2000/PinnacleParser/blob/master/docPics/8.png?raw=true)

### Значение линии
![alt text](https://github.com/hax2000/PinnacleParser/blob/master/docPics/9.png?raw=true)

### Кнопка (блок) линии
![alt text](https://github.com/hax2000/PinnacleParser/blob/master/docPics/10.png?raw=true)
