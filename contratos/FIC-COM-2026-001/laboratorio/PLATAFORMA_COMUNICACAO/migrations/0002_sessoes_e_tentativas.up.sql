-- MOD-001: sessões revogáveis no servidor e registro de tentativas de login
CREATE TABLE sessions (id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, created_at TEXT NOT NULL, expires_at TEXT NOT NULL, revoked_at TEXT, FOREIGN KEY(user_id) REFERENCES users(id));
CREATE INDEX ix_sessions_user ON sessions(user_id);
CREATE TABLE login_attempts (id INTEGER PRIMARY KEY, username TEXT NOT NULL, ip TEXT NOT NULL, success INTEGER NOT NULL, at TEXT NOT NULL);
CREATE INDEX ix_login_attempts_user_at ON login_attempts(username, at);
CREATE INDEX ix_login_attempts_ip_at ON login_attempts(ip, at);
