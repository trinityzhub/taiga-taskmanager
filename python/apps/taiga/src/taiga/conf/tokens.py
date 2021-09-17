# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos Ventures SL

from typing import Optional

from pydantic import BaseSettings, validator

ALLOWED_ALGORITHMS = (
    "HS256",
    "HS384",
    "HS512",
    "RS256",
    "RS384",
    "RS512",
)


class TokensSettings(BaseSettings):
    ALGORITHM: str = "HS256"
    SIGNING_KEY: str = ""
    VERIFYING_KEY: str = ""
    AUDIENCE: Optional[str] = None
    ISSUER: Optional[str] = None

    TOKEN_TYPE_CLAIM: str = "token_type"
    JTI_CLAIM: str = "jti"

    # Tokens lifetimes (in minutes)
    ACCESS_TOKEN_LIFETIME: int = 30
    REFRESH_TOKEN_LIFETIME: int = 8 * 24 * 60

    # Validators
    @validator("ALGORITHM", pre=True)
    def validate_algorithm(cls, v: str) -> str:
        if v not in ALLOWED_ALGORITHMS:
            raise ValueError(v)
        return v

    class Config:
        case_sensitive = True