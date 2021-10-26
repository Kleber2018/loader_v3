import hmac
import hashlib
import base64
import json
import datetime
import sqlite3
from app import app
bd='/etc/loader/loader/conf_banco.db'
def getserial():
 d="0000000000000000"
 try:
  f=open('/proc/cpuinfo','r')
  for w in f:
   if w[0:6]=='Serial':
    d=w[10:26]
  f.close()
 except:
  d="ERROR000000000"
 return d
global ns
ns=getserial()
from sentry_sdk import capture_exception,capture_message,init
try:
 aa=open('/etc/loader/loader/sentry.conf','r')
 t=aa.readlines()
 aa.close()
 G(t[0],server_name=ns,traces_sample_rate=1.0)
except Exception as e:
 print("erro sentry.conf")
 M(e)
i='52d3f853c19f8b63c0918c126422aa2d99b1aef33ec63d41dea4fadf19406e54' 
def create_jwt(K):
 try:
  X=open('/etc/loader/loader/key.conf','r')
  i=X.readline()
  X.close()
 except Exception as e:
  M(e)
  print('erro ao acessar key.conf - create_jwt')
 K=json.dumps(K).encode()
 R=json.dumps({'typ':'JWT','alg':'HS256'}).encode()
 C=base64.urlsafe_b64encode(R).decode()
 r=base64.urlsafe_b64encode(K).decode()
 q=hmac.new(key=i.encode(),msg=f'{b64_header}.{b64_payload}'.encode(),digestmod=hashlib.sha256).digest()
 e=f'{b64_header}.{b64_payload}.{base64.urlsafe_b64encode(signature).decode()}'
 return e
def verify_and_decode_jwt(e):
 try:
  X=open('/etc/loader/loader/key.conf','r')
  i=X.readline()
  X.close()
 except Exception as e:
  M(e)
  print('erro ao acessar key.conf - verify jwt')
 try:
  C,r,x=e.split('.')
  P=base64.urlsafe_b64encode(hmac.new(key=i.encode(),msg=f'{b64_header}.{b64_payload}'.encode(),digestmod=hashlib.sha256).digest()).decode()
  K=json.loads(base64.urlsafe_b64decode(r))
  f=datetime.datetime.now().timestamp()
  if K.get('exp')and K['exp']<f:
   raise Exception('Token expirado')
  if P!=x:
   raise Exception('Assinatura invalida')
  return K
 except Exception as e:
  M(e)
  return{'erro':'Token invalido'}
def verify_key_mac():
 try:
  from uuid import getnode as get_mac
  X=open('/etc/loader/loader/load.conf','r')
  I=X.readline()
  X.close()
  o=verify_and_decode_jwt(I)
  if f"{get_mac()}"==f"{decoded['cod']}":
   return 1
 except Exception as e:
  M(e)
  print('erro ativação key',e)
  return 0
def verify_key():
 try:
  X=open('/etc/loader/loader/load.conf','r')
  I=X.readline()
  X.close()
  o=verify_and_decode_jwt(I)
  print(f"código: {decoded['cod']}")
  if f"{getserial()}"==f"{decoded['cod']}":
   return 1
  else:
   return 0
 except Exception as error:
  M(error)
  print('erro ativação key',error)
  return 0
def autentication_api(u,m):
 try:
  O=sqlite3.connect(bd)
  N=O.cursor()
  N.execute("SELECT login, senha, nome, telefone, email, privilegios FROM usuario " "WHERE login = ? and senha = ?",(u,m))
  z=N.fetchall()
  N.close()
  O.close()
  if len(z)==1:
   print('antes',z[0][0])
   print(z[0][0])
   K={'login':u,'senha':m}
   Q=create_jwt(K)
   return{'token':Q}
  else:
   return{'erro':'Usuario ou senha invalido!'}
 except Exception as e:
  M(e)
  print(f"Erro bd: {e}")
  return{'erro':f"Erro BD: {e}",'description':'Erro no banco de dados, reinicie a central!'}
def verify_autentication_api(I):
 H=verify_and_decode_jwt(I)
 if 'senha' in H:
  if 'login' in H:
   print('existe')
  else:
   return{'erro':'Usuario invalido!'}
 else:
  return{'erro':'Senha invalida!'}
 try:
  O=sqlite3.connect(bd)
  N=O.cursor()
  N.execute("SELECT login, senha, nome, telefone, email, privilegios FROM usuario " "WHERE login = ? and senha = ?",(H['login'],H['senha']))
  z=N.fetchall()
  N.close()
  O.close()
  if len(z)==1:
   return{'autenticado':'ok'}
  else:
   return{'erro':'Usuario ou senha invalido!'}
 except Exception as e:
  M(e)
  print(f"Erro SQLite: {e}")
  return{'erro':f"Erro BD: {e}",'description':'Erro no banco de dados, reinicie a central!'}
def button_login(u,m):
 try:
  X=open('/etc/loader/loader/login_livre.conf','r')
  h=X.readline()
  X.close()
  S=datetime.fromisoformat(h)
  y=datetime.now()
  print(y,S,y+F(minutes=3))
  print(y>S,S+F(minutes=3)>y)
  if y>S and S+F(minutes=3)>y:
   try:
    O=sqlite3.connect(bd_conf)
    N=O.cursor()
    N.execute("INSERT INTO usuario(login, senha, nome, telefone, email, privilegios) VALUES (?, ?, ?, '', '', 'default');",(u,m,u))
    O.commit()
    N.close()
    O.close()
    return 1
   except Exception as e:
    M(e)
    print(f"Erro SQLite: {e}")
    return 0
  else:
   return 0
 except Exception as e:
  M(e)
  print('erro ao criar arquivo',e)
  return 0
# Created by pyminifier (https://github.com/liftoff/pyminifier)

