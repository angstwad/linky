import hashlib
from datetime import datetime


def generate(some_string):
    return hashlib.sha1(some_string + repr(datetime.utcnow())).hexdigest()
