#!/usr/bin/env python3

#deixar uma pasta antes da principal

from datetime import datetime, timedelta
import json
import os


def backup():
    try:
        now = datetime.now()
        print(now.year)
        c = os.popen(f"python3 ./../atualiza.py")
        c.read()
        c.close()
        return 1
    except Exception as e:
        print('erro backup', e)
        return 0


if __name__ == "__main__":
    backup()
