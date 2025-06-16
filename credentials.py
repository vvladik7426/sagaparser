from dataclasses import dataclass


@dataclass(frozen=True)
class ImmomioCredentials:
    email: str
    password: str