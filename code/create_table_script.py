import psycopg2
import yaml


def get_configs() -> dict:
    with open('configs.yaml') as fh:
        result = yaml.load(fh, Loader=yaml.FullLoader)
    return result


def create_table(configs: dict):
    connection = cursor = None
    try:
        connection = psycopg2.connect(user=configs.get('user'),
                                      password=configs.get('password'),
                                      host=configs.get('host'),
                                      port=configs.get('port'),
                                      database=configs.get('database'))
        cursor = connection.cursor()

        query = """
        CREATE TABLE author(
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(100) UNIQUE NOT NULL
        );
        CREATE TABLE book(
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) UNIQUE NOT NULL,
            author_id INTEGER NOT NULL,
            page_count INTEGER NOT NULL,
            file_id VARCHAR(20) NOT NULL,
            released_year INT2 NOT NULL,
            date_create DATE NOT NULL DEFAULT CURRENT_DATE,
            FOREIGN KEY (author_id) REFERENCES author(id)
        );
        CREATE TABLE topic(
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL
        );
        CREATE TABLE topic_book(
            id SERIAL PRIMARY KEY,
            book_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            FOREIGN KEY(book_id) REFERENCES book(id),
            FOREIGN KEY(book_id) REFERENCES topic(id)
        );
        """

        cursor.execute(query)
        connection.commit()


    except Exception:
        print('Возникла ошибка')
    finally:
        if connection:
            connection.close()
            cursor.close()


if __name__ == "__main__":
    configs_data = get_configs()
    create_table(configs_data)