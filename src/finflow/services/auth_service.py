from finflow.exceptions import AuthenticationError
from finflow.models.entities import User
from finflow.repositories.interfaces import UserRepository
from finflow.security import verify_password


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
    ) -> None:
        self._user_repository = user_repository

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> User:
        user = self._user_repository.get_by_username(
            username
        )

        if user is None or not verify_password(
            password,
            user.password_hash,
        ):
            raise AuthenticationError(
                "Invalid username or password"
            )

        if user.disabled:
            raise AuthenticationError(
                "User is disabled"
            )

        return user

    def get_user(self, username: str) -> User | None:
        return self._user_repository.get_by_username(
            username
        )