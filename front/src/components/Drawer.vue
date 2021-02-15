<template>
  <q-drawer
    v-model="show"
    show-if-above
    bordered
    content-class="bg-grey-1 q-mt-xl"
  >
    <div class="row no-wrap">
      <q-btn dense flat  icon="add_circle_outline" class="col-auto"
        @click="actionList('new', '')"
      />
      <q-select
        class="col  q-mx-sm"
        outlined dense
        :value="solst.dlists"
        :options="solst.slists"
        stack-label
        label="Standard"
        color="secondary"
      >
        <template v-slot:option="props">
          <q-item clickable
            @click="actionList('select', props.opt.list.luid)"
          >
            <q-tooltip>
              {{ props.opt.list.luid }}
            </q-tooltip>
            <q-item-section avatar>
              <q-icon :name="privIcons[props.opt.admin]" />
            </q-item-section>
            <q-item-section>
              {{ props.opt.list.dat.name }}
            </q-item-section>
          </q-item>
        </template>
        <template v-slot:selected-item="scope">
          <q-chip removable dense color="white" text-color="secondary" class="q-ma-none" multiple
            v-for="selectedList in scope.opt"
            :tabindex="scope.tabindex"
            :key="selectedList.list.luid"
            @remove="actionList('deselect', selectedList.list.luid)"
          >
            <q-avatar color="secondary" text-color="white" icon="send" />
            {{selectedList.list.dat.name}}
          </q-chip>
        </template>
      </q-select>
    </div>
    <div>
      <div class="row no-wrap q-mt-md q-mx-sm" v-for="dlist in solst.dlists" :key="dlist.list.luid">
        <q-list bordered padding v-if="dlist.admin < 3">
          <q-item>
            <q-item-section>
              <q-item-label class="caps" overline>{{ dlist.list.dat.name }}</q-item-label>
              <q-item-label>Single line item</q-item-label>
              <q-item-label caption>Secondary line text. Lorem ipsum dolor sit amet, consectetur adipiscit elit.</q-item-label>
            </q-item-section>

            <q-item-section side top>
              <q-icon :name="privIcons[dlist.admin]" />
            </q-item-section>
          </q-item>

          <q-separator spaced />
          <q-item-label header>Columns</q-item-label>
          <q-tabs
            v-model="selTab[dlist.list.luid].tab"
          >
            <q-tab name="columns" label="Columns" no-caps />
            <q-tab name="users" label="Users" no-caps />
          </q-tabs>

          <div v-if="selTab[dlist.list.luid].tab==='users'">
            <q-item class="row no-wrap"
              v-for="userRights in dlist.rights"
              :key="userRights.uuid"
            >
              <div class="col text-subtitle1">
                <div class="row no-wrap">
                  {{ userRights.dat.name }}
                </div>
              </div>
              <div class="col-auto q-mr-sm">
                <q-chip square dense color="grey-1"
                  v-for="priv in [0, 1, 2, 3, 4]"
                  :key="priv"
                  :clickable="canChangePriv(dlist.list.luid, userRights.uuid, priv)"
                  :disable="!canChangePriv(dlist.list.luid, userRights.uuid, priv)"
                >
                  <q-icon size="sm" class="q-py-sm" :color="userRights.priv === priv ? 'orange-6' : 'black'"
                    style="padding-top:10px;padding-bottom:10px;"
                    :name="privIcons[priv]"
                    @click="actionRights('priv', dlist.list.luid, {...userRights, priv: priv})"
                  />
                </q-chip>
              </div>
            </q-item>

            <q-item class="row no-wrap">
              <div class="col-auto q-mr-sm">
                <q-chip square dense color="grey-1"
                  clickable
                  @click="actionRights('new', dlist.list.luid, { email: selTab[dlist.list.luid].newUser, priv: 4 })"
                  :disabled="Boolean(!validateEmail(selTab[dlist.list.luid].newUser) || (dlist.rights.map(x => x.email).indexOf(selTab[dlist.list.luid].newUser) + 1))"
                >
                  <q-icon size="md" class="q-py-sm" :color="'black'"
                    style="padding-top:10px;padding-bottom:10px;"
                    name="add_circle_outline"
                  />
                </q-chip>
              </div>
              <div class="col-6">
                <q-input outlined dense
                  label="Email address"
                  v-model="selTab[dlist.list.luid].newUser"
                />
              </div>
            </q-item>
          </div>

          <div v-if="selTab[dlist.list.luid].tab==='columns'">
            <q-item class="row no-wrap"
              v-for="(col, colIndex) in dlist.list.dat.cols"
              :key="col.cuid"
            >
              <div class="col-auto q-mr-sm">
                <q-chip square dense color="grey-1"
                  :clickable="col.cuid === editingCol.cuid"
                  @click="editingCol.type = {0: 1, 1: 0}[editingCol.type]"
                >
                  <q-icon size="md" class="q-py-sm" :color="col.active ? 'black' : 'grey-6'"
                    style="padding-top:10px;padding-bottom:10px;"
                    :name="{0: 'subject', 1: 'task_alt'}[col.cuid === editingCol.cuid ? editingCol.type : col.type]"
                  />
                </q-chip>
              </div>
              <div class="col text-h6">
                <div class="row no-wrap">
                  <span v-if="col.cuid !== editingCol.cuid">
                  {{ col.title }}
                  </span>
                  <q-input outlined dense
                    v-model="editingCol.title"
                    v-else
                  />
                </div>
                <div class="row no-wrap" v-if="col.cuid === editingCol.cuid">
                  <q-slider v-model="editingCol.width" :min="10" :max="500" />
                </div>
              </div>
              <div class="col-auto" v-for="btnData in btnIcon(col, colIndex, dlist)" :key="btnData">
                <q-btn dense flat :icon="btnData" class="q-ml-xs" style="border: 1.5px solid black;border-radius: 5px;"
                  @click="editCol(btnData, col, dlist.list.luid)"
                />
              </div>
            </q-item>

            <q-item class="row no-wrap">
              <div class="col-auto q-mr-sm">
                <q-chip square dense color="grey-1"
                  clickable
                  @click="actionCol('new', dlist.list.luid)"
                >
                  <q-icon size="md" class="q-py-sm" :color="'black'"
                    style="padding-top:10px;padding-bottom:10px;"
                    name="add_circle_outline"
                  />
                </q-chip>
              </div>
            </q-item>
          </div>
        </q-list>
      </div>
    </div>
  </q-drawer>
