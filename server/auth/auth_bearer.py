import os
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.jwt_token_handler import decode_access_token, verify_token
from modules.api_key.service.api_key_service import ApiKeyService
from modules.user.entity.user_identity import UserIdentity

api_key_service = ApiKeyService()


class AuthBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    def __call__(
            self,
            request: Request,
    ):
        credentials: Optional[HTTPAuthorizationCredentials] = super().__call__(
            request
        )
        self.check_scheme(credentials)
        token = credentials.credentials  # pyright: ignore reportPrivateUsage=none
        return self.authenticate(
            token,
        )

    def check_scheme(self, credentials):
        if credentials and credentials.scheme != "Bearer":
            raise HTTPException(status_code=401, detail="Token must be Bearer")
        elif not credentials:
            raise HTTPException(
                status_code=403, detail="Authentication credentials missing"
            )

    def authenticate(
            self,
            token: str,
    ) -> UserIdentity:
        if os.environ.get("AUTHENTICATE") == "false":
            return self.get_test_user()
        elif verify_token(token):
            return decode_access_token(token)
        elif api_key_service.verify_api_key(
                token,
        ):
            return api_key_service.get_user_from_api_key(
                token,
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid token or api key.")

    def get_test_user(self) -> UserIdentity:
        return UserIdentity(
            email="test@example.com", id="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"  # type: ignore
        )  # replace with test user information


def get_current_user(user: UserIdentity = Depends(AuthBearer())) -> UserIdentity:
    return user
