import os, secrets, hashlib, hmac, base64, json, time

SECRET = os.getenv('DG_COMM_SECRET', '')
SESSAO_HORAS = 8


def hash_password(password):
    if len(password) < 12: raise ValueError('A senha precisa ter pelo menos 12 caracteres')
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 260000)
    return 'pbkdf2$' + base64.b64encode(salt).decode() + '$' + base64.b64encode(digest).decode()


def verify_password(password, stored):
    try:
        _, s, d = stored.split('$')
        test = hashlib.pbkdf2_hmac('sha256', password.encode(), base64.b64decode(s), 260000)
        return hmac.compare_digest(test, base64.b64decode(d))
    except (ValueError, TypeError): return False


def new_session_id():
    return secrets.token_urlsafe(24)


def token_for(user_id, session_id):
    """Token assinado com o usuário e a sessão; a sessão é conferida no banco a cada requisição."""
    if len(SECRET) < 32: raise RuntimeError('DG_COMM_SECRET obrigatório, 32+ caracteres')
    dados = {'uid': user_id, 'sid': session_id, 'exp': int(time.time()) + SESSAO_HORAS * 3600}
    body = base64.urlsafe_b64encode(json.dumps(dados, separators=(',', ':')).encode()).decode().rstrip('=')
    sign = hmac.new(SECRET.encode(), body.encode(), 'sha256').hexdigest()
    return body + '.' + sign


def decode(token):
    """Devolve {'uid', 'sid'} se a assinatura e o prazo forem válidos; senão None."""
    if len(SECRET) < 32: return None
    try:
        body, sign = token.split('.', 1)
        expected = hmac.new(SECRET.encode(), body.encode(), 'sha256').hexdigest()
        if not hmac.compare_digest(sign, expected): return None
        data = json.loads(base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)))
        if data.get('exp', 0) < time.time() or not data.get('sid'): return None
        return {'uid': int(data['uid']), 'sid': str(data['sid'])}
    except (ValueError, IndexError, TypeError, KeyError): return None
