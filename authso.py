import _clibash
import locaf as af
from locaf import En
import wsql
import gv
import re
import tf
from cryptoAES import CryW
from crypto25519 import Crypt25519
import time
from starlette.responses import JSONResponse
import lists

class AuthSo:
  # store Starlette request
  REQUEST = None

  # init either with email (allows getting challenge) or cookie (decrypts)
  def __init__(self, email = None, cookie = None, sqlCredentials = gv.SQL_CRED, req = None):
    self.sqlCredentials = sqlCredentials
    self.sql = wsql.WSQL(*sqlCredentials)
    self.email = email
    self.cookieIn, self.cookieOut = cookie, None

    # at end usually call <AuthSo obj>.responseType(<AuthSo obj>.response)
    self.response = {}
    self.responseType = JSONResponse

    # sql line for user
    if self.email:
      self.userDict = self.sql.getOneDataDict('users', 'email', self.email)

    # what is returned in routes.py
    if req and not self.REQUEST:
      self.setRequest(req)

    # same as 'email' but from cookie
    if self.cookieIn:
      if not self.parseCookie():
        return None

  # so it is available globally
  @classmethod
  def setRequest(cls, req):
    cls.REQUEST = req


  def getLuids(self, active = True, disp = True):
    # list of lists where user has rights
    wheres = f"uuid = '{self.userDict['uuid']}'"
    if disp:
      wheres = f"{wheres} AND disp = 1"

    query = self.sql.fetch(f"SELECT luid FROM lists WHERE luid = (SELECT luid FROM rights WHERE {wheres}){' AND active = 1' if active else ''}")
    luids = [] if not query else [lst[0] for lst in query]

    return luids


  def setLists(self, summary = None):
    for typeLst in [True, False] if summary is None else [summary]:
      solsts = [lists.SOList(self, luid) for luid in self.getLuids(disp = not typeLst)]
      self.response[f"{'s' if typeLst else 'd'}lists"] = [solst.vueList(typeLst) for solst in solsts]

  def setSelf(self):
    self.response['user'] = {k: tf.bj(v) if k == 'dat' else v for k, v in self.userDict.items() if k in ['uuid', 'email', 'phone', 'dat', 'pwrdchange']}

  # set a response - then used in routes.py when returning
  def setResponse(self, response):
    self.response.update(response)
    return self

  # from PBKDF2 b64 encoded from FE, get cookie
  def getCookie(self, pbkdf2b64):
    # get encrypted vault for this user and try to decrypt
    decrypted = CryW(cryptedObj = self.userDict['priv'], pbkd = En(pbkdf2b64)._by64()).decrypt()
    if not decrypted:
      return False

    # decrypt the user's vault which contains (1) the hashed pwrd and (2) the private Ed25519 key
    self.hashedpwrd, self.priv = decrypted[0:64], decrypted[64:]

    # cookie content in bytes: 16 bytes for uuid, 32 bytes of session AES 'secret' (not key) and time UTC, make b64 cookie
    cookieBytes = self.ioUUID(self.userDict['uuid']) + En()._rnd(32) + af.itb(int(time.time()))
    self.cookieOut = En(cookieBytes)._b64()

    # then rotate user's vault (avoid replay attack if XSS attack getting client-generated PBKDF2) and generate session
    # AES vault which is a SHA256 hashed combination of AES 'secret' above with time UTC so even a corrupt browser
    # can't fake cookie time generation to server as the hash which decrypts the session vault would change
    self.sql.replaceRows('users', {
      **self.userDict,
      'priv': CryW(bytesMessage = self.hashedpwrd + self.priv, bytesPwrd = self.hashedpwrd).encrypt(),
      'saes': CryW(bytesMessage = self.priv, bytesPwrd = En(cookieBytes[16:])._sha256()).encrypt(),
    })

    self.keyring = Crypt25519(self.priv, self.userDict['pub'])

    return True

  # as above but just renewal ie no access to user vault or hashed pwrd
  def renewCookie(self):
    # ensure the renewed cookie will be valid ie current cookie can actually decrypt the session vault
    if not CryW(cryptedObj=self.userDict['saes'], bytesPwrd=En(En(self.cookieIn)._by64()[16:])._sha256()).decrypt():
      return False

    # create a new session vault with known, same private Ed25519 key but change the 'secret' and time hence AES key too
    cookieBytes = self.ioUUID(self.userDict['uuid']) + En()._rnd(32) + af.itb(int(time.time()))
    self.cookieOut = En(cookieBytes)._b64()
    self.sql.replaceRows('users', {
      **self.userDict,
      'saes': CryW(bytesMessage = self.priv, bytesPwrd = En(cookieBytes[16:])._sha256()).encrypt(),
    })

    return True

  # decipher cookie into uuid, secret, time; check time and validity of decryption + recover Ed25519 private key
  def parseCookie(self):
    # b64 → bytes, huuid (16 bytes) + AES 'secret' + time (UTC/*nix)
    cookieBytes = En(self.cookieIn)._by64()
    huuid, phKey, ts = cookieBytes[0:16], cookieBytes[16:48], cookieBytes[48:]

    # in case login from cookie
    if not self.email:
      self.userDict = self.sql.getOneDataDict('users', 'uuid', self.ioUUID(huuid))
      if False if not self.userDict else self.userDict.get('email'):
        self.email = self.userDict['email']
      return False

    # check that cookie not expired
    if int(time.time()) - gv.COOKIE.MAX > af.ifb(cookieBytes[48:]):
      return False

    # from bytes huuid get uuid len 36 which IDs user and get SQL dict (line) for this user
    self.userDict = self.sql.getOneDataDict('users', 'uuid', self.ioUUID(huuid))
    if not self.userDict:
      return False

    # concatenate AES 'secret' with time and SHA256 hash to get AES key to decrypt 'saes' session vault and get
    # Ed25519 private key
    self.priv = CryW(cryptedObj = self.userDict['saes'], bytesPwrd = En(phKey + ts)._sha256()).decrypt()

    # keyring
    if self.priv:
      self.keyring = Crypt25519(self.priv, self.userDict['pub'])

    return bool(self.priv)

  # len 36 UUID <- -> len 16 bytes of same
  @classmethod
  def ioUUID(cls, val):
    if len(val) == 36:
      return En(val.replace('-', ''))._by16()
    if len(val) == 16:
      return f"{En(val)._b16().lower()[0:8]}-{En(val)._b16().lower()[8:12]}-{En(val)._b16().lower()[12:16]}-{En(val)._b16().lower()[16:20]}-{En(val)._b16().lower()[20:]}"
    return False


  # get PBKDF2 challenge (using by default user's private key)
  def getChallenge(self):
    if not self.userDict:
      return False
    return En(CryW.getChallenge(self.userDict['priv']))._b64()

  # add a user from email when init AuthSo
  def addUser(self, dat):
    if not re.fullmatch(re.compile('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'), self.email):
      return False
    if self.email in self.sql.getOneCol('users', 'email', self.email):
      return False

    password = En()._rnd58(8)
    keys25519 = Crypt25519()

    self.sql.replaceRows('users', {
      'uuid': tf.getUUID(),
      'email': self.email,
      'priv': CryW(bytesMessage = En(password)._sha512u() + keys25519.privateBytes, bytesPwrd = En(password)._sha512u()).encrypt(),
      'pub': keys25519.publicBytes,
      'dat': tf.jb(dat),
      'pwrdchange': 1,
      'active': 1
    })

    return En(password)._b58()

def nothing():
  self = AuthSo(email = 'alex@alexhal.me')
  self.getCookie(cryptoAES.JS('DpPAnp1Vg9F', self.getChallenge()))
  self = AuthSo(cookie = self.cookieOut)