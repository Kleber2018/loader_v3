#!/usr/bin/env python3

from datetime import datetime, timedelta
import os
import time

import subprocess

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
    capture_message("atualizando projeto")
except Exception as e:
    print("erro sentry.conf")

def resetar_fila():
    try:
        print('resetando')
        subprocess.run(["git", "checkout", "--", "."])
        subprocess.run(["git", "clean", "-f", "-d"])
        return 1
    except Exception as e:
        capture_exception(e)
        print('erro no git reset', e)
        return 0

def atualizando():
    try:
        if backup() == 1:
            time.sleep(5.0)
            resetar_fila()
            time.sleep(5.0)
            print("atualizando para nova versão")
            subprocess.run(["sudo", "git", "pull"])
            time.sleep(40.0)
            subprocess.run(["sudo", "chmod", "-R", "777", "/etc/loader/loader"])
            time.sleep(10.0)
            subprocess.run(["sudo", "reboot"])
        return 1
    except Exception as e:
        capture_exception(e)
        print('erro atualização', e)
        return 0

def clear_bkp():
    try:
        now = datetime.now()
        print(now.year)
        subprocess.run(["rm" "-fR" "/etc/loader/loader_bkp"])
        return 1
    except Exception as e:
        capture_exception(e)
        print('erro clear_bkp', e)
        return 0

def backup():
    try:
        clear_bkp()
        import time
        time.sleep(5.0)
        now = datetime.now()
        print(now.year)
        subprocess.run(["cp", "-fR", "/etc/loader/loader", "/etc/loader/loader_bkp"])
        return 1
    except Exception as e:
        capture_exception(e)
        print('erro backup2', e)
        return 0


if __name__ == "__main__":
    atualizando()