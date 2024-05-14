import mysql.connector


class Database():
    def __init__(self, host, user, password, database):
        self.database = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.database_cursor = self.database.cursor()
    def get_table(self, table):
        self.database_cursor.execute(f"SELECT * FROM {table}")
        table = self.database_cursor.fetchall()
        return table

    def get_table_sorted(self, table, row):
        self.database_cursor.execute(f"SELECT * FROM {table} ORDER BY {row}")
        table = self.database_cursor.fetchall()
        return table

    def delete_row(self, table, room):
        self.database_cursor.execute(f"DELETE FROM {table} WHERE room = '{room}'")
        self.database.commit()





