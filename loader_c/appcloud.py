#!/usr/bin/env python3
import datetime
import json
import os
import ssl
import time
def getserial():
 P="0000000000000000"
 try:
  f=open('/proc/cpuinfo','r')
  for B in f:
   if B[0:6]=='Serial':
    P=B[10:26]
  f.close()
 except:
  P="ERROR000000000"
 return P
global ns
ns=getserial()
from sentry_sdk import capture_exception,capture_message,init
try:
 aa=open('/etc/loader/loader/sentry.conf','r')
 s=aa.readlines()
 R(s[0],server_name=ns,traces_sample_rate=1.0)
 aa.close()
except Exception as e:
 print("erro sentry.conf")
import pyrebase
f=open('/etc/loader/loader/firebase.conf','r')
r=f.readlines()
A=json.loads(r[0])
f.close()
i=pyrebase.initialize_app(A)
x=i.auth()
db=i.database()
print("--------------------f--------------------")
import socketio
def get_cpu_temp():
 t=open("/sys/class/thermal/thermal_zone0/temp")
 b=t.read()
 t.close()
 return float(b)/1000
from views import auth
global us
try:
 t=open('/etc/loader/loader/cloud.conf')
 G=t.read()
 t.close()
 us=auth.verify_and_decode_jwt(G)
 from datetime import datetime
 f=f'{datetime.now()}'
 dt={'hora':f,'log':'inicializando'}
 h=x.sign_in_with_email_and_password(us['user'],us['key'])
 db.child(ns).child("log").push(dt,h['idToken'])
except Exception as e:
 N(e)
 print('erro de autenticação',e)
def atualizar_firmware():
 import subprocess
 try:
  subprocess.run(["sudo","python3","/etc/loader/loader/atualiza.py"])
  return 1
 except Exception as e:
  N(e)
  return 0
def rollback_atualizar(v):
 from datetime import datetime
 import subprocess
 try:
  subprocess.run(["sudo","python3","/etc/loader/loader/rollback_updt.py"])
  d=datetime.now()
  M=open('/etc/loader/loader/version.conf','w')
  M.write(v-0.1)
  M.close()
  return 1
 except Exception as e:
  N(e)
  return 0
def verify_firmware():
 l=db.child(ns).child("firmware").get(h['idToken'])
 print('firmware22',l.val())
 fw=l.val()
 O=0
 try:
  t=open('/etc/loader/loader/version.conf')
  O=t.read()
  O=int(O)
  t.close()
 except Exception as e:
  N(e)
  print(e)
 try:
  global F
  F=0
  global k
  k=0
  for t in l.each():
   if t.key()== 'importance':
    F=t.val()
   if t.key()== 'version':
    k=t.val()
  print('testeeee',F,k)
  if F==9:
   if k>O:
    print('executar código de atualização')
    M=open('/etc/loader/loader/version.conf','w')
    M.write(str(k))
    M.close()
 except Exception as e:
  N(e)
  print(e)
def main():
 V=socketio.Client()
 global v
 v=290
 global D
 D=10
 global H
 H=22
 global o
 o=0
 @V.event
 def connect():
  print('connection established')
 @V.event
 def medicao(a):
  global us
  global ns
  global v
  v+=1
  global D
  D+=1
  global o
  global H
  global q
  try:
   q=x.sign_in_with_email_and_password(us['user'],us['key'])
  except Exception as e:
   N(e)
   print('erro de autenticação',e)
  if v>300:
   H+=1
   v=0
   a['cpu']=round(get_cpu_temp())
   a['filtro']=o
   if o==1:
    o=0
   else:
    o=1
   try:
    q=x.sign_in_with_email_and_password(us['user'],us['key'])
    db.child(ns).child("medicoes").push(a,q['idToken'])
   except Exception as e:
    N(e)
    print('erro de autenticação',e)
  if D>10:
   D=0
   a['cpu']=round(get_cpu_temp())
   try:
    db.child(ns).child("medicao").set(a,q['idToken'])
   except Exception as e:
    N(e)
    print('erro de autenticação',e)
  if H>24:
   H=0
   verify_firmware()
 @V.event
 def disconnect():
  print('disconnected from server')
 K=0 
 while True:
  K=K+1
  try:
   V.connect('http://0.0.0.0:35494')
   print('my sid is',V.sid)
   break
  except Exception as e:
   N(e)
   print('erro no servidor',e)
   if K>9:
    print('erro socket')
    break
   time.sleep(5.0*K) 
 V.wait() 
if __name__=='__main__':
 main()
# Created by pyminifier (https://github.com/liftoff/pyminifier)

