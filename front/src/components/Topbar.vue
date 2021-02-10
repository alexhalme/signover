<template>
  <div class="row no-wrap">
    <q-toolbar class="col-4 bg-blue-6">
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
          v-model="password"
        />
      </div>
      <q-btn :icon="logged ? 'logout' : 'login'" dense flat class="q-ml-md"
        color="grey-8"
        @click="logClick(!logged)"
      />
    </q-toolbar>
  </div>
</template>
<script>
import { EzNaClWrapper } from '../assets/cryptoso'
import EventBus from '../assets/eventbus.js'
import $ from 'jquery'

export default {
  name: 'Topbar',
  props: {
    logged: {
      type: Boolean,
      required: false,
      default () { return false }
    },
    server: {
      type: String,
      required: false,
      default () { return '' }
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
      password: '',
      bustest: 'zz'
    }
  },
  created () {
    EventBus.$on('from-mainlayout', (arg) => {
      this.bustest = arg
    })
    // temporary
    if (/8082|5007/.test(window.location)) {
      this.email = 'alex@alexhal.me'
      this.password = 'DpPAnp1Vg9F'
    }
  },
  updated () {
    // temporary
    if (/8082|5007/.test(window.location)) {
      this.email = 'alex@alexhal.me'
      this.password = 'DpPAnp1Vg9F'
    }
  },
  methods: {
    logClick (inOut) {
      if (inOut) {
        const ezNaCl = new EzNaClWrapper()
        $.ajax({
          dataType: 'json',
          type: 'post',
          url: `${this.server}/login`,
          data: JSON.stringify({ email: this.email, pbkdf2b64: '' })
        }).done((server) => {
          if (server) {
            var uintPBKDF2 = ezNaCl.pbkdf2SHA512bytes(
              ezNaCl.uintBase64(ezNaCl.sha512(ezNaCl.strUint(this.password))), server.challenge, 32, 100
            )

            $.ajax({
              dataType: 'json',
              type: 'post',
              url: `${this.server}/login`,
              data: JSON.stringify({ email: this.email, pbkdf2b64: ezNaCl.uintBase64(uintPBKDF2) })
            }).done((server) => {
              if (!server.cookie) {
                EventBus.$emit('notify', ['Authentication failed'], 'red-6', 2)
              } else {
                var nextPbkdf2 = ezNaCl.uintBase64(ezNaCl.pbkdf2SHA512bytes(ezNaCl.uintBase64(ezNaCl.sha512(ezNaCl.strUint(this.password))), server.challenge, 32, 100))
                // this.password = ''
                this.$emit('init', nextPbkdf2)
              }
            }).fail(() => {
              EventBus.$emit('notify', ['There was a connection problem with the server'], 'red-6', 2)
            })
          }
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
