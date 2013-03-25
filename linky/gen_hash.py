import hashlib
from datetime import datetime


def gen_sha_hash(some_string):
    return hashlib.sha1(some_string + repr(datetime.utcnow())).hexdigest()