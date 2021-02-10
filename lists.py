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
import json

# 0 - disabled, 1 - superuser, 2 - admin, 3 - regular, 4 - view only
PRIVS = {
  0: {0:[], 1:[], 2:[], 3:[], 4:[]},
  1: {0:[0, 1, 2, 3, 4], 1:[], 2:[0, 1, 2, 3, 4], 3:[0, 1, 2, 3, 4], 4:[0, 1, 2, 3, 4]},
  2: {0:[0, 2, 3, 4], 1:[], 2:[], 3:[0, 2, 3, 4], 4:[0, 2, 3, 4]},
  3: {0:[], 1:[], 2:[], 3:[], 4:[]},
  4: {0:[], 1:[], 2:[], 3:[], 4:[]},
}

class SOList:
  def __init__(self, auth, luid):
    self.auth, self.luid = auth, luid

    rights = self.auth.sql.getDataDict('rights', where = f"luid = '{luid}' AND uuid = '{self.auth.userDict['uuid']}'")
    self.rights = rights[0] if rights else None
    solst = self.auth.sql.getOneDataDict('lists', 'luid', luid)
    self.active = solst['active']
    self.disp = solst['disp']
    if not solst:
      self.active = self.rights = self.dat = self.aes = None
      return None

    self.aes = self.auth.keyring.decrypt(self.solst['aes'])
    if not self.aes:
      self.active = self.rights = self.dat = self.aes = None
      return None

    self.dat = tf.bj(self.solts['dat'], self.aes)
    if not self.dat:
      self.active = self.rights = self.dat = self.aes = None
      return None

  def vueList(self, summary = False):

    retval = {
      'admin': self.rights['priv'] in [1, 2],
      'list': {
        'luid': self.luid,
        'dat': self.dat,
        'active': self.active
      }
    }

    if summary:
      return retval

    return {**retval,
      'rights': self.vueRights(),
      'patients': self.vuePatients()
    }

  def vueRights(self):
    if not self.rights['priv'] in [1, 2]:
      return []

    uuids = self.auth.sql.getOneCol('rights', 'uuid', where = f"luid = '{self.luid}'")
    return self.auth.sql.getDataDicts('users', cols = ['uuid', 'email', 'dat'], where = ' OR '.join([f"uuid = '{uuid}'" for uuid in uuids]))

  def vuePatients(self):
    return []


  def updateList(self, newDat = None, newActive = None):

    self.auth.sql.replaceRows('lists', {
      'luid': self.luid,
      'dat': tf.jb(newDat if newDat else self.dat, self.aes),
      'active': newActive if newActive else self.solst['active']
    })


  def createList(self):

    self.luid = tf.getUUID()
    self.aes = En()._rnd(32)

    self.updateList(
      newDat = {
        'name': f"My new list {self.luid}",
        'cols': [{'type': 0, 'title': '', 'active': True, 'width': 200}]
      },
      newActive = 1
    )
    self.shareList(1, uuids = [self.auth.userDict['uuid']], first = True)


  def deleteRights(self, uluids):
    self.auth.sql.deleteCond('rights', where = ' OR '.join([f"(uuid = '{uuid}' AND luid = '{luid}')" for uuid, luid in uluids]))


  def shareList(self, priv, emails = None, uuids = None, first = False):
    if False if not first else not self.rights.get('priv'):
      return False

    if not priv in [0, 1, 2, 3, 4]:
      return False

    if emails:
      wheres = ' OR '.join([f"email = '{email}'" for email in af.iwList(emails)])
      if not wheres:
        return False
      query = self.auth.sql.fetch(f"SELECT uuid FROM users WHERE {wheres}")
      if not query:
        return False
      uuids = [x[0] for x in query]
    else:
      if not uuids:
        return False
      uuids = af.iwList(uuids)

    if self.auth.userDict['uuid'] in uuids and (True if first else priv <= self.rights.get('priv')):
      self.deleteRights((self.aut.userDict['uuid'], self.luid))
      self.auth.sql.replaceRows('rights', {
        'luid': self.luid,
        'uuid': self.auth.userDict['uuid'],
        'priv': priv,
        'aes': self.auth.keyring.encrypt(self.aes)
      })

    if first:
      return uuids

    # possible uuids ie where emails match and not self user's uuid
    uuidsPossible = list(set(uuids) - {self.auth.userDict['uuid']})

    allowedPrivs = PRIVS.get(self.rights.get('priv'))

    # where statement for privileges when priv would be allowed
    uuidsAllowedWheres = ' OR '.join([f"priv = {k}" for k, v in allowedPrivs.items() if priv in v])
    # uuids in rights table for this list where priv prevents Δ
    uuidsProhibited = self.auth.sql.getOneCol('rights', 'uuid', where = f"luid = {self.luid} AND NOT ({uuidsAllowedWheres})")
    # to-do list ie possible minus prohibited
    uuidsToDo = list(set(uuidsPossible) - set(uuidsProhibited))
    self.deleteRights([(uuid, self.luid) for uuid in uuidsToDo])
    self.replaceRows('rights', [{
      'uuid': uuid,
      'luid': self.luid,
      'priv': priv,
      'aes': self.asymEncrypt(uuid, self.aes)
    } for uuid in uuidsToDo])

    return uuidsToDo




  def asymEncrypt(self, uuid, blob):
    return self._asymEncrypt(self.auth.sql, uuid, blob)

  @classmethod
  def _asymEncrypt(cls, sql, uuid, blob):
    query = sql.fetch(f"SELECT pub FROM users WHERE uuid = '{uuid}'")
    if not query:
      return False
    return Crypt25519(publicBytes = query[0][0]).encrypt(blob)


















