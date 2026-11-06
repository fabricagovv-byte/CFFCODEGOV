import argparse, sqlite3
from .db import init,connect
from .security import hash_password
from .main import now

def main():
    parser=argparse.ArgumentParser(description='Administração de usuários do MVP Digitalgov')
    parser.add_argument('command',choices=['init','add-user'])
    parser.add_argument('--name',default='Administrador');parser.add_argument('--username',default='admin');parser.add_argument('--password');parser.add_argument('--role',default='ADMIN')
    a=parser.parse_args();init()
    if a.command=='init':print('Banco de dados criado, sem usuários ou conteúdo fictício');return
    if a.role not in {'ADMIN','EDITOR','APPROVER','VIEWER'}:parser.error('Perfil inválido')
    if not a.password:parser.error('Informe --password (não compartilhe em repositórios)')
    try:
        with connect() as c:c.execute('INSERT INTO users(name,username,password_hash,role,created_at) VALUES(?,?,?,?,?)',(a.name,a.username,hash_password(a.password),a.role,now()))
    except sqlite3.IntegrityError:parser.error('Usuário já existe')
    print('Usuário criado:',a.username,a.role)
if __name__=='__main__':main()
