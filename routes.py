import _clibash
import uvicorn
from fastapi import FastAPI, Header, Cookie, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse, FileResponse, RedirectResponse, Response
from typing import Optional
import json
import starlette
import locaf as af
from locaf import En
import authso
import wsql
import sys
import requests
import gv
import httpx
import lists
import re

app = FastAPI()
#app.mount('/app', StaticFiles(directory = af.path('front/dist/spa')), name = 'static')
app.mount('/app', app)

app.add_middleware(
  CORSMiddleware,
  allow_origins = ['http://localhost:5007', 'https://localhost:8082', 'https://so.alexhal.me'],
  allow_credentials = True,
  allow_methods = ['*'],
  allow_headers = ['*']
)

# TODO: USE 127.0.0.1:5007 in browser *NOT* localhost *NOT* 8082 port -> cookie issues





def closeAjax(obj, what = None, noCookie = False):
  wsql.WSQL.closeAll()

  if hasattr(obj, 'response'):
    retval = obj.responseType(obj.response)
  else:
    retval = what(obj)

  if noCookie:
    retval.delete_cookie(key = 'scso')
    return retval

  if False if not (hasattr(obj, 'cookieIn') and hasattr(obj, 'cookieOut')) else (not obj.cookieIn == obj.cookieOut and bool(obj.cookieOut)):
    retval.set_cookie(
      key='scso',
      value=obj.cookieOut,
      samesite = 'strict',
      httponly=True,
      max_age=gv.COOKIE.MAX
    )

  return retval

# TODO: temporary
@app.get('/wipe/{something}')
def wipe(something):
  sql = wsql.WSQL(*gv.SQL_CRED)
  for letter in something:
    table = {'l': 'lists', 'r': 'rights', 'u': 'users', 'p': 'patients'}
    sql.deleteCond(table.get(letter), condition = 'TRUE')

  wsql.WSQL.closeAll()
  return JSONResponse({'wiped': True})



