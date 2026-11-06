from jose import JWSError, jwt , JOSEError
from datetime import datetime , timedelta , timezone
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from  dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

#token create
def create_token(data : dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp":expire})

    return jwt.encode(to_encode , SECRET_KEY , algorithm=ALGORITHM)

#verify token
def token_verify(token : str = Depends(oauth2_schema)):
    try:
        payload = jwt.decode(token ,SECRET_KEY , algorithms=ALGORITHM)
        return payload
    except JWSError:
        raise HTTPException(status_code=401 , detail="Invalid token")

