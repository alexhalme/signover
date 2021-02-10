import nacl from 'tweetnacl'
import naclUtil from 'tweetnacl-util'
import * as scryptPbkdf from 'scrypt-pbkdf'
import * as crypto from 'crypto'

// JSON --> b64 mostly for addending to endpoints
export function obj2b64 (someObject) {
  var ezNaCl = new EzNaClWrapper()
  return ezNaCl.uintBase64(ezNaCl.strUint(JSON.stringify(someObject)))
}

// Wrapper around a few JS crypto libraries (tweetnacl, tweetnacl-util, pbkdf2)
export class EzNaClWrapper {
  // encrypt ed25519 for sending to server
  encryptToServer (serverPublicKeyb64, whatToSendb64) {
    // var ephemeralKeyPair = nacl.box.keyPair()
    // nacl.box(message, nonce, theirPublicKey, mySecretKey)
    var ephemeralKeyPair = {
      publicKey: this.base64Uint('UAooj5YjRCUQUvPeMtMF2QWkUwi/ZwuFQe7jx3feBmQ='),
      secretKey: this.base64Uint('DQtuM4QT/GawwoSNJA8Jf1rsMPvE/mkGiOTzIbawdqU=')
    }
    var nonce = this.base64Uint('wu7wO6yWrytDKwU5r9ERRbiJpzgP8eBT') // nacl.randomBytes(24)
    var encryptedBox = nacl.box(
      this.base64Uint(whatToSendb64),
      nonce,
      this.base64Uint(serverPublicKeyb64),
      ephemeralKeyPair.secretKey
    )
    const fullEncryptedBox = new Uint8Array(nonce.length + encryptedBox.length)
    fullEncryptedBox.set(nonce)
    fullEncryptedBox.set(encryptedBox, nonce.length)
    var fullEncryptedBoxb64 = this.uintBase64(fullEncryptedBox)
    return fullEncryptedBoxb64
  }

  strBuf (ezStr) {
    return Buffer.from(naclUtil.decodeUTF8(ezStr))
  }

  uintHex (ezUint) {
    return Buffer.from(ezUint).toString('hex')
  }

  rndBytes (n) {
    return nacl.randomBytes(n)
  }

  rndb64 (n) {
    return this.uintBase64(nacl.randomBytes(n))
  }

  // Simple converters
  strUint (ezStr) {
    // string to uint8
    return naclUtil.decodeUTF8(ezStr)
  }

  uintStr (ezUint) {
    // uint to string (this can bug if bytes are illegal)
    return naclUtil.encodeUTF8(ezUint)
  }

  base64Uint (ezBase64) {
    // base64 (as string) to uint
    return naclUtil.decodeBase64(ezBase64)
  }

  uintBase64 (ezUint) {
    // uint to base64 string
    return naclUtil.encodeBase64(ezUint)
  }

  // Crypto functions
  sha512 (ezUint) {
    // sha512 hash uint8 → uint8
    return nacl.hash(ezUint)
  }

  mergeUint (ezUint0, ezUint1) {
    // concatenates 2 uint8 arrays
    // TODO: concatenate N arrays
    var retval = new Uint8Array(ezUint0.length + ezUint1.length)
    retval.set(ezUint0)
    retval.set(ezUint1, ezUint0.length)
    return retval
  }

  // Python equivalent
  //   from Crypto.Protocol.KDF import PBKDF2
  //   from Crypto.Hash import SHA512
  //   PBKDF2(string_for_password, string_for_salt, keyLenght, nIterations, hmac_hash_modules=SHA512)
  pbkdf2SHA512 (b64Pwrd, b64Salt, keyLength, nIterations) {
    var key = crypto.pbkdf2Sync(b64Pwrd, b64Salt, nIterations, keyLength, 'sha512')
    return key
  }

  // Python equivalent BYTES
  //   from Crypto.Protocol.KDF import PBKDF2
  //   from Crypto.Hash import SHA512
  //   PBKDF2(string_for_password, string_for_salt, keyLenght, nIterations, hmac_hash_modules=SHA512)
  pbkdf2SHA512bytes (b64Pwrd, b64Salt, keyLength, nIterations) {
    var key = crypto.pbkdf2Sync(this.base64Uint(b64Pwrd), this.base64Uint(b64Salt), nIterations, keyLength, 'sha512')
    return key
  }

  async strPwrdB64SaltPBKDF (strPwrd, b64Salt, keyLength, scryptParams) {
    var key = await scryptPbkdf.scrypt(this.uintBase64(this.sha512(this.strUint(strPwrd))), this.base64Uint(b64Salt), keyLength, scryptParams)
    var key8 = new Uint8Array(key)
    return key8
  }
}

export function ezHash (ezStr, n) {
  if (ezStr === '') {
    return ''
  }
  var ezNaCl = new EzNaClWrapper()
  var hash = ezNaCl.strUint(ezStr)
  for (var i of Array(n).keys()) {
    hash = ezNaCl.sha512(hash)
    if (ezStr === '') {
      ezStr = i
    }
  }
  return ezNaCl.uintBase64(hash)
}