</template>
<script>
// import EventBus from 'assets/eventbus.js'
import $ from 'jquery'
import { dictzip } from 'assets/pylike.js'
import { PrivMap } from 'assets/initdata.js'

export default {
  name: 'Drawer',
  props: {
    solst: {
      type: Object,
      required: false,
      default () { return { dlists: [], slists: [] } }
    },
    user: {
      type: Object,
      required: false,
      default () { return {} }
    }
  },
  model: {
    prop: 'solst',
    event: 'update'
  },
  data () {
    return {
      show: true,
      editingCol: this.resetEditionCol(),
      selTab: {},
      privIcons: { 0: 'close', 1: 'house', 2: 'admin_panel_settings', 3: 'edit', 4: 'visibility' },
      privMap: PrivMap()
    }
  },
  computed: {
    server () {
      return this.$store.state.server
    }
  },
  created () {
    this.getDOMMappers()
  },
  updated () {
    this.getDOMMappers()
  },
  methods: {
    // for list 'luid' and user 'uuid', can the current user (props user) change uuid's priv to <priv> ?
    canChangePriv (luid, uuid, priv) {
      var currentUserPriv = this.solst.dlists.filter(x => x.list.luid === luid)[0].rights.filter(y => y.uuid === this.user.uuid)[0].priv
      var otherUserPriv = this.solst.dlists.filter(x => x.list.luid === luid)[0].rights.filter(y => y.uuid === uuid)[0].priv

      if (uuid === this.user.uuid) {
        return Boolean(priv > currentUserPriv || !priv)
      }

      return Boolean(this.privMap[currentUserPriv][otherUserPriv].indexOf(priv) + 1)
    },
    validateEmail (email) {
      return /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(email)
    },
    getDOMMappers () {
      var missingKeys = this.solst.dlists.map(x => x.list.luid).filter(key => !(key in this.selTab))
      if (missingKeys.length) {
        this.selTab = { ...dictzip(missingKeys.map(x => [x, { tab: 'columns', newUser: '' }])), ...this.selTab }
      }
    },
    resetEditionCol () {
      return { cuid: '', title: '', width: 0, type: 0 }
    },
    editCol (action, col, luid) {
      switch (action) {
        case 'edit':
          this.editingCol = {
            cuid: col.cuid,
            title: col.title,
            width: col.width,
            type: col.type
          }
          break
        case 'close':
          this.editingCol = this.resetEditionCol()
          break
        case 'check':
          this.actionCol('edit', luid)
          this.editingCol = this.resetEditionCol()
          break
        default:
          this.editingCol = {
            cuid: col.cuid,
            title: col.title,
            width: col.width,
            type: col.type
          }
          if (action !== 'edit') {
            this.actionCol(`unitaction-${action}`, luid)
            this.editingCol = this.resetEditionCol()
          }
          break
      }
    },
    btnIcon (col, colIndex, dlist) {
      var beingEdited = this.editingCol.cuid === col.cuid
      var btnData = [
        col.active && !beingEdited && colIndex ? 'keyboard_arrow_up' : '',
        col.active && !beingEdited && colIndex !== dlist.list.dat.cols.filter(x => x.active).length - 1 ? 'keyboard_arrow_down' : '',
        beingEdited ? 'check' : (col.active ? 'edit' : ''),
        beingEdited ? 'close' : '',
        col.active ? 'toggle_off' : 'toggle_on'
      ]
      return btnData.filter(x => x !== '')
    },
    parseServerDrawer (server) {
      for (var key in this.solst) {
        if (key in server) {
          this.solst[key] = server[key]
        }
      }
      // list of pt lists in dlists or slists for *updating* w/o touching the other ones
      // marked by 's' before dlists/slists
      for (key in { sdlists: null, sslists: null }) {
        if (key in server) {
          // make a copy of solst's sublist dlists or slists, then update the list with right list index
          var solstSublistCopy = JSON.parse(JSON.stringify(this.solst[key.substring(1)]))
          // one list at the time provided by server in sslists or sdlists
          for (var serverListIndex in server[key]) {
            // find index in solst.dlists or solst.slists where luids match
            var solstListIndex = this.solst[key.substring(1)].map(x => x.list.luid).indexOf(server[key][serverListIndex].list.luid)
            solstSublistCopy[solstListIndex] = server[key][serverListIndex]
          }
          // reattribute to the subkey the whole thing changed -> if not done this way (if changed subkey instead of key in 'solst') as it is second level, won't be reactive
          this.solst[key.substring(1)] = solstSublistCopy
        }
      }
      this.$emit('update', this.solst)
    },
    actionRights (action, luid, datum) {
      var actionsRightsDat = { action: action, luid: luid, dat: datum }

      $.ajax({
        dataType: 'json',
        type: 'post',
        url: `${this.server}/rights`,
        data: JSON.stringify(actionsRightsDat)
      }).done((server) => {
        this.parseServerDrawer(server)
        if (action === 'new') {
          this.selTab[luid].newUser = ''
        }
      })
    },
    actionCol (action, luid) {
      var actionColDat = { action: action, luid: luid }
      if (['edit', 'unitaction'].indexOf(action.split('-')[0]) + 1) {
        actionColDat.dat = this.editingCol
      }
      $.ajax({
        dataType: 'json',
        type: 'post',
        url: `${this.server}/cols`,
        data: JSON.stringify(actionColDat)
      }).done((server) => {
        this.parseServerDrawer(server)
      })
    },
    actionList (action, luid) {
      $.ajax({
        dataType: 'json',
        type: 'post',
        url: `${this.server}/solst`,
        data: JSON.stringify({ action: action, luid: luid })
      }).done((server) => {
        this.parseServerDrawer(server)
      })
    }
  }
}
</script>
