import sqlite3
from datetime import datetime

from client_data import ClientData

class DatabaseClients(list):
    def __str__(self):
        return f"DatabaseClients[{len(self)}]: " + super().__str__()

    def by_telegram_username(self, telegram_username: str) -> ClientData | None:
        return next(filter(lambda client: client.telegram_username == telegram_username, self), None)


class ClientsDatabaseConnection(sqlite3.Connection):
    def __init__(self):
        super().__init__("clients.db")
        self.init_tables()

    def init_tables(self):
        cursor = self.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            telegram_chatid INTEGER NOT NULL,
            telegram_username TEXT NOT NULL,
            immomio_email TEXT DEFAULT NULL,
            immomio_password TEXT DEFAULT NULL,
            plan_activated_at DATETIME DEFAULT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

        self.commit()

    def write_client(self, client: ClientData):
        cursor = self.cursor()
        cursor.execute("""
           INSERT INTO clients (telegram_chatid,
                                telegram_username,
                                immomio_email,
                                immomio_password,
                                plan_activated_at,
                                created_at)
           VALUES (?, ?, ?, ?, ?, ?)
       """, (
            client.telegram_chatid,
           client.telegram_username,
           client.immomio_email,
           client.immomio_password,
           client.plan_activated_at.isoformat() if client.plan_activated_at else None,
           client.created_at
       ))
        self.commit()

    def read_clients(self) -> DatabaseClients:
        cursor = self.cursor()
        cursor.execute("SELECT * FROM clients")
        rows = cursor.fetchall()

        clients = []
        for row in rows:
            clients.append(ClientData(
                telegram_chatid=row[0],
                telegram_username=row[1],
                immomio_email=row[2],
                immomio_password=row[3],
                plan_activated_at=datetime.fromisoformat(row[4]) if row[4] else None,
                created_at=row[5]
            ))
        return DatabaseClients(clients)

    def update_plan_activated_at(self, telegram_username: str, activated_at: datetime):
        cursor = self.cursor()
        cursor.execute("""
                       UPDATE clients
                       SET plan_activated_at = ?
                       WHERE telegram_username = ?
                       """, (activated_at.isoformat(), telegram_username))
        self.commit()

    def update_immomio_credentials(self, telegram_username: str, email: str, password: str):
        cursor = self.cursor()
        cursor.execute("""
                       UPDATE clients
                       SET immomio_email    = ?,
                           immomio_password = ?
                       WHERE telegram_username = ?
                       """, (email, password, telegram_username))
        self.commit()

    def delete_client(self, telegram_username: str):
        cursor = self.cursor()
        cursor.execute("""
            DELETE FROM clients
            WHERE telegram_username = ?
        """, (telegram_username,))
        self.commit()

    def __enter__(self):
        print("Connected to database")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        print("Connection closed")
        super().close()
