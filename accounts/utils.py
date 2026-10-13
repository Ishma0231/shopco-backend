from rest_framework_simplejwt.tokens import RefreshToken
import random
import redis
from decouple import config
import json

redis_client=redis.Redis(
    host=config("REDIS_HOST"),
    port=config("REDIS_PORT",cast=int),
    db=config("REDIS_DB",cast=int),
    decode_responses=config("REDIS_DECODE_RESPONSE",cast=bool)
)

def generate_otp():
    return str(random.randint(100000,999999))


def save_signup_data(
        otp,
        email,
        first_name,
        last_name,
  
):
    key=f"signup:{email}"
    value=json.dumps(
        {
            "otp":otp,
            "email":email,
            "first_name":first_name,
            "last_name":last_name
        }
    )
    redis_client.set(
        key,
        value,
        ex=300
    )


def get_signup_data(email):
    key=f"signup:{email}"
    value=redis_client.get(key)
    if value is None:
        return None

    return json.loads(value)


def delete_signup_data(email):
    key=f"signup:{email}"
    redis_client.delete(key)

def generate_token(user):
    refresh=RefreshToken.for_user(user)
    access=refresh.access_token
    return {
        "access":str(access),
        "refresh":str(refresh)
    }

def save_login_data(email,otp):
    key=f"login:{email}"
    value=json.dumps({
        "otp":otp,
        "email":email
    })
    redis_client.set(
        key,
        value,
        ex=300
    )

def get_login_data(email):
    key=f"login:{email}"
    value=redis_client.get(key)
    if value is None:
        return None
    
    return json.loads(value)

def delete_login_data(email):
    key=f"login:{email}"
    redis_client.delete(key)