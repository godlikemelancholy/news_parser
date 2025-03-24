import psycopg2
from config import db_host, db_pass, db_user, db_port, db_name


class DB:
    def __init__(self):
        self.__conn = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_pass,
            host=db_host,
            port=db_port
        )

    def __del__(self):
        if hasattr(self, "__conn") and self.__conn:
            self.__conn.close()

    def add_news(self, news, source_name):
        if self.__conn is None:
            raise Exception("Database connection is not established. Call connect() first.")

        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
            source_row = cursor.fetchone()

            if source_row is None:
                cursor.execute("INSERT INTO sources (name) VALUES (%s) RETURNING id", (source_name,))
                source_id = cursor.fetchone()[0]
                self.__conn.commit()
            else:
                source_id = source_row[0]

            for title, link, published_at in news:
                cursor.execute("SELECT id FROM news WHERE title = %s", (title,))
                if cursor.fetchone() is None:
                    cursor.execute(
                        """
                        INSERT INTO news (source, title, link, published_at) 
                        VALUES (%s, %s, %s, %s) 
                        ON CONFLICT (link) DO NOTHING
                        """,
                        (source_id, title, link, published_at)
                    )

            self.__conn.commit()