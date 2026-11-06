import os, secrets, hashlib, hmac, base64, json, time

SECRET=os.getenv('DG_COMM_SECRET','')

def hash_password(password):
    if len(password)<12: raise ValueError('A senha precisa ter pelo menos 12 caracteres')
    salt=secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,260000)
    return 'pbkdf2$'+base64.b64encode(salt).decode()+'$'+base64.b64encode(digest).decode()

def verify_password(password,stored):
    try:
        _,s,d=stored.split('$')
        test=hashlib.pbkdf2_hmac('sha256',password.encode(),base64.b64decode(s),260000)
        return hmac.compare_digest(test,base64.b64decode(d))
    except (ValueError,TypeError):return False

def token_for(user_id):
    if len(SECRET)<32: raise RuntimeError('DG_COMM_SECRET obrigatório, 32+ caracteres')
    body=base64.urlsafe_b64encode(json.dumps({'uid':user_id,'exp':int(time.time())+8*3600},separators=(',',':')).encode()).decode().rstrip('=')
    sign=hmac.new(SECRET.encode(),body.encode(),'sha256').hexdigest()
    return body+'.'+sign

def decode(token):
    if len(SECRET)<32: return None
    try:
        body,sign=token.split('.',1)
        expected=hmac.new(SECRET.encode(),body.encode(),'sha256').hexdigest()
        if not hmac.compare_digest(sign,expected):return None
        data=json.loads(base64.urlsafe_b64decode(body+'='*(-len(body)%4)))
        if data.get('exp',0)<time.time():return None
        return int(data['uid'])
    except (ValueError,IndexError,TypeError,KeyError):return None
