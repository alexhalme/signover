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
import sms


class GSQLBridge:
  SQL = wsql.WSQL(*gv.SQL_CRED)

  def __init__(self, sqlCredentials = gv.SQL_CRED):
    self.reassignSQLCredentials(sqlCredentials)

  @classmethod
  def reassignSQLCredentials(cls, sqlCredentials):
    cls.SQL = wsql.WSQL(*sqlCredentials)

  def killSession(self, uuids):
    userDicts = self.SQL.getDataDicts('users', where = ' OR '.join([f"uuid = '{uuid}'" for uuid in af.iwList(uuids)]))
    self.SQL.replaceRows('users', [{**userDict, 'saes': b''} for userDict in userDicts])


class AuthSo:
  # store Starlette request
  REQUEST = None

  # init either with email (allows getting challenge) or cookie (decrypts)
  def __init__(self, email = None, cookie = None, sqlCredentials = gv.SQL_CRED, req = None):
    self.sqlCredentials = sqlCredentials
    self.sql = wsql.WSQL(*sqlCredentials)
    self.email = email
    self.cookieIn, self.cookieOut = cookie, None
    self.priv = None

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

    query = self.sql.fetch(f"SELECT luid FROM lists WHERE luid IN (SELECT luid FROM rights WHERE {wheres}){' AND active = 1' if active else ''}")
    luids = [] if not query else [lst[0] for lst in query]

    return luids


  def setLists(self, summary = None, specific = None):
    self.sql.reconnect()

    for typeLst in [True, False] if summary is None else [summary]:
      luids = list(set(self.getLuids(disp = not typeLst)).intersection(set(af.iwList(specific)))) if specific else self.getLuids(disp = not typeLst)
      solsts = [lists.SOList(self, luid) for luid in luids]
      self.response[f"{'s' if specific else ''}{'s' if typeLst else 'd'}lists"] = [solst.vueList(typeLst) for solst in solsts]

  def setSelf(self):
    self.sql.reconnect()
    self.response['user'] = {k: tf.bj(v) if k == 'dat' else v for k, v in self.userDict.items() if k in ['uuid', 'email', 'phone', 'dat', 'pwrdchange']}

  # set a response - then used in routes.py when returning
  def setResponse(self, response):
    self.response.update(response)
    return self

  # kill this user's session
  def killSession(self):
    GSQLBridge().killSession([self.userDict['uuid']])
    return self


  def changePassword(self, newHash, pub, priv):
    testBytes = En()._rnd(32)
    assert( testBytes == Crypt25519(privateBytes=priv).decrypt(Crypt25519(publicBytes=pub).encrypt(testBytes)) )

    self.userDict.update({
      'nextkeys': None,
      'priv': CryW(bytesMessage = newHash + priv, bytesPwrd = newHash).encrypt(),
      'pub': pub
    })

    self.sql.replaceRows('users', self.userDict)
    self.sql.reconnect()



  # from PBKDF2 b64 encoded from FE, get cookie
  def getCookie(self, login):
    # get encrypted vault for this user and try to decrypt
    decrypted = {
      k: CryW(
        cryptedObj = self.userDict['priv'] if k == 'current' else self.parseNextKeys(self.userDict['nextkeys'])[3],
        pbkd = En(v)._by64()
      ).decrypt() for k, v in login.pbkdf2b64.items()
    }

    decrypted = {k: v for k, v in decrypted.items() if v}
    if not decrypted:
      return False

    # we can cancel the request as user knows password
    if login.type == 'reset' and decrypted.get('current'):
      self.sql.wesc(f"UPDATE users SET nextkeys* WHERE uuid*'", v = [(None, self.userDict['uuid'])])

    # case where 'nextkeys' needs to be moved to usual permanents vaults ie new user or pwrd reset (not change, reset)
    if set(decrypted.keys()) == {'next'}:
      _, _, pub, _ = self.parseNextKeys(self.userDict['nextkeys'])
      self.hashedpwrd, self.priv = login.newhash, decrypted.get('next')[64:]
      self.changePassword(self.hashedpwrd, pub, self.priv)
    else:
      # decrypt the user's vault which contains (1) the hashed pwrd and (2) the private Ed25519 key
      self.hashedpwrd, self.priv = decrypted.get('current')[0:64], decrypted.get('current')[64:]

    # case where we are just Δing password
    if login.type == 'change':
      if not login.newhash:
        return False
      self.hashedpwrd = login.newhash
      self.changePassword(self.hashedpwrd, self.userDict['pub'], self.priv)



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

    # from bytes huuid get uuid len 36 which IDs user and get SQL dict (line) for this user
    self.userDict = self.sql.getOneDataDict('users', 'uuid', self.ioUUID(huuid))

    # in case login from cookie
    if not self.email:
      if False if not self.userDict else self.userDict.get('email'):
        self.email = self.userDict.get('email')
      else:
        return False

    # check that cookie not expired
    if int(time.time()) - gv.COOKIE.MAX > af.ifb(cookieBytes[48:]):
      return False

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

    # none if never logged in + case where first login ever *or* reset email password
    privateKeys = {
      'current': self.userDict['priv'],
      'next': self.parseNextKeys(self.userDict['nextkeys'])[3]
    }

    # analyze content of dict to figure out what type is to be sent to front end -> standard, reset, change, first
    # (cookie and forgot are other 'types' but not relevant here)
    if privateKeys.get('next'):
      self.response['type'] = 'reset' if self.userDict['pub'] else 'first'
    else:
      self.response['type'] = 'next' if self.userDict['pwrdchange'] else 'standard'

    return {k: En(CryW.getChallenge(v))._b64() for k, v in privateKeys.items() if v}


  def parseNextKeys(self, nextKeys):
    if not nextKeys:
      return b'', b'', b'', b''
    return af.ifb(nextKeys[0:4]), nextKeys[4:36], nextKeys[36:68], nextKeys[68:]

  # add a user from email when init AuthSo
  def addUser(self, email):
    if not re.fullmatch(re.compile('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'), email):
      return False

    query = self.sql.fetch(f"SELECT uuid FROM users WHERE email = '{email}'")
    if query:
      return query[0][0]

    newUUID = tf.getUUID()
    self.sql.replaceRows('users', {
      'uuid': newUUID,
      'email': email,
      'priv': None,
      'pub': None,
      'dat': tf.jb({'name': email}),
      'pwrdchange': 1,
      'active': 0
    })

    self.requestPwrdReset(newUUID, newAccount = True)

    return newUUID


  def newKeypair(self):
    password = En()._rnd58(8)
    keys25519 = Crypt25519()
    return password, CryW(bytesMessage = En(password)._sha512u() + keys25519.privateBytes, bytesPwrd = En(password)._sha512u()).encrypt(), keys25519.publicBytes

  def requestPwrdReset(self, uuid, newAccount = False):
    self.sql.reconnect()
    userDict = self.sql.getOneDataDict('users', 'uuid', uuid)

    password, priv, pub = self.newKeypair()

    cancel = En()._rnd(32)

    message = {
      'Subject': 'Signout password change request',
      'TextPart': f"Dear {tf.bj(userDict['dat'])['name']},\r\nA request to {'create an account' if newAccount else 'change password'} "
                  f"was made to signout.\r\n\r\nIf you did not make this request, you can cancel it with this link: "
                  f"https://so.alexhal.me/cancel/{En(self.ioUUID(uuid) + cancel)._b58()}."
                  f"\r\n\r\nOtherwise, your temporary password is: {password}.\r\n\r\nThe Signout team."
    }
    email = sms.Mailjet(af.iob('mailjetapi.txt').decode('utf8'), 'alex@alexhal.me')
    email.send(message, userDict['email'])

    userDict['nextkeys'] = af.itb(int(time.time())) + En(cancel)._sha256() + pub + priv
    if newAccount:
      userDict['pub'] = pub
    self.sql.replaceRows('users', userDict)

    return password, priv, pub


password = 'baeTgwM3VSG'
msg= b'\x16C\xd8\xa6\xc1\xdb~\xcdY\xc3\xd77\xeb\xfe\xa1\x0e\x9c\xe4\xdc:m5\xe7\xf5|\xc1\xb2U\x15\xbb\xe9\xd6\x86\xc1\xd8\xdcM\xb2\xeez\xd3\xe5C\xb9o\x1eN\x040\x19_\xe6\xc8\x9b\xdee\x95\xe2t\xe9\x82\xdd\xf5\t\x80U\xeb/\x08\xab~\xe5\x86"\xdf\xf2\xf2\x04!P\xae\xc5\xe9tv\x1c\xb9|\xbd\x99\xd2\xf1V\x14\x04\xac'
cipher = CryW(bytesMessage = msg, bytesPwrd = En(password)._sha512u()).encrypt()

CryW(cryptedObj = cipher, bytesPwrd = En(password)._sha512u()).decrypt()






















def nothing():
  self = AuthSo(email = 'alex@alexhal.me')
  self.getCookie(cryptoAES.JS('DpPAnp1Vg9F', self.getChallenge()))
  self = AuthSo(cookie = self.cookieOut)