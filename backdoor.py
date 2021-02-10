import _clibash
from importlib import reload
import locaf as af
import gv
from locaf import En
import time

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