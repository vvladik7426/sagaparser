from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ClientData:
    telegram_chatid: int
    telegram_username: str
    immomio_email: str | None = field(default=None)
    immomio_password: str | None = field(default=None)
    plan_activated_at: datetime | None = field(default=None)
    created_at: str = field(default=str(int(datetime.now().timestamp())))

    def __str__(self):
        return f"SAGA database client {self.__dict__}"