# cancel a pwrd change request
@app.get('/cancel/{cancelKeyb58}')
def cancel(cancelKeyb58):
  # convert url end to bytes, extract uuid (bytes 0-16) and cancel key (rest)
  cancelKeyBytes = En(cancelKeyb58)._by58()
  uuid, cancelKey = authso.AuthSo.ioUUID(cancelKeyBytes[0:16]), cancelKeyBytes[16:]

  # ensure uuid is valid - avoid SQL injections
  if not re.fullmatch(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', uuid):
    return {'success': False}

  # SQL obj to fetch user dict
  gsql = authso.GSQLBridge()
  query = gsql.SQL.fetch(f"SELECT nextkeys FROM users WHERE uuid = '{uuid}'")
  if True if not query else not query[0][0]:
    return {'success': False}

  # extract from 'nextkeys' the hashed cancelKey; seq of nextkeys is nix ts (4 bytes), hashed cancel key (32 bytes),
  # public key (32 bytes), encrypted private key (rest, usually 144 bytes)
  _, cancelKeyHashed, _ = query[0][0][0:4], query[0][0][4:36], query[0][0][36:]

  # ensure key provided once hashed matches the hash
  if not cancelKeyHashed == En(cancelKey)._sha256():
    return {'success': False}

  # remove the request
  gsql.SQL.wesc(f"UPDATE users SET nextkeys* WHERE uuid = '{uuid}'", v = [(None,)])
  return {'success': True}



@app.get('/{path:path}')
async def tile_request(path: str, response: Response):
  async with httpx.AsyncClient() as client:
    proxy = await client.get(f'http://127.0.0.1:8082/{path}')
  response.body = proxy.content
  response.status_code = proxy.status_code
  return response

# login
class Login(BaseModel):
  email: str
  pbkdf2b64: dict
  type: str
  newhash: Optional[str] = None

@app.post('/login')
def doLogin(login: Login, req: Request, scso: Optional[str] = Cookie(None)):
  auth = authso.AuthSo(email = login.email, req = req, cookie = scso)
  if login.pbkdf2b64:
    cookie = auth.getCookie(login)
    return closeAjax(auth.setResponse({'challenge': auth.getChallenge(), 'cookie': cookie}), noCookie = not cookie)

  if login.email:
    if login.type == 'standard':
      return closeAjax(auth.setResponse({'challenge': auth.getChallenge()}))

    # reset pwrd requested
    auth.requestPwrdReset(auth.userDict['uuid'], newAccount=False)
    return closeAjax(auth.setResponse({'challenge': False, 'type': 'forgot'}))

  return closeAjax(auth.killSession(), noCookie=True)

# init after login/reload
@app.post('/init')
def doInit(req: Request, scso: Optional[str] = Cookie(None)):
  auth = authso.AuthSo(cookie = scso, req = req)
  if not auth.priv:
    return closeAjax(auth.setResponse({'success': False}), noCookie = True)

  auth.setLists()
  auth.setSelf()

  return closeAjax(auth.setResponse({'success': True}))


# list actions
class Solst(BaseModel):
  # new, deactivate, activate, alter
  action: str
  luid: str
  dat: Optional[dict] = None

@app.post('/solst')
def modifySolsts(solst: Solst, req: Request, scso: Optional[str] = Cookie(None)):
  auth = authso.AuthSo(cookie=scso, req=req)

  lst = lists.SOList(auth, solst.luid)

  if solst.action in ['select', 'deselect']:
    lst.selection(solst.action == 'select')

  for action, kwargs in {
      'new': [('setLists', {'summary': True})],
      'select': [('setLists', {'summary': False})],
      'deselect': [('setLists', {'summary': False})]
      }.get(solst.action):
    getattr(auth, action)(**(kwargs if kwargs else {}))

  return closeAjax(auth.setResponse({}))



class Cols(BaseModel):
  action: str
  luid: str
  dat: Optional[dict] = None


@app.post('/cols')
def modifyCols(cols: Cols, req: Request, scso: Optional[str] = Cookie(None)):
  auth = authso.AuthSo(cookie=scso, req=req)
  if not auth.priv:
    return closeAjax(auth.setResponse({'success': False}), noCookie = True)


  lst = lists.SOList(auth, cols.luid)

  # seems like a cross-site forgery
  if False if cols.action == 'new' else not cols.dat['cuid'] in af.kmap(lst.dat['cols'], 'cuid'):
    closeAjax(auth.setResponse({'success': False}), noCookie=True)

  if cols.action in ['new', 'edit']:
    lst.updateCol(dat = cols.dat if hasattr(cols, 'dat') else None)

  if re.fullmatch(r'^unitaction-[a-z_]+$', cols.action):
    lst.unitAction(cols.action, cols.dat)

  for action, kwargs in {
      'new': [('setLists', {'summary': False, 'specific': cols.luid})],
      'edit': [('setLists', {'summary': False, 'specific': cols.luid})],
      'unitaction': [('setLists', {'summary': False, 'specific': cols.luid})]
      }.get(cols.action.split('-')[0]):
    getattr(auth, action)(**(kwargs if kwargs else {}))

  return closeAjax(auth.setResponse({}))










class Rights(BaseModel):
  action: str
  luid: str
  # list of { email: <email>, priv: <priv> }
  dat: dict

@app.post('/rights')
def modifyCols(rights: Rights, req: Request, scso: Optional[str] = Cookie(None)):
  auth = authso.AuthSo(cookie=scso, req=req)
  if not auth.priv:
    return closeAjax(auth.setResponse({'success': False}), noCookie = True)

  lst = lists.SOList(auth, rights.luid)

  uuid = rights.dat.get('uuid')

  if rights.action == 'new':
    uuid = auth.addUser(rights.dat['email'])
    rights.dat.update({'uuid': uuid, 'priv': 4})


  lst.shareList(rights.dat.get('priv'), uuids = [rights.dat.get('uuid')])


  auth.setLists(summary = False, specific = lst.luid)

  return closeAjax(auth.setResponse({}))
























if __name__ == '__main__':
  uvicorn.run(app, host='127.0.0.1', port=5007)