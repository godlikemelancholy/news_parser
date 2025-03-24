import psycopg2
from aiogram.types import Message
from datetime import datetime, timedelta
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

    def reg_user(self, message: Message):
        user_id = message.from_user.id
        username = message.from_user.username
        default_source = None
        news_limit = 0

        with self.__conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (user_id, username, default_source, news_limit) VALUES (%s, %s, %s, %s) ON CONFLICT (user_id) DO NOTHING",
                (user_id, f"@{username}", default_source, news_limit)
            )
            self.__conn.commit()

    def check_user(self, user_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE user_id = %s", (user_id,))
            check = cursor.fetchone()
            return check[0] if check else False

    def get_default_source(self, user_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT default_source FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_user_subscriptions(self, user_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("""
                SELECT sources.id, sources.name 
                FROM subscriptions
                JOIN sources ON subscriptions.source_id = sources.id
                WHERE subscriptions.user_id = %s
            """, (user_id,))
            return cursor.fetchall()

    def is_subscribed(self, user_id, source_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM subscriptions WHERE user_id = %s AND source_id = %s", (user_id, source_id))
            return cursor.fetchone() is not None

    def add_subscription(self, user_id, source_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("INSERT INTO subscriptions (user_id, source_id) VALUES (%s, %s)", (user_id, source_id))
            self.__conn.commit()

    def subscribe(self, user_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("UPDATE users SET is_subscribed = TRUE WHERE user_id = %s", (user_id,))
            self.__conn.commit()

    def unsubscribe(self, user_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("UPDATE users SET is_subscribed = FALSE WHERE user_id = %s", (user_id,))
            self.__conn.commit()

    def is_user_subscribed(self, user_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT is_subscribed FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else False

    def remove_subscription(self, user_id, source_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("DELETE FROM subscriptions WHERE user_id = %s AND source_id = %s", (user_id, source_id))
            self.__conn.commit()

    def change_default_source(self, source, user_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("UPDATE users SET default_source = %s WHERE user_id = %s", (source, user_id))
            self.__conn.commit()

    def reset_default_source(self, user_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("UPDATE users SET default_source = NULL WHERE user_id = %s", (user_id,))
            self.__conn.commit()

    def change_news_limit(self, user_id, news_limit):
        with self.__conn.cursor() as cursor:
            cursor.execute("UPDATE users SET news_limit = %s WHERE user_id = %s", (news_limit, user_id))
            self.__conn.commit()

    def get_all_sources(self):
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sources")
            return cursor.fetchall()

    def get_news(self, user_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT news_limit, default_source FROM users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()

            if not user_data:
                return []

            news_limit, default_source = user_data

            if default_source:
                cursor.execute("SELECT id FROM sources WHERE name ILIKE %s", (default_source,))
                source_id = cursor.fetchone()

                if not source_id:
                    return []

                source_id = source_id[0]

                cursor.execute("""
                    SELECT news.title, news.link, news.published_at, sources.name
                    FROM news
                    JOIN sources ON news.source = sources.id
                    WHERE news.source = %s
                    ORDER BY news.published_at DESC
                    LIMIT %s
                """, (source_id, news_limit))

                return cursor.fetchall()

            cursor.execute("""
                SELECT news.title, news.link, news.published_at, sources.name
                FROM news
                JOIN sources ON news.source = sources.id
                ORDER BY news.published_at DESC
            """)
            return cursor.fetchall()

    def get_news_by_target(self, source_name):
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT id FROM sources WHERE name ILIKE %s", (source_name,))
            source_id = cursor.fetchone()

            if not source_id:
                return []

            source_id = source_id[0]

            cursor.execute("""
                SELECT news.title, news.link, news.published_at, sources.name
                FROM news
                JOIN sources ON news.source = sources.id
                WHERE news.source = %s
                ORDER BY news.published_at DESC
                LIMIT 10
            """, (source_id,))

            return cursor.fetchall()

    def delete_old_news(self):
        threshold = datetime.now() - timedelta(hours=1)
        with self.__conn.cursor() as cursor:
            cursor.execute("DELETE FROM news WHERE published_at < %s", (threshold,))
            self.__conn.commit()

    def get_subscribed_users(self):
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE is_subscribed = TRUE")
            return [row[0] for row in cursor.fetchall()]

    def get_unsent_news_for_user(self, user_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("""
                SELECT n.id, n.title, n.link, s.name 
                FROM news n
                JOIN sources s ON n.source = s.id
                WHERE NOT EXISTS (
                    SELECT 1 FROM news_sent ns WHERE ns.user_id = %s AND ns.news_id = n.id
                )
                ORDER BY n.published_at DESC
            """, (user_id,))
            return cursor.fetchall()

    def mark_news_as_sent_for_user(self, user_id, news_id):
        with self.__conn.cursor() as cursor:
            cursor.execute("INSERT INTO news_sent (user_id, news_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                           (user_id, news_id))
            self.__conn.commit()