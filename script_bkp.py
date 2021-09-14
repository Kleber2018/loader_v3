#!/usr/bin/env python3

#deixar uma pasta antes da principal

from datetime import datetime, timedelta
import json
import os

def clear_bkp():
    try:
        now = datetime.now()
        print(now.year)
        c = os.popen(f"rm -fR ./loaders_bkp")
        c.read()
        c.close()
        return 1
    except Exception as e:
        print('erro backup', e)
        return 0

def backup():
    try:
        clear_bkp()
        import time
        time.sleep(5.0)
        now = datetime.now()
        print(now.year)
        c = os.popen(f"cp -fR ./loaders ./loaders_bkp")
        c.read()
        c.close()
        return 1
    except Exception as e:
        print('erro backup', e)
        return 0

def voltar_backup():
    try:
        now = datetime.now()
        print(now.year)
        c = os.popen(f"cp -fR loaders_bkp/loader_a ./loaders")
        c = os.popen(f"cp -fR loaders_bkp/loader_m ./loaders")
        c = os.popen(f"cp -fR loaders_bkp/loader_s ./loaders")
        c.read()
        c.close()
        return 1
    except Exception as e:
        print('erro backup', e)
        return 0



if __name__ == "__main__":
    voltar_backup()
