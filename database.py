import sqlite3
import logging
import os
from logging.handlers import RotatingFileHandler

BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH=os.path.join(BASE_DIRECTORY, 'Phone_book_database.db')
LOG_DIRECTORY = os.path.join(BASE_DIRECTORY, "logs")
LOG_FILE_PATH = os.path.join(LOG_DIRECTORY, "database.log")

os.makedirs(LOG_DIRECTORY, exist_ok=True)

logger= logging.getLogger(
    'database'
)
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        filename=LOG_FILE_PATH,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

logger.propagate = False

import sqlite3


class Database:
    def __init__(self, database_name="Phone_book_database.db"):
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT,
                phone_number TEXT NOT NULL,
                email TEXT,
                group_id INTEGER,
                FOREIGN KEY (group_id) REFERENCES groups(id)
            )
        """)

        self.connection.commit()

    def add_group(self, name):
        try:
            self.cursor.execute(
                """
                INSERT INTO groups (name)
                VALUES (?)
                """,
                (name,)
            )

            self.connection.commit()
            return self.cursor.lastrowid

        except sqlite3.IntegrityError:
            return None

    def get_groups(self):
        self.cursor.execute("""
            SELECT id, name
            FROM groups
            ORDER BY name
        """)

        return self.cursor.fetchall()

    def count_contacts(self, group_id):
        self.cursor.execute(
            """
            SELECT COUNT(*)
            FROM contacts
            WHERE group_id = ?
            """,
            (group_id,)
        )

        result = self.cursor.fetchone()

        return result[0]

    def delete_group(self, group_id):
        if self.count_contacts(group_id) > 0:
            return False

        self.cursor.execute(
            """
            DELETE FROM groups
            WHERE id = ?
            """,
            (group_id,)
        )

        self.connection.commit()

        return self.cursor.rowcount > 0

    def add_contact(
        self,
        first_name,
        last_name,
        phone_number,
        email,
        group_id
    ):
        self.cursor.execute(
            """
            INSERT INTO contacts (
                first_name,
                last_name,
                phone_number,
                email,
                group_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                first_name,
                last_name,
                phone_number,
                email,
                group_id
            )
        )

        self.connection.commit()

        return self.cursor.lastrowid

    def get_contacts(self, group_id=None):
        if group_id is None:
            self.cursor.execute("""
                SELECT
                    contacts.id,
                    contacts.first_name,
                    contacts.last_name,
                    contacts.phone_number,
                    contacts.email,
                    groups.name
                FROM contacts
                LEFT JOIN groups
                    ON contacts.group_id = groups.id
                ORDER BY contacts.first_name
            """)
        else:
            self.cursor.execute(
                """
                SELECT
                    contacts.id,
                    contacts.first_name,
                    contacts.last_name,
                    contacts.phone_number,
                    contacts.email,
                    groups.name
                FROM contacts
                LEFT JOIN groups
                    ON contacts.group_id = groups.id
                WHERE contacts.group_id = ?
                ORDER BY contacts.first_name
                """,
                (group_id,)
            )

        return self.cursor.fetchall()

    def get_contact(self, contact_id):
        self.cursor.execute(
            """
            SELECT
                contacts.id,
                contacts.first_name,
                contacts.last_name,
                contacts.phone_number,
                contacts.email,
                groups.name
            FROM contacts
            LEFT JOIN groups
                ON contacts.group_id = groups.id
            WHERE contacts.id = ?
            """,
            (contact_id,)
        )

        return self.cursor.fetchone()

    def search_contacts(self, text):
        pattern = f"%{text}%"

        self.cursor.execute(
            """
            SELECT
                contacts.id,
                contacts.first_name,
                contacts.last_name,
                contacts.phone_number,
                contacts.email,
                groups.name
            FROM contacts
            LEFT JOIN groups
                ON contacts.group_id = groups.id
            WHERE contacts.first_name LIKE ?
               OR contacts.last_name LIKE ?
               OR contacts.phone_number LIKE ?
            ORDER BY contacts.first_name
            """,
            (pattern, pattern, pattern)
        )

        return self.cursor.fetchall()

    def update_contact(
        self,
        contact_id,
        first_name,
        last_name,
        phone_number,
        email,
        group_id
    ):
        self.cursor.execute(
            """
            UPDATE contacts
            SET first_name = ?,
                last_name = ?,
                phone_number = ?,
                email = ?,
                group_id = ?
            WHERE id = ?
            """,
            (
                first_name,
                last_name,
                phone_number,
                email,
                group_id,
                contact_id
            )
        )

        self.connection.commit()

        return self.cursor.rowcount > 0

    def delete_contact(self, contact_id):
        self.cursor.execute(
            """
            DELETE FROM contacts
            WHERE id = ?
            """,
            (contact_id,)
        )

        self.connection.commit()

        return self.cursor.rowcount > 0 #see if the delete method was actually working #

    def close(self):
        self.connection.close()



































