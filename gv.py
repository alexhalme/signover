import _clibash
import locaf as af

SQL_CRED = ('localhost', 'signout', af.iob('sqlpassword.txt').decode('utf8'), 'signout')

COOKIE = af.MakeObj({
  'MAX': 800,
  'WARN': 500
})