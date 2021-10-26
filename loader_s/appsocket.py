#!/usr/bin/env python3
def getserial():
 O="0000000000000000"
 try:
  f=open('/proc/cpuinfo','r')
  for b in f:
   if b[0:6]=='Serial':
    O=b[10:26]
  f.close()
 except:
  O="ERROR000000000"
 return O
global ns
ns=getserial()
from sentry_sdk import capture_exception,capture_message,init
try:
 aa=open('/etc/loader/loader/sentry.conf','r')
 D=aa.readlines()
 aa.close()
 P(D[0],server_name=ns,traces_sample_rate=1.0)
except Exception as e:
 print("erro sentry.conf")
import time
import threading 
import eventlet
import socketio 
global F
F=socketio.Server(cors_allowed_origins="*")
K=socketio.WSGIApp(F)
@F.event
def connect(sid,environ):
 print('connect ok ',sid)
 F.emit('my event',{'data':'foobar'})
@F.event
def my_message(sid,data):
 print('message ',data)
 F.emit('my event',{'data':'mensagem teste22'})
 F.emit('message',{'data':'mensagem teste44'})
@F.event
def medicao(sid,data):
 print('Enviando mensagem ',data)
 F.emit('medicao',data)
@F.event
def disconnect(sid):
 print('disconnect ',sid)
if __name__=='__main__':
 vr=0
 while True:
  vr=vr+1
  try:
   eventlet.wsgi.server(eventlet.listen(('',35494)),K)
  except Exception as e:
   T(e)
  time.sleep(5*vr)
  if vr>20:
   vr=0
# Created by pyminifier (https://github.com/liftoff/pyminifier)

