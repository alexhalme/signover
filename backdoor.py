import _clibash
from importlib import reload
import locaf as af
import gv
from locaf import En
import time
import lipsum
import tf
import re
import json

from cryptoAES import CryW
from crypto25519 import Crypt25519
import random

# speed test
plains = [b''.join([af.itb(random.randint(15,126)) for x in range(random.randint(100,1000))]) for y in range (100)]

asymKC = Crypt25519()


t = time.time()
for plain in plains:
  asym = asymKC.encrypt(plain)
  dasym = Crypt25519(asymKC.privateBytes, asymKC.publicBytes).decrypt(asym)
  assert(dasym == plain)

print(time.time() - t)


aes = En().rnd(16)._sha256()

t = time.time()
for plain in plains:
  sym = CryW(bytesMessage = plain, bytesPwrd = aes, slow = 1).encrypt()
  dsym = CryW(cryptedObj = sym, bytesPwrd = aes, slow = 1).decrypt()

  assert(dsym == plain)

print(time.time() - t)



# speed test
def makeNotes(n = 1, z = 1):
  generator = getattr(lipsum, {0: 'generate_words', 1: 'generate_sentences'}.get(random.randint(0, 1)))

  return {
    'nuid': tf.getUUID(),
    'cuid': tf.getUUID(),
    'history': [{
      'content': generator(random.randint(1, 4)),
      'uuid': tf.getUUID(),
      'time': random.randint(1613066000, 1628618000)
    } for x in range(random.randint(max(n, 1), z))]
  }

def makePt(cols = 5, n = 1, z = 1):
  return {
    'puid': tf.getUUID(),
    'name': re.sub(r'[,\.\?!]', r'', lipsum.generate_words(2)),
    'notes': [makeNotes(n, z) for x in range(cols)]
  }

aes = En()._rnd(32)

# scenario 1
listN = 30
tests = 100
toPrint = False

testList1 = [tf.jb([makePt(5, 1, 1) for x in range(listN)]) for y in range(tests)]
print(sum([len(x) for x in testList1])/tests)

times1 = []
result1 = []
for test in testList1:
  t = time.time()
  if toPrint:
    print(tf.bj(test))
  else:
    result1.append(tf.bj(test))
  times1.append(time.time() - t)

[[len(s['history']) for s in t['notes']] for t in tf.bj(test)]


testList2 = [tf.jb([makePt(5, 1, 10) for x in range(listN)]) for y in range(tests)]
print(sum([len(x) for x in testList2])/tests)

times2 = []
result2 = []
for test in testList2:
  t = time.time()
  if toPrint:
    print(tf.bj(test))
  else:
    result2.append(tf.bj(test))
  times2.append(time.time() - t)


print(f"Ratio: {sum(times2)/sum(times1)}")


[[len(s['history']) for s in t['notes']] for t in tf.bj(test)]




































