import _clibash
import locaf as af
import uuid
import json
import zlib
from locaf import En
from cryptoAES import CryW

def getUUID():
  return uuid.uuid4().__str__()

def jb(obj, aes = None):
  compressed = zlib.compress(En(json.dumps(obj))._by())
  return CryW(bytesMessage = compressed, bytesPwrd = aes).encrypt() if aes else compressed

def bj(obj, aes = None):
  compressed = CryW(cryptedObj = obj, bytesPwrd = aes).decrypt() if aes else obj
  if not compressed:
    return False
  return json.loads(zlib.decompress(compressed))
