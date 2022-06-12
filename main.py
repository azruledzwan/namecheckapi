import uvicorn

import logging
from logging.config import dictConfig

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pydantic import BaseModel
from jose import jwt
from typing import Union, Any, Optional
from datetime import datetime, timedelta

from config import LogConfig
from config import APP_NAME, VERSION
from modules.namematch import NameMatcher
from security import ACCESS_TOKEN_EXPIRE_MINUTES
from security import Token, User, authenticate_user, users_dict
from security import get_current_user, create_access_token, get_password_hash

log_config = LogConfig()
log_config_dict = log_config.dict()
dictConfig(log_config_dict)
logger = logging.getLogger("NameCheckAPI")

# Log verbosity
logger.setLevel(logging.DEBUG)

# Token dependency injector
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI(
    title=APP_NAME,
    version=VERSION,
)
name_matcher = NameMatcher()


class NameCheckRequest(BaseModel):
    ic_name: str
    fpx_name: str
    account_uuid: str
    fpx_buyer_bank_id: str


# @app.post("/token", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(users_dict, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}


@app.post("/name_match/", summary="Match the name")
async def match_name(nameCheckRequest: NameCheckRequest):
    """Calculates and returns the similarity score between the two names.

    This is done by implementing a few preprocessing logic on the provided names before calculating the similarity scores.

    Depending on the buyer bank, names from FPX might have already been truncated. As such we will also truncate the IC name
     to match the length of FPX-provided name prior to making the comparison.

    For Maybank, the buyer bank ID is 'MB2U0227'. The maximum char length for Maybank is 25.

    For Public Bank, the buyer bank ID is 'PBB0233'. The maximum char length for Public Bank is 23.

    Args:
    * ic_name (str): Name of customer according to IC.
    * fpx_name (str): Name of customer from buyer bank (returned name from FPX).
    * fpx_buyer_bank_id (str): The buyer bank ID from FPX. 

    Returns:
    * float: The return value. Similarity score in percentages.

    """
    ic_name = nameCheckRequest.ic_name
    fpx_name = nameCheckRequest.fpx_name
    account_uuid = nameCheckRequest.account_uuid
    fpx_buyer_bank_id = nameCheckRequest.fpx_buyer_bank_id

    logger.debug(f'Name #1: {ic_name}')
    logger.debug(f'Name #2: {fpx_name}')
    logger.debug(f'Account UUID: {account_uuid}')
    logger.debug(f'FPX Buyer Bank ID: {fpx_buyer_bank_id}')

    score = name_matcher.match_names(ic_name, fpx_name, account_uuid, fpx_buyer_bank_id)
    response = JSONResponse({"score": score})

    logger.debug(f'Response: {response}')
    
    return response


@app.get("/healthcheck")
def healthcheck():
    """Health check endpoint"""
    return JSONResponse({"status": "healthy"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
