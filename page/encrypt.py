import time
from jwt import encode, decode
from jwt.exceptions import InvalidSignatureError, DecodeError
from bcrypt import hashpw, checkpw, gensalt

JWT_SECRET = '5d0e5c7104e6cb669cf4c04b'
JWT_EXP_LENGTH = 7200 # 60 * 60 * 2 s = 2 h
JWT_REMEMBER_LENGTH = 604800 # 60 * 60 * 24 * 7 s = 7 day
JWT_ALGORITHM = 'HS256'
BCRYPT_SALT_LENGTH = 10

def jwt_generator(payload: dict, exp=JWT_EXP_LENGTH, secret=JWT_SECRET, algorithm=JWT_ALGORITHM):
    gen_time = time.time()
    refresh_time = gen_time
    exp_time = refresh_time + exp
    payload.update({
        'gen_time': gen_time,
        'refresh_time': refresh_time,
        'exp_time': exp_time
    })
    jwt = encode(payload, secret, algorithm=algorithm).decode()
    return jwt, payload

def jwt_refresher(payload: dict, exp=JWT_EXP_LENGTH, secret=JWT_SECRET, algorithm=JWT_ALGORITHM):
    refresh_time = time.time()
    exp_time = refresh_time + exp
    payload.update({
        'refresh_time': refresh_time,
        'exp_time': exp_time
    })
    jwt = encode(payload, secret, algorithm=algorithm).decode()
    return jwt, payload

def jwt_run(payload=None, jwt=None, exp=JWT_EXP_LENGTH, secret=JWT_SECRET, algorithm=JWT_ALGORITHM):
    status = False
    new = False
    if payload and jwt is None:
        status = True
        new = True
        msg = '登录成功'
        jwt, payload = jwt_generator(payload, exp, secret, algorithm)

    elif payload is None and jwt:
        try:
            payload = decode(jwt, secret, algorithm=algorithm)
            now = time.time()
            exp_time = payload.get('exp_time', 0)
            gen_time = payload.get('gen_time', 0)
            remember = payload.get('remember', False)

            if exp_time >= now:
                status = True
                msg = '登录成功'
            elif remember and gen_time + JWT_REMEMBER_LENGTH >= now:
                status = True
                new = True
                msg = '登录成功'
                jwt, payload = jwt_refresher(payload, exp, secret, algorithm)
            else:
                msg = 'JWT过期, 请重新登录'

        except (InvalidSignatureError, DecodeError):
            msg = 'JWT无效, 请重新登录'

    return status, new, msg, jwt, payload

def bcrypt_generator(password, salt_length=BCRYPT_SALT_LENGTH):
    return hashpw(password.encode(), gensalt(salt_length)).decode()

def bcrypt_checker(password, hashed):
    return checkpw(password.encode(), hashed.encode())
