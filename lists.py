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
import zlib

# 0 - disabled, 1 - superuser, 2 - admin, 3 - regular, 4 - view only
PRIVS = {
  0: {0:[], 1:[], 2:[], 3:[], 4:[]},
  1: {0:[0, 1, 2, 3, 4], 1:[], 2:[0, 1, 2, 3, 4], 3:[0, 1, 2, 3, 4], 4:[0, 1, 2, 3, 4]},
  2: {0:[0, 2, 3, 4], 1:[], 2:[], 3:[0, 2, 3, 4], 4:[0, 2, 3, 4]},
  3: {0:[], 1:[], 2:[], 3:[], 4:[]},
  4: {0:[], 1:[], 2:[], 3:[], 4:[]}
}

class SOList:
  def __init__(self, auth, luid):
    self.auth, self.luid = auth, luid

    if not luid:
      self.createList()
      self.auth.sql.reconnect()

    self.reload()

  def reload(self):
    self.auth.sql.reconnect()

    rights = self.auth.sql.getDataDicts('rights', where = f"luid = '{self.luid}' AND uuid = '{self.auth.userDict['uuid']}'")
    self.rights = rights[0] if rights else None
    solst = self.auth.sql.getOneDataDict('lists', 'luid', self.luid)
    self.active = solst['active']
    if not solst:
      self.active = self.rights = self.dat = self.aes = None
      return None

    self.aes = self.auth.keyring.decrypt(self.rights['aes'])
    if not self.aes:
      self.active = self.rights = self.dat = self.aes = None
      return None

    self.dat = tf.bj(solst['dat'], self.aes)
    if not self.dat:
      self.active = self.rights = self.dat = self.aes = None
      return None

  def selection(self, select = True):

    self.auth.sql.wesc('UPDATE rights SET disp* WHERE uuid* AND luid*', v = [(select, self.auth.userDict['uuid'], self.luid)])

    return True

  def vueList(self, summary = False):

    retval = {
      'admin': self.rights['priv'],
      'list': {
        'luid': self.luid,
        'dat': self.dat,
        'active': self.active
      }
    }

    if summary:
      return retval

    return {**retval,
      'patients': self.vuePatients(),
      'rights': self.vueRights()
    }

  def vueRights(self):
    if not self.rights['priv'] in [1, 2]:
      return []

    query = self.auth.sql.fetch(
      f"SELECT uuid, email, dat, ("
      f"  SELECT priv FROM rights WHERE luid = '{self.luid}' AND rights.uuid = users.uuid"
      f") FROM users WHERE uuid in ("
      f"  SELECT uuid FROM rights WHERE luid = '{self.luid}' AND priv != 0"
      f") AND !ISNULL(priv)"
    )
    retval = [dict(zip(['uuid', 'email', 'dat', 'priv'], x)) for x in query]
    return [{**x, 'dat': tf.bj(x['dat'])} for x in retval]

  def vuePatients(self):
    return []


  def updateList(self, newDat = None, newActive = None):

    self.auth.sql.replaceRows('lists', {
      'luid': self.luid,
      'dat': tf.jb(newDat if newDat else self.dat, self.aes),
      'active': newActive if newActive else self.active
    })

    self.reload()


  def createList(self):

    self.luid = tf.getUUID()
    self.aes = En()._rnd(32)

    self.shareList(1, uuids = [self.auth.userDict['uuid']], first = True)
    self.updateList(
      newDat = {
        'name': f"My new list {self.luid}",
        'cols': []
      },
      newActive = 1
    )

    # add empty col
    self.updateCol()

    # check if one list displayed else display this one
    if not self.auth.sql.fetch(f"SELECT luid FROM lists WHERE luid IN (SELECT luid FROM rights WHERE uuid = '{self.auth.userDict['uuid']}' AND disp = 1) AND active = 1"):
      self.auth.sql.wesc('UPDATE rights SET disp* WHERE uuid* AND luid*', v = [(True, self.auth.userDict['uuid'], self.luid)])



  def updateCol(self, dat = None):
    # new col requested
    newDat = {k: v for k, v in self.dat.items()}
    if not dat:
      newDat['cols'].append({'type': 0, 'title': '(none)', 'active': True, 'width': 200, 'cuid': tf.getUUID()})
    else:
      newDat['cols'][af.kmap(newDat['cols'], 'cuid').index(dat['cuid'])].update(dat)



    self.updateList(newDat = newDat)
    return True


  def unitAction(self, action, dat):
    what = action.split('-')[1]

    newDat = {k: v for k, v in self.dat.items()}
    colIndex = af.kmap(newDat['cols'], 'cuid').index(dat['cuid'])


    if what in ['keyboard_arrow_up', 'keyboard_arrow_down']:
      colCopy = newDat['cols'][colIndex]
      newDat['cols'].pop(colIndex)
      newIndex = colIndex + {'keyboard_arrow_up': -1, 'keyboard_arrow_down': 1}.get(what)
      if not len(newDat['cols']) > newIndex > -1:
        return False
      newDat['cols'].insert(newIndex, colCopy)

    if what in ['toggle_on', 'toggle_off']:
      newDat['cols'][colIndex]['active'] = {'toggle_on': True, 'toggle_off': False}.get(what)

    # inactive at the end
    newDat['cols'] = af.flst([[colA for colA in newDat['cols'] if colA['active']], [colI for colI in newDat['cols'] if not colI['active']]])

    self.updateList(newDat = newDat)




  def deleteRights(self, uluids):
    self.auth.sql.deleteCond('rights', condition = ' OR '.join([f"(uuid = '{uuid}' AND luid = '{luid}')" for uuid, luid in af.iwList(uluids)]))


  def shareList(self, priv, emails = None, uuids = None, first = False):
    if False if first else not self.rights.get('priv'):
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
      self.auth.sql.wesc(
        f"DELETE FROM rights WHERE uuid* AND luid*",
        v = (self.auth.userDict['uuid'], self.luid)
      )

      rightsDict = {
        'luid': self.luid,
        'uuid': self.auth.userDict['uuid'],
        'priv': priv,
        'aes': self.auth.keyring.encrypt(self.aes, forceSealedBox = True)
      }

      # TODO: this?
      self.auth.sql.wesc(f"INSERT INTO rights **", d = rightsDict)

    if first:
      return uuids

    # possible uuids ie where emails match and not self user's uuid
    uuidsPossible = list(set(uuids) - {self.auth.userDict['uuid']})

    allowedPrivs = PRIVS.get(self.rights.get('priv'))

    # where statement for privileges when priv would be allowed
    uuidsAllowedWheres = ' OR '.join([f"priv = {k}" for k, v in allowedPrivs.items() if priv in v])
    # uuids in rights table for this list where priv prevents Δ
    uuidsProhibited = self.auth.sql.getOneCol('rights', 'uuid', where = f"luid = '{self.luid}' AND NOT ({uuidsAllowedWheres})")
    # to-do list ie possible minus prohibited
    uuidsToDo = list(set(uuidsPossible) - set(uuidsProhibited))
    if not uuidsToDo:
      return []

    self.deleteRights([(uuid, self.luid) for uuid in uuidsToDo])
    self.auth.sql.replaceRows('rights', [{
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


















