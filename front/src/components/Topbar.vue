<template>
  <div class="row no-wrap">
    <q-dialog
      v-if="['standard', 'forgot'].indexOf(modalSituation) === -1"
      v-model="credDialog"
    >
      <q-card class="q-pa-md">
        <div class="row no-wrap">
          <div class="col-auto q-pr-sm">
            <q-icon :name="modalText[modalSituation].icon" size="lg" />
          </div>
          <q-separator vertical />
          <div class="col q-pl-sm text-h6">
            <div class="row">
            {{ modalText[modalSituation].title }}
            </div>
            <div class="row text-body2">
            {{ modalText[modalSituation].text }}
            </div>
          </div>
        </div>
        <div class="row no-wrap">
          <div class="col-auto q-px-sm">
            <span class="row no-wrap q-py-md"> Email address: </span>
            <span class="row no-wrap"> Passwords: </span>
          </div>
          <div class="col q-px-sm">
            <span class="row no-wrap q-py-md"> {{ email }} </span>
            <q-input outlined dense type="password" label="Current password" class="row no-wrap q-py-xs"
              v-if="modalText[modalSituation].input0"
              v-model="pwrdCurrent"
            />
            <q-input outlined dense type="password" label="New password" class="row no-wrap q-py-xs"
              v-if="modalText[modalSituation].input12"
              v-model="pwrdNew[0]"
            />
            <q-input outlined dense type="password" label="New password" class="row no-wrap q-py-xs"
              v-if="modalText[modalSituation].input12"
              v-model="pwrdNew[1]"
            />
          </div>
        </div>
        <div class="row no-wrap q-mt-md">
          <div class="col">
            <div class="float-right">
              <q-btn dense
                v-for="btn in modalText[modalSituation].btn"
                :class="`q-mx-sm ${btn[1]}`"
                :label="btn[0]"
                :key="btn[0]"
                :disable="btnDisabler(btn[0])"
                @click="pwrdLogin(btn[0])"
              />
            </div>
          </div>
        </div>
      </q-card>
    </q-dialog>
    <q-toolbar class="col-4 bg-blue-6">
      <q-btn icon="menu" dense
        @click="$emit('drawerState')"
      />
      <q-icon name="delete_sweep" size="md" :color="temp" v-if="temp" />
      <q-btn flat dense round size="md"
        v-for="letter in ['lr', 'l', 'r', 'u', 'p']"
        :label="letter" :key="letter"
        :color="letter === 'lr' ? temp : 'white'"
        @click="wipe(letter)"
      />
    </q-toolbar>
    <q-toolbar class="col bg-grey-3">
      <q-item-label color="primary" overline class="q-pl-md q-pr-xs">
        {{logged ? 'LOGGED AS' : 'LOGIN'}}
      </q-item-label>
      <div v-if="logged">
        <q-badge class="q-ml-sm" color="dark" size='lg' style='height: 25px;'>
          <q-icon name="person"/>
          {{user.dat.name}}
        </q-badge>
      </div>
      <div class="row no-wrap" v-else>
        <q-input outlined dense label="Email address" class="q-px-xs"
          v-model="email"
        />
        <q-input outlined dense type="password" label="Password" class="q-px-xs"
          v-model="pwrdCurrent"
        />
      </div>
      <q-btn :icon="logged ? 'logout' : 'login'" dense flat class="q-ml-md"
        color="grey-8"
        @click="logClick(!logged)"
      />
      <q-space />
      <q-btn v-if="!logged" dense flat class="q-ml-md"
        color="grey-8"
        label="password forgotten"
        @click="modalSituation = 'forgot'; logClick(true)"
      />
    </q-toolbar>
  </div>
</template>
<script>
import { EzNaClWrapper, ezHash } from '../assets/cryptoso'
import { EventBus } from 'assets/vuecommon.js'
import { ModalText } from 'assets/initdata.js'
import $ from 'jquery'

