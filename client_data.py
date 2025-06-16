from dataclasses import dataclass, field
from datetime import datetime

from credentials import ImmomioCredentials


@dataclass(frozen=True)
class ClientData:
    telegram_chatid: int
    telegram_username: str
    immomio_email: str | None = field(default=None)
    immomio_password: str | None = field(default=None)
    plan_activated_at: datetime | None = field(default=None)
    created_at: str = field(default=str(int(datetime.now().timestamp())))

    def immomio_creds(self) -> ImmomioCredentials | None:
        return (
            ImmomioCredentials(self.immomio_email, self.immomio_password)
            if self.immomio_email and self.immomio_password else
            None
        )

    def __str__(self):
        return (f"SAGA database client\n"
                f"TG username: {self.telegram_username}\n"
                f"TG chatid: {self.telegram_chatid}\n"
                f"IMMOMIO email: {self.immomio_email}\n"
                f"IMMOMIO password: {self.immomio_password}\n"
                f"PLAN activated at: {self.plan_activated_at}\n")
