import psycopg2
from psycopg2 import sql
from datetime import datetime
import os

CSV_file = "contacts_info.csv"

class ContactManager:

    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.connect_to_db()
        self.create_contacts_table()

    def connect_to_db(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True
        except psycopg2.DatabaseError as e:
            print(f"Database connection error: {e}")
            raise

    def create_contacts_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            phone VARCHAR(15),
            date_added TIMESTAMP
        )
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
        except psycopg2.DatabaseError as e:
            print(f"Error creating table: {e}")
            raise

    def add_contact(self, name, email, phone):
        if not name or not email or not phone:
            raise ValueError("Please enter data on all fields!")

        query = """
                INSERT INTO contacts (name, email, phone, date_added)
                VALUES (%s, %s, %s, %s)
                """
        date_added = datetime.now()

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (name, email, phone, date_added))
        except psycopg2.DatabaseError as e:
            raise Exception(f"Error adding contact to database: {e}")

    def update_contact(self, contact_id, name, email, phone):
        query = """
                UPDATE contacts
                SET name = %s, email = %s, phone = %s
                WHERE id = %s
                """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (name, email, phone, contact_id))
        except psycopg2.DatabaseError as e:
            raise Exception(f"Error updating contact in database: {e}")

    def get_contacts(self):
        query = "SELECT id, name, email, phone, date_added FROM contacts ORDER BY id ASC"

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                contacts = cursor.fetchall()
                return [{"ID": contact[0], "Name": contact[1], "Email": contact[2], "Phone": contact[3],
                         "Date Added": contact[4]} for contact in contacts]
        except psycopg2.DatabaseError as e:
            raise Exception(f"Error retrieving contacts from database: {e}")

    def delete_contact(self, contact_id):
        query = "DELETE FROM contacts WHERE id = %s"

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (contact_id,))
        except psycopg2.DatabaseError as e:
            raise Exception(f"Error deleting contact from database: {e}")

    def __del__(self):
        if self.connection:
            self.connection.close()