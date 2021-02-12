<template>
  <q-layout view="lHh Lpr lFf">
    <notification/>
    <q-header>
      <topbar
        v-model="logged"
        :user="user"
        @init="init"
        @logout="logout"
      />
    </q-header>

    <drawer
      v-if="logged"
      v-model="solst"
      :user="user"
    />

    <q-page-container>
      {{server}}
      {{user}} <br> <br>
      {{solst.slists}} <br> <br>
      {{solst.dlists}}
    </q-page-container>
  </q-layout>
</template>

<script>
import Topbar from 'components/Topbar.vue'
import Notification from 'components/Notification.vue'
import Drawer from 'components/Drawer.vue'
import { EventBus, Store } from 'assets/vuecommon.js'
import { InitData } from 'assets/initdata.js'
import $ from 'jquery'

const serverKeysToData = ['user', 'slists', 'dlists']

export default {
  name: 'MainLayout',
  components: { Topbar, Notification, Drawer },
  store: Store,
  data () {
    return InitData()
  },
  computed: {
    server () {
      // temporary --> to put back in initdata.js when done
      // return /8082|5007/.test(window.location) ? 'http://127.0.0.1:5007' : 'https://so.alexhal.me'
      return this.$store.state.server
    }
  },
  created () {
    this.$store.commit('changeServerURL', /8082|5007/.test(window.location) ? 'http://127.0.0.1:5007' : 'https://so.alexhal.me')
  },
  methods: {
    // logout initiated by TopBar - here we adjust variables
    logout () {
      Object.assign(this, InitData())
    },

    // from a JSON returned by server, parse keys to assign to data () appropriately
    parseServerJSONs (server) {
      for (var key in server) {
        if (serverKeysToData.indexOf(key) + 1) {
          if (['dlists', 'slists'].indexOf(key) + 1) {
            this.solst[key] = server[key]
          } else {
            this[key] = server[key]
          }
        }
      }
    },

    // init reception of bunch of stuff by server
    init (nextPbkdf2) {
      // backup in case of disconnection
      if (nextPbkdf2) {
        this.nextPbkdf2 = nextPbkdf2
      }

      $.ajax({
        dataType: 'json',
        type: 'post',
        url: `${this.server}/init`
      }).done((server) => {
        this.logged = this.logged ? true : server.success
        this.parseServerJSONs(server)
      }).fail(() => {
        EventBus.$emit('notify', ['There was a connection problem with the server'], 'red-6', 2)
      })
    }
  }
}
</script>
