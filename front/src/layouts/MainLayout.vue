<template>
  <q-layout view="lHh Lpr lFf">
    <notification/>
    <q-header>
      <topbar
        v-model="logged"
        :user="user"
        :server="server"
        @init="init"
        @logout="logout"
      />
    </q-header>

    <q-drawer
      v-model="drawer"
      show-if-above
      bordered
      content-class="bg-grey-1"
    >
      <q-list>
        <q-item-label
          header
          class="text-grey-8"
        >
          Essential Links
        </q-item-label>
      </q-list>
    </q-drawer>

    <q-page-container>
      {{logged}}
    </q-page-container>
  </q-layout>
</template>

<script>
import Topbar from 'components/Topbar.vue'
import Notification from 'components/Notification.vue'
import EventBus from 'assets/eventbus.js'
import InitData from 'assets/initdata.js'
import $ from 'jquery'

const serverKeysToData = ['user', 'slists', 'dlists']

export default {
  name: 'MainLayout',
  components: { Topbar, Notification },
  data () {
    return InitData()
  },
  computed: {
    server () {
      // temporary --> to put back in initdata.js when done
      return /8082|5007/.test(window.location) ? 'http://127.0.0.1:5007' : 'https://so.alexhal.me'
    }
  },
  methods: {
    // logout initiated by TopBar - here we adjust variables
    logout () {
      Object.assign(this, InitData())
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
        for (var key in server) {
          if (serverKeysToData.indexOf(key) + 1) {
            this[key] = server[key]
          }
        }
      }).fail(() => {
        EventBus.$emit('notify', ['There was a connection problem with the server'], 'red-6', 2)
      })
    }
  }
}
</script>
