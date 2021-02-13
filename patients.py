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
import lists
import authso

class Pt:
  def __init__(self, auth, puid, luid = None, skipRights = False):
    self.auth, self.puid, self.skipRights = auth, puid, skipRights


    # no puid -> create pt
    if not self.puid:
      # rights for list
      self.luid = luid
      self.getRights()

      if not self.canEdit:
        return None

      self.newPt(luid)

    else:
      pt = self.auth.sql.getOneDataDict('pts', 'puid', self.puid)
      if not pt:
        return None
      self.puid, self.luid, self.active = [pt[k] for k in ['puid', 'luid', 'active']]
      if False if not luid else not self.luid == luid:
        return None
      self.getRights()
      self.list = lists.SOList(self.auth, self.luid)
      self.dat, self.hx = [tf.bj(pt[k], self.list.aes) for k in ['dat', 'hx']]

  def getRights(self):
    if self.skipRights:
      self.rights, self.canEdit = 1, True
      return True

    rights = self.auth.sql.fetch( f"SELECT priv FROM rights WHERE luid = '{self.luid}' AND uuid = '{self.auth.userDict['uuid']}'")
    if True if not rights else not rights[0][0] in [1, 2, 3, 4]:
      self.rights = False
      return False

    self.rights = rights[0][0]
    self.canEdit = {1: True, 2: True, 3: True, 4: False}.get(self.rights)


  def vuePt(self, history = False):
    retval = {k: getattr(self, k) for k in ['puid', 'luid', 'dat', 'active']}
    if not history:
      retval['dat'] = {k: v[0] for k, v in retval['dat'].items()}
    return retval


  def newPt(self, luid):
    self.luid = luid
    self.list = lists.SOList(self.auth, luid)
    self.puid = tf.getUUID()
    self.dat = {
      'baseline': [{'name': 'new', 'surname': 'patient', 'mrn': '', 'insurance': '', 'dob': '', 'age': '', 'gender': '', 'room': '', 'admit': af.mytime(time.time(), 1), 'info': ''}]
    }
    self.hx = {}
    self.active = 1

    self.savePt()



  def savePt(self):
    self.auth.sql.replaceRows('pts', {
      'puid': self.puid,
      'luid': self.luid,
      'dat': tf.jb(self.dat, self.list.aes),
      'hx': tf.jb(self.hx, self.list.aes),
      'active': self.active
    })
    self.auth.sql.reconnect()


