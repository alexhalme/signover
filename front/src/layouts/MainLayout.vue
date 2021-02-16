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
      @setEmpties="setEmpties"
    />

    <q-page-container>
      <div v-if="logged">
        <div v-for="dlist in solst.dlists" :key="dlist.list.luid">
          <div class="row no-wrap">
            <ptable
              :dlist="dlist"
              :colDict="colDict[dlist.list.luid]"
              v-model="pts[dlist.list.luid]"
              :changeTracker="changeTracker"
              @ptsFromServer="parseServerJSONs"
              @recordChange="recordChange"
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

const serverKeysToData = ['user', 'slists', 'dlists', 'pts', 'spts']

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
    },
    colDict () {
      return this.solst.dlists.reduce((acc, x) => { var y = {}; y[x.list.luid] = x.list.dat.cols; return { ...acc, ...y } }, {})
    }
  },
  created () {
    this.$store.commit('changeServerURL', /8082|5007/.test(window.location) ? 'http://127.0.0.1:5007' : 'https://so.alexhal.me')
  },
  methods: {
    async recordChange (luid, puid, cuid) {
      this.changeTracker.time = new Date().getTime()
      var changeDict = {}
      changeDict[cuid] = this.pts[luid].filter(pt => pt.puid === puid)[0].dat[cuid]
      this.changeTracker.data[puid] = puid in this.changeTracker.data ? { ...this.changeTracker.data[puid], ...changeDict } : changeDict
      await this.changeDebounce(this.changeTracker.time)
    },
    changeDebounce (time) {
      setTimeout(() => {
        if (time === this.changeTracker.time) {
          // console.log(`SEND : time start: ${time}; time current: ${new Date().getTime()}; time last change: ${this.changeTracker.time}`)
          console.log(this.changeTracker.data)
          $.ajax({
            dataType: 'json',
            type: 'post',
            data: JSON.stringify({
              action: 'save',
              puids: Object.keys(this.changeTracker.data),
              luids: Object.keys(this.changeTracker.data).map(x => ''),
              dat: this.changeTracker.data
            }),
            url: `${this.server}/pts`
          }).done((server) => {
            this.parseServerJSONs(server)
            for (var uuid in this.changeTracker.data) {
              this.changeTracker.data[uuid] = Object.keys(this.changeTracker.data[uuid]).reduce((x, y) => { var z = {}; z[y] = false; return { ...x, ...z } }, {})
            }
          }).fail(() => {
            EventBus.$emit('notify', ['There was a connection problem with the server'], 'red-6', 2)
          })
        }
      }, 2000)
    },
    typeIt (obj) {
      if (typeof (obj) !== 'object') {
        return typeof (obj)
      }
      return Array.isArray(obj) ? 'array' : 'object'
    },
    drawerState () {
      console.log('drawerState')
    },
    // logout initiated by TopBar - here we adjust variables
    logout () {
      Object.assign(this, InitData())
    },
    // for a given 'luid', looks at all patients in this.pts[<luid>] and ensures (1) they all have a key per column (active or not)
    // and that the mapped value is appropriate
    setEmpties (luid, puids) {
      var empties = this.colDict[luid].reduce((acc, x) => { var y = {}; y[x.cuid] = x.type === 0 ? { text: '' } : { tasks: [{ text: '', check: false }] }; return { ...acc, ...y } }, {})
      var ptsInLuid = JSON.parse(JSON.stringify(this.pts[luid]))
      // indices
      var puidIndices = []
      if (!puids) {
        puidIndices = ptsInLuid.map((x, y) => y)
      } else {
        puidIndices = ptsInLuid.map(pt => pt.puid).map((x, y) => puids.indexOf(x) + 1 ? y : -1).filter(y => y + 1)
      }

      for (var i in puidIndices) {
        // ptsInLuid[puidIndices[i]].dat = { ...JSON.parse(JSON.stringify(empties)), ...ptsInLuid[puidIndices[i]].dat }
        for (var key in empties) {
          if (key !== 'baseline') {
            if (!(key in ptsInLuid[puidIndices[i]].dat)) {
              ptsInLuid[puidIndices[i]].dat[key] = JSON.parse(JSON.stringify(empties[key]))
            } else {
              switch (this.colDict[key]) {
                case 0:
                  if (this.typeIt(ptsInLuid[puidIndices[i]].dat[key]) === 'object' ? (Object.keys(ptsInLuid[puidIndices[i]].dat[key]).length === 1 ? !('text' in ptsInLuid[puidIndices[i]].dat[key]) : true) : true) {
                    ptsInLuid[puidIndices[i]].dat[key] = JSON.parse(JSON.stringify(empties[key]))
                  }
                  break
                case 1:
                  if (this.typeIt(ptsInLuid[puidIndices[i]].dat[key]) === 'object' ? (Object.keys(ptsInLuid[puidIndices[i]].dat[key]).length === 1 ? !('tasks' in ptsInLuid[puidIndices[i]].dat[key]) : true) : true) {
                    ptsInLuid[puidIndices[i]].dat[key] = JSON.parse(JSON.stringify(empties[key]))
                  }
                  break
              }
            }
          }
        }
      }

      this.pts[luid] = ptsInLuid
    },
    // from a JSON returned by server, parse keys to assign to data () appropriately
    parseServerJSONs (server) {
      for (var key in server) {
        if (serverKeysToData.indexOf(key) + 1) {
          if (['dlists', 'slists'].indexOf(key) + 1) {
            this.solst[key] = server[key]
            // this.colDict = this.solst.dlists.reduce((acc, x) => { var y = {}; y[x.list.luid] = x.list.dat.cols; return { ...acc, ...y } }, {})
          } else if (key === 'pts') {
            this.pts = this.solst.dlists.map(x => x.list.luid).reduce((acc, x) => { var y = {}; y[x] = server.pts.filter(pt => pt.luid === x); return { ...acc, ...y } }, {})
            for (var luid in this.pts) {
              this.setEmpties(luid, false)
            }
          } else if (key === 'spts') {
            for (var serverPtIndex in server.spts) {
              // get luid for pt, then in this.pts[<luid>], find index of pt
              var ptLuid = server.spts[serverPtIndex].luid
              var clientPtIndex = this.pts[ptLuid].map(pt => pt.puid).indexOf(server.spts[serverPtIndex].puid)
              // if -1, pt does not exist -> put at end of list
              clientPtIndex = clientPtIndex === -1 ? this.pts[ptLuid].length : clientPtIndex
              // modify (replace) or add
              this.pts[ptLuid][clientPtIndex] = server.spts[serverPtIndex]

              // adjust dat with cols
              this.setEmpties(ptLuid, server.spts.map(pt => pt.puid))
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
