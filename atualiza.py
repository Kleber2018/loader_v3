#!/usr/bin/env python3

from datetime import datetime, timedelta
import json
import os

def resetar_fila():
    try:
        print('resetando')
        c = os.popen(f"git reset")
        c.read()
        c.close()
        return 1
    except Exception as e:
        print('erro no git reset', e)
        return 0

def atualizando():
    try:
        resetar_fila()
        import time
        time.sleep(5.0)
        print("atualizando para nova versão")
        c = os.popen(f"git pull")
        c.read()
        c.close()
        return 1
    except Exception as e:
        print('erro atualização', e)
        return 0


if __name__ == "__main__":
    atualizando()
