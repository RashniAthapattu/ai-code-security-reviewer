"""Deliberately insecure sample code for demos and tests. Do not copy.

Every problem here is on purpose, so the scanners have something to find.
"""

import hashlib
import pickle
import subprocess

API_PASSWORD = "hunter2"


def list_directory(path):
    # Command injection: the path is placed into a shell command
    return subprocess.call("ls " + path, shell=True)


def fingerprint(data):
    # MD5 is a broken hash
    return hashlib.md5(data).hexdigest()


def load_session(blob):
    # Loading untrusted pickle data can run attacker code
    return pickle.loads(blob)


def calculate(expression):
    # eval() runs whatever text it is given
    return eval(expression)


def disk_usage():
    # Probably fine: a fixed command with no user input
    return subprocess.call(["df", "-h"])
