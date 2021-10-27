#!/usr/bin/env python3
#TESTE UTILIZANDO O GOOGLE IOT COM FLOWDATA

import datetime
import json
import os
import ssl
import time

def getserial():
    #https://qastack.com.br/raspberrypi/2086/how-do-i-get-the-serial-number
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:6]=='Serial':
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR000000000"
    return cpuserial

global ns
ns = getserial()
from sentry_sdk import capture_exception, capture_message, init
try:
    aa = open('/etc/loader/loader/sentry.conf', 'r')
    lines = aa.readlines()
    init(
        lines[0],
        server_name=ns,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0
    )
    aa.close()
except Exception as e:
    print("erro sentry.conf")


import pyrebase

f = open('/etc/loader/loader/firebase.conf', 'r')
r = f.readlines()
config = json.loads(r[0])
f.close()

firebase = pyrebase.initialize_app(config)
auth_fire = firebase.auth()

db = firebase.database()
print("--------------------f--------------------")


import socketio

def get_cpu_temp():
    tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp)/1000

from views import auth

global us

try:
    tempFile = open( '/etc/loader/loader/cloud.conf')
    jwt_user = tempFile.read()
    tempFile.close()
    us = auth.verify_and_decode_jwt(jwt_user)
    from datetime import datetime
    hora = f'{datetime.now()}'
    dt = {'hora': hora, 'log': 'inicializando'}
    user = auth_fire.sign_in_with_email_and_password(us['user'], us['key'])
    db.child(ns).child("log").push(dt, user['idToken']) #edita o mesmo arquivo
except Exception as e:
    capture_exception(e)

def atualizar_firmware():
    import subprocess
    try:
        subprocess.run(["sudo", "python3", "/etc/loader/loader/atualiza.py"])
        return 1
    except Exception as e :
        capture_exception(e)
        return 0

def rollback_atualizar(v):
    from datetime import datetime
    import subprocess
    try:
        subprocess.run(["sudo", "python3", "/etc/loader/loader/rollback_updt.py"])
        now = datetime.now()
        arquivo = open('/etc/loader/loader/version.conf', 'w')
        arquivo.write(v - 0.1)
        arquivo.close()
        return 1
    except Exception as e :
        capture_exception(e)
        return 0

def verify_firmware():
    firmware = db.child(ns).child("firmware").get(user['idToken']) #edita o mesmo arquivo
    fw = firmware.val()
    version_local = 0
    try:
        tempFile = open( '/etc/loader/loader/version.conf')
        version_local = tempFile.read()
        version_local = int(version_local)
        tempFile.close()
    except Exception as e:
        capture_exception(e)
        print(e)
    try:
        global importance
        importance = 0
        global version_web
        version_web = 0
        for t in firmware.each():
            if t.key() ==  'importance':
                importance = t.val()
            if t.key() ==  'version':
                version_web = t.val()
        print('testeeee', importance, version_web)
        if importance == 9:
            if version_web > version_local:
                print('executar código de atualização')
                atualizar_firmware()
                arquivo = open( '/etc/loader/loader/version.conf', 'w')
                arquivo.write(str(version_web))
                arquivo.close()
    except Exception as e:
        capture_exception(e)
        print(e)



def main():
    sio = socketio.Client()
    global contador
    contador = 290
    global contador2
    contador2 = 10
    global contador3
    contador3 = 22
    global filtro
    filtro = 0
    @sio.event
    def connect():
        print('connection established')
    @sio.event
    def medicao(data):
        global us
        global ns
        global contador
        contador += 1
        global contador2
        contador2 += 1
        global filtro
        global contador3
        global user_auth
        try:
            user_auth = auth_fire.sign_in_with_email_and_password(us['user'], us['key'])
        except Exception as e:
            capture_exception(e)
        if contador > 300:
            contador3 += 1
            contador = 0
            data['cpu'] = round(get_cpu_temp())
            data['filtro'] = filtro
            if filtro == 1:
                filtro = 0
            else:
                filtro = 1
            try:
                user_auth = auth_fire.sign_in_with_email_and_password(us['user'], us['key'])
                db.child(ns).child("medicoes").push(data, user_auth['idToken']) # cria novo arquivo
            except Exception as e:
                capture_exception(e)
        if contador2 > 10:
            contador2 = 0
            data['cpu'] = round(get_cpu_temp())
            try:
                db.child(ns).child("medicao").set(data, user_auth['idToken']) #edita o mesmo arquivo
            except Exception as e:
                capture_exception(e)
        if contador3 > 24:
            contador3 = 0
            verify_firmware()
    @sio.event
    def disconnect():
        print('disconnected from server')
    vr_erro = 0 #caso de erro de conexão ele tenta 10 vezes com intervalo de tempo exponencial
    while True:
        vr_erro = vr_erro+1
        try:
            sio.connect('http://0.0.0.0:35494')
            break
        except Exception as e:
            capture_exception(e)
            if vr_erro > 9:
                break
            time.sleep(5.0*vr_erro)     
    sio.wait()  


if __name__ == '__main__':
    main()
