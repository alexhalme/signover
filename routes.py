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
  pbkdf2b64: str

@app.post('/login')
def doLogin(login: Login, req: Request, scso: Optional[str] = Cookie(None)):
  auth = authso.AuthSo(email = login.email, req = req, cookie = scso)
  if login.pbkdf2b64:
    cookie = auth.getCookie(login.pbkdf2b64)
    return closeAjax(auth.setResponse({'challenge': auth.getChallenge(), 'cookie': cookie}), noCookie = not cookie)

  if login.email:
    return closeAjax(auth.setResponse({'challenge': auth.getChallenge()}))

  return closeAjax(auth.setResponse({}), noCookie=True)

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





class Rights(BaseModel):
  luid: str
  # list of { email: <email>, priv: <priv> }
  priv: list

























if __name__ == '__main__':
  uvicorn.run(app, host='127.0.0.1', port=5007)