export default {
  name: 'Topbar',
  props: {
    logged: {
      type: Boolean,
      required: false,
      default () { return false }
    },
    user: {
      type: Object,
      required: false,
      default () { return {} }
    }
  },
  model: {
    prop: 'logged',
    event: 'logchange'
  },
  data () {
    return {
      email: '',
      pwrdCurrent: '',
      pwrdNew: ['', ''],
      credDialog: true,
      modalSituation: 'standard',
      modalText: ModalText(),
      temp: this.randomColor()
    }
  },
  created () {
    // temporary
    if (/8082|5007/.test(window.location)) {
      var TRUE = true
      if (TRUE) {
        this.email = 'alex@alexhal.me'
        this.pwrdCurrent = 'abc123'
      } else {
        this.email = 'maizlyn.rosi@twodrops.org'
        // this.pwrdCurrent = 'AY9MMFhWKre'
      }
    }
  },
  updated () {
    // temporary
    if (/8082|5007/.test(window.location)) {
      var TRUE = true
      if (TRUE) {
        this.email = 'alex@alexhal.me'
        this.pwrdCurrent = 'abc123'
      } else {
        this.email = 'maizlyn.rosi@twodrops.org'
        // this.pwrdCurrent = 'AY9MMFhWKre'
      }
    }
  },
  computed: {
    server () {
      return this.$store.state.server
    }
  },
  methods: {
    // temporary for testing
    randomColor () {
      return `${['red', 'pink', 'purple', 'deep-purple', 'indigo', 'blue', 'light-blue', 'cyan', 'teal', 'green', 'orange', 'yellow', 'lime', 'brown', 'grey'][Math.floor(Math.random() * 15)]}-${Math.floor(Math.random() * 14)}`
    },
    wipe (letters) {
      this.temp = false
      $.ajax({
        type: 'get',
        url: `${this.server}/wipe/${letters}`
      }).done(() => {
        this.temp = this.randomColor()
      })
    },
    // button disable on modal
    btnDisabler (btnLabel) {
      var pwrdCheck = this.pwrdCheck()
      switch (btnLabel) {
        case 'reset':
          return !pwrdCheck[1]
        case 'login':
          switch (this.modalSituation) {
            case 'cookie':
              return !pwrdCheck[0]
            default:
              return !pwrdCheck[1]
          }
        default:
          return false
      }
    },
    // standard password check for change
    pwrdCheck () {
      return [
        this.pwrdCurrent !== this.pwrdNew[0] && this.pwrdCurrent.length > 5,
        this.pwrdCurrent !== this.pwrdNew[0] && this.pwrdCurrent.length > 5 && this.pwrdNew[0] === this.pwrdNew[1] && this.pwrdNew[0].length > 5
      ]
    },
    pwrdLogin (btnType) {
      switch (btnType) {
        case 'cancel':
          this.pwrdCurrent = ''
          this.pwrdNew = ['', '']
          this.modalSituation = 'standard'
          break
        case 'abord password reset':
          this.pwrdNew = ['', '']
          this.modalSituation = 'standard'
          break
        case 'logout':
          this.logout()
          break
        default:
          this.logClick(true)
      }
    },
    logout () {

    },
    logLoop (server) {
      if (server) {
        const ezNaCl = new EzNaClWrapper()

        // no such user
        if (server.step === -1) {
          EventBus.$emit('notify', ['This username dose not exist'], 'red-6', 2)
          this.pwrdCurrent = ''
          this.email = ''
          return null
        }

        var uintPBKDF2 = {}
        for (var key in server.challenge) {
          uintPBKDF2[key] = ezNaCl.uintBase64(
            ezNaCl.pbkdf2SHA512bytes(
              ezNaCl.uintBase64(ezNaCl.sha512(ezNaCl.strUint(this.pwrdCurrent))), server.challenge[key], 32, 100
            )
          )
        }

        if (server.step) {
          this.modalSituation = server.type

          // if pwrd change request to email
          if (!server.challenge && this.modalSituation === 'forgot') {
            this.modalSituation = 'standard'
            this.pwrdCurrent = ''
            EventBus.$emit('notify', ['An email was sent to your address to reset the password'], 'green-6', 2)
            return null
          }

          if (this.modalSituation === 'passwordchanged') {
            this.modalSituation = 'standard'
            this.pwrdCurrent = ''
            this.pwrdNew = ['', '']
            EventBus.$emit('notify', ['Password change successful, please login'], 'green-6', 2)
            return null
          }

          if (!server.cookie) {
            this.modalSituation = server.type
            if (server.type === 'standard') {
              EventBus.$emit('notify', ['Authentication failed'], 'red-6', 2)
            }
            return null
          } else {
            var nextPbkdf2 = '' // ezNaCl.uintBase64(ezNaCl.pbkdf2SHA512bytes(ezNaCl.uintBase64(ezNaCl.sha512(ezNaCl.strUint(this.pwrdCurrent))), server.challenge, 32, 100))
            // this.pwrdCurrent = ''
            this.$emit('init', nextPbkdf2)
            return null
          }
        }

        // if new hash re pwrd changed
        var newHash = this.pwrdNew[0].length > 0 && this.pwrdNew[0] === this.pwrdNew[1] ? ezHash(this.pwrdNew[0]) : ''

        $.ajax({
          dataType: 'json',
          type: 'post',
          url: `${this.server}/login`,
          data: JSON.stringify({ email: this.email, pbkdf2b64: uintPBKDF2, type: this.modalSituation, newhash: newHash })
        }).done((server) => {
          this.logLoop(server)
        }).fail(() => {
          EventBus.$emit('notify', ['There was a connection problem with the server'], 'red-6', 2)
        })
      }
    },
    logClick (inOut) {
      if (!this.modalSituation && this.modalSituation !== '') {
        this.modalSituation = 'standard'
      }
      if (inOut) {
        $.ajax({
          dataType: 'json',
          type: 'post',
          url: `${this.server}/login`,
          data: JSON.stringify({ email: this.email, pbkdf2b64: {}, type: this.modalSituation })
        }).done((server) => {
          this.logLoop(server)
        }).fail(() => {
          EventBus.$emit('notify', ['There was a connection problem with the server'], 'red-6', 2)
        })
      } else {
        // logs out
        $.ajax({
          dataType: 'json',
          type: 'post',
          url: `${this.server}/login`,
          data: JSON.stringify({ email: '', pbkdf2b64: '' })
        })
        this.$emit('logout')
      }
    },
    logStatus (status) {
      this.$emit('input', status)
    }
  }
}
</script>
