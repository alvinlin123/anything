#!/usr/bin/env python
import time
import hashlib
import base64
import random

print "starting..."
startTimeMs = time.time() * 1000

toHash = b"hello world"
maxtry = 1 << 20
randNum = random.getrandbits(32)

for i in xrange(maxtry):
    randNum = randNum + i
    nounce = bytearray([(randNum & 0xff000000) >> 24, (randNum & 0x00ff0000) >> 16, (randNum & 0x0000ff00) >> 8, randNum & 0x000000ff ])
    bytearrayToHash = bytearray()
    bytearrayToHash.extend(toHash)
    bytearrayToHash.extend(nounce)
    sha256 = hashlib.sha256(bytearrayToHash).hexdigest()
    if sha256.startswith("00000"):
        print sha256
        break



endTimeMs = time.time() * 1000
print "done took %sms" %  (endTimeMs - startTimeMs)
