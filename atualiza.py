#!/usr/bin/env python3

from datetime import datetime, timedelta
import os
import time

import subprocess

def resetar_fila():
    try:
        print('resetando')
        subprocess.run(["git", "checkout", "--", "."])
        subprocess.run(["git", "clean", "-f", "-d"])
        return 1
    except Exception as e:
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
            subprocess.run(["sudo", "chmod", "-R", "777", "/etc/loader/loader"])
        return 1
    except Exception as e:
        print('erro atualização', e)
        return 0

def clear_bkp():
    try:
        now = datetime.now()
        print(now.year)
        subprocess.run(["rm" "-fR" "/etc/loader/loader_bkp"])
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
        subprocess.run(["cp", "-fR", "/etc/loader/loader", "/etc/loader/loader_bkp"])
        return 1
    except Exception as e:
        print('erro backup2', e)
        return 0


if __name__ == "__main__":
    atualizando()