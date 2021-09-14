#!/usr/bin/env python3

from datetime import datetime, timedelta
import json
import os
import time

def resetar_fila():
    try:
        print('resetando')
        c = os.popen(f"git checkout .")
        c.read()
        c = os.popen(f"git clean -f -d")
        c.read()
        c.close()
        return 1
    except Exception as e:
        print('erro no git reset', e)
        return 0

def volta_backup():
    try:
        print('fazendo backup')
        c = os.popen(f"python3 ./../script_bkp.py")
        c.read()
        c.close()
        return 1
    except Exception as e:
        print('erro no git backup', e)
        return 0

def atualizando():
    try:
        if backup() == 1:
            time.sleep(10.0)
            resetar_fila()
            time.sleep(5.0)
            print("atualizando para nova versão")
            c = os.popen(f"git pull")
            c.read()
            c.close()
        return 1
    except Exception as e:
        print('erro atualização', e)
        return 0

def clear_bkp():
    try:
        now = datetime.now()
        print(now.year)
        c = os.popen(f"rm -fR ./../../loaders_bkp")
        c.read()
        c.close()
        return 1
    except Exception as e:
        print('erro clear_bkp', e)
        return 0

def backup():
    try:
        clear_bkp()
        import time
        time.sleep(5.0)
        now = datetime.now()
        print(now.year)
        c = os.popen(f"cp -fR ./../../loaders ./../../loaders_bkp")
        c.read()
        c.close()
        return 1
    except Exception as e:
        print('erro backup2', e)
        return 0


if __name__ == "__main__":
    atualizando()
