<template>
  <q-layout view="lHh Lpr lFf">
    <notification/>
    <q-header>
      <topbar
        v-model="logged"
        :user="user"
        @init="init"
        @logout="logout"
        @drawerState="showDrawer = !showDrawer && logged"
      />
    </q-header>

    <drawer
      v-if="logged && showDrawer"
      v-model="solst"
      :user="user"
    />

    <q-page-container>
      <div v-if="logged">
        <div v-for="dlist in solst.dlists" :key="dlist.list.luid">
          <div class="row no-wrap">
            <ptable
              :dlist="dlist"
              :colDict="colDict[dlist.list.luid]"
              v-model="pts[dlist.list.luid]"
            />
          </div>
        </div>
      </div>
    </q-page-container>
  </q-layout>
</template>

<script>
import Topbar from 'components/Topbar.vue'
import Notification from 'components/Notification.vue'
import Drawer from 'components/Drawer.vue'
import Ptable from 'components/Ptable.vue'
import { EventBus, Store } from 'assets/vuecommon.js'
import { InitData } from 'assets/initdata.js'
import $ from 'jquery'

const serverKeysToData = ['user', 'slists', 'dlists', 'pts']

export default {
  name: 'MainLayout',
  components: { Topbar, Notification, Drawer, Ptable },
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
    drawerState () {
      console.log('drawerState')
    },
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
            this.colDict = this.solst.dlists.reduce((acc, x) => { var y = {}; y[x.list.luid] = x.list.dat.cols; return { ...acc, ...y } }, {})
          } else if (key === 'pts') {
            this.pts = this.solst.dlists.map(x => x.list.luid).reduce((acc, x) => { var y = {}; y[x] = server.pts.filter(pt => pt.luid === x); return { ...acc, ...y } }, {})
            for (var luid in this.pts) {
              var empties = this.colDict[luid].reduce((acc, x) => { var y = {}; y[x.cuid] = x.type === 0 ? { text: '' } : { tasks: [{ text: '', check: false }] }; return { ...acc, ...y } }, {})
              for (var ptIndex in this.pts[luid]) {
                this.pts[luid][ptIndex].dat = { ...JSON.parse(JSON.stringify(empties)), ...this.pts[luid][ptIndex].dat }
              }
            }
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
        url: `${this.server}/init/lsp`
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
