import psycopg2
import yaml


def get_configs() -> dict:
    with open('configs.yaml') as fh:
        result = yaml.load(fh, Loader=yaml.FullLoader)
    return result


def save_book(book_info: str):
    book_dict = yaml.load(book_info, Loader=yaml.FullLoader)
    book_dict["title"] = book_dict["file_name"].replace('.pdf', '')
    items = [item.strip() for item in book_dict['caption'].split(',')]
    book_dict["author"] = items[0]
    book_dict["released_year"] = int(items[-1])
    topics = items[1:-1]
    book_dict["author_id"] = get_or_create_author_id(book_dict["author"])
    book_id = get_and_create_book_id(book_dict)
    topic_id_list = get_and_create_topic_id_list(topics)
    create_topic_book_relation(book_id, topic_id_list)


def get_or_create_author_id(author: str) -> int:
    """
    Обращается к базе данных за id указанного автора
    Если такого нет, то создается новая запись
    Возвращает id автора
    """
    configs = get_configs()
    connection = psycopg2.connect(user=configs.get('user'),
                                  password=configs.get('password'),
                                  host=configs.get('host'),
                                  port=configs.get('port'),
                                  database=configs.get('database'))
    cursor = connection.cursor()

    get_query = f"""
        SELECT id, full_name
        FROM author
        WHERE full_name LIKE ('%{author}%')
    """
    cursor.execute(get_query)
    result = cursor.fetchone()

    if not result:
        create_query = f"""
            INSERT INTO author(full_name)
            VALUES('{author}')
            """
        cursor.execute(create_query)
        connection.commit()

        cursor.execute(get_query)
        result = cursor.fetchone()

    connection.close()
    cursor.close()
    return result[0]


def get_and_create_book_id(bt: dict) -> int:
    """
    Обращается к базе данных за id указанной книги
    Создается новая запись, не учитывается ошибка уникальности
    Возвращает id книги
    """
    configs = get_configs()
    connection = psycopg2.connect(user=configs.get('user'),
                                  password=configs.get('password'),
                                  host=configs.get('host'),
                                  port=configs.get('port'),
                                  database=configs.get('database'))
    cursor = connection.cursor()
    get_query = f"""
        SELECT id, title
        FROM book 
        WHERE title LIKE '%{bt.get("title")}%'
    """
    create_query = f"""
        INSERT INTO book(title, author_id, released_year, file_id)
        VALUES('{bt.get("title")}','{bt.get("author_id")}', '{bt.get("released_year")}', '{bt.get("file_id")}')
    """
    cursor.execute(create_query)
    connection.commit()

    cursor.execute(get_query)
    result = cursor.fetchone()

    connection.close()
    cursor.close()
    return result[0]


def get_and_create_topic_id_list(topics: list):
    """
    Обращается к базе данных за id указанных тем
    Если такой темы нет, то создается новая запись
    Возвращает список, содержащий id тем
    """
    configs = get_configs()
    connection = psycopg2.connect(user=configs.get('user'),
                                  password=configs.get('password'),
                                  host=configs.get('host'),
                                  port=configs.get('port'),
                                  database=configs.get('database'))
    cursor = connection.cursor()

    topic_id_list = []
    for topic in topics:
        create_query = f"""
        INSERT INTO topic(name)
        VALUES ('{topic}')
        """
        get_query = f"""
        SELECT id, name
        FROM topic
        WHERE name LIKE '{topic}'
        """

        cursor.execute(get_query)
        result = cursor.fetchone()
        if not result:
            cursor.execute(create_query)
            connection.commit()
            cursor.execute(get_query)
            result = cursor.fetchone()
        topic_id_list.append(result[0])

    connection.close()
    cursor.close()
    return topic_id_list


def create_topic_book_relation(book_id: int, topic_id_list: list) -> None:
    """
    Обращается к базе данных для создания связи между книгой и темами
    Ничего не возвращает
    """
    configs = get_configs()
    connection = psycopg2.connect(user=configs.get('user'),
                                  password=configs.get('password'),
                                  host=configs.get('host'),
                                  port=configs.get('port'),
                                  database=configs.get('database'))
    cursor = connection.cursor()
    for topic_id in topic_id_list:
        create_query = f"""
        INSERT INTO topic_book(book_id, topic_id)
        VALUES({book_id}, {topic_id})
        """
        cursor.execute(create_query)
        connection.commit()

    connection.close()
    cursor.close()


def get_file_id(book_id: int) -> tuple:
    configs = get_configs()
    connection = psycopg2.connect(user=configs.get('user'),
                                  password=configs.get('password'),
                                  host=configs.get('host'),
                                  port=configs.get('port'),
                                  database=configs.get('database'))
    cursor = connection.cursor()

    get_query = f"""
        SELECT file_id
        FROM book
        WHERE id = {book_id}
        """
    cursor.execute(get_query)
    result = cursor.fetchone()

    connection.close()
    cursor.close()
    return result


def find_book_in_db_by_title(text: str) -> list:
    configs = get_configs()
    connection = psycopg2.connect(user=configs.get('user'),
                                  password=configs.get('password'),
                                  host=configs.get('host'),
                                  port=configs.get('port'),
                                  database=configs.get('database'))
    cursor = connection.cursor()

    get_query = f"""
    SELECT title, id
    FROM book
    WHERE title ILIKE '%{text}%'
    """
    cursor.execute(get_query)
    result = cursor.fetchall()

    connection.close()
    cursor.close()
    return result


def find_book_in_db_by_author(text: str) -> list:
    configs = get_configs()
    connection = psycopg2.connect(user=configs.get('user'),
                                  password=configs.get('password'),
                                  host=configs.get('host'),
                                  port=configs.get('port'),
                                  database=configs.get('database'))
    cursor = connection.cursor()

    get_query = f"""
        SELECT book.title, book.id
        FROM book
        INNER JOIN author
        ON book.author_id = author.id
        WHERE author.full_name ILIKE '%{text}%'
        """
    cursor.execute(get_query)
    result = cursor.fetchall()

    connection.close()
    cursor.close()
    return result


def find_book_in_db_by_keywords(keywords: list) -> list:
    configs = get_configs()
    connection = psycopg2.connect(user=configs.get('user'),
                                  password=configs.get('password'),
                                  host=configs.get('host'),
                                  port=configs.get('port'),
                                  database=configs.get('database'))
    cursor = connection.cursor()

    topics = set()
    for key in keywords:
        check_query = f"""
            SELECT id
            FROM topic
            WHERE name ILIKE '%{key}%'
            """
        cursor.execute(check_query)
        try:
            topic_id = str(cursor.fetchone()[0])
        except TypeError:
            continue
        topics.add(topic_id)

    result = []
    if topics:
        get_query = f"""
        SELECT DISTINCT book.title, book.id
        FROM book
        INNER JOIN topic_book
        ON book.id = topic_book.book_id
        WHERE topic_book.topic_id IN ({', '.join(list(topics))}) 
        """

        cursor.execute(get_query)
        result = cursor.fetchall()

    connection.close()
    cursor.close()
    return result


def find_last_books() -> list:
    configs = get_configs()
    connection = psycopg2.connect(user=configs.get('user'),
                                  password=configs.get('password'),
                                  host=configs.get('host'),
                                  port=configs.get('port'),
                                  database=configs.get('database'))
    cursor = connection.cursor()

    get_query = f"""
        SELECT title, id
        FROM book
        ORDER BY date_create DESC
        LIMIT 10
        """
    cursor.execute(get_query)
    result = cursor.fetchall()

    connection.close()
    cursor.close()
    return result
