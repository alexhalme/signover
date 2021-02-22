<template>
  <q-drawer
    v-model="show"
    show-if-above
    bordered
    content-class="bg-grey-1 q-mt-xl"
    :width="400"
  >
    <div class="row no-wrap">
      <q-btn dense flat  icon="add_circle_outline" class="col-auto"
        @click="actionList('new', '')"
      />
      <q-select
        class="col q-mt-sm q-mx-sm"
        outlined
        :value="solst.dlists"
        :options="solst.slists"
        stack-label
        label="Selected lists"
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
          <q-chip removable text-color="white" square
            class="q-ma-xs text-bold"
            :style="`border: 1.5px solid black;border-radius: 5px;background: #${selectedList.list.luid.substring(0, 6).toUpperCase()};`"
            v-for="selectedList in scope.opt"
            :tabindex="scope.tabindex"
            :key="selectedList.list.luid"
            @remove="actionList('deselect', selectedList.list.luid)"
          >
            <!-- <q-avatar color="secondary" text-color="white" icon="send" /> -->
            {{selectedList.list.dat.name}}
          </q-chip>
        </template>
      </q-select>
    </div>
    <div class="row no-wrap q-mt-md q-mx-sm" v-for="dlist in solst.dlists" :key="dlist.list.luid">
      <div class="col">
        <q-list bordered padding v-if="dlist.admin < 3">
          <q-item>
            <q-item-section>
              <q-input outlined dense
                v-if="editingListName.luid === dlist.list.luid"
                v-model="editingListName.title"
              />
              <q-chip text-color="white" square class="q-ma-xs text-bold"
                v-else
                :style="`border: 1.5px solid black;border-radius: 0px;background: #${dlist.list.luid.substring(0, 6).toUpperCase()};`"
              >
              <q-item-label class="caps text-bold text-white" overline
              >{{ dlist.list.dat.name }}</q-item-label>
              </q-chip>
            </q-item-section>

            <q-item-section side top>
              <q-chip flat
                :clickable="Boolean([1, 2].indexOf(dlist.admin) + 1)" square size="lg"
                :icon="editingListName.luid === dlist.list.luid ? 'save' : privIcons[dlist.admin]" dense color="grey-1"
                @click="editList(dlist.list.luid)"
              />
            </q-item-section>
          </q-item>

          <q-separator spaced />
          <q-tabs
            v-model="selTab[dlist.list.luid].tab"
          >
            <q-tab name="columns" label="Columns" no-caps />
            <q-tab name="users" label="Users" no-caps />
          </q-tabs>

          <div v-if="selTab[dlist.list.luid].tab==='columns'">
            <div v-for="(col, colIndex) in dlist.list.dat.cols" :key="col.cuid">
            <q-item class="row no-wrap" dense>
              <div class="col-auto q-mr-sm">
                <q-chip square dense color="grey-1" class="q-mt-xs"
                  :clickable="col.cuid === editingCol.cuid"
                  @click="editingCol.type = {0: 1, 1: 0}[editingCol.type]"
                >
                  <q-icon size="sm" class="q-py-sm" :color="col.active ? 'black' : 'grey-6'"
                    style="padding-top:10px;padding-bottom:10px;"
                    :name="{0: 'subject', 1: 'task_alt'}[col.cuid === editingCol.cuid ? editingCol.type : col.type]"
                  />
                </q-chip>
              </div>
              <div class="col">
                <div class="row no-wrap">
                  <span class="q-mt-xs" v-if="col.cuid !== editingCol.cuid">
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
                <q-btn dense flat :icon="btnData" class="q-ml-xs q-mt-xs" style="border: 1.5px solid black;border-radius: 5px;" size="sm"
                  @click="editCol(btnData, col, dlist.list.luid, $event)"
                />
                <q-btn dense flat icon="add_circle_outline" class="q-ml-xs q-mt-xs" style="border: 1.5px solid black;border-radius: 5px;" size="sm"
                  v-if="colIndex === dlist.list.dat.cols.length - 1 && ['visibility', 'visibility_off'].indexOf(btnData) + 1 && false"
                  @click="actionCol('new', dlist.list.luid)"
                />
              </div>
            </q-item>
            <q-separator v-if="colIndex < dlist.list.dat.cols.length - 1 || true" />
            </div>

            <q-item class="row no-wrap" v-if="true" dense>
              <div class="col">
                <div class="float-right">
                <q-btn dense flat icon="add_circle_outline" class="q-ml-xs q-mt-xs" style="border: 1.5px solid black;border-radius: 5px;" size="sm"
                  @click="actionCol('new', dlist.list.luid)"
                />
              </div>
              </div>
            </q-item>
          </div>

          <div v-if="selTab[dlist.list.luid].tab==='users'">
            <q-item dense class="row no-wrap q-py-none q-my-none"
              v-for="userRights in dlist.rights"
              :key="userRights.uuid"
            >
              <div class="col-auto">
                <div class="row no-wrap">
                  {{ userRights.dat.name }}
                </div>
              </div>
              <div class="col q-mr-sm">
                <div class="float-right">
                  <div class="row no-wrap q-py-none">
                  <q-chip square dense color="grey-1" class="q-px-none q-mx-xs q-py-none"
                    v-for="priv in [0, 1, 2, 3, 4]"
                    :key="priv"
                    :clickable="canChangePriv(dlist.list.luid, userRights.uuid, priv)"
                    :disable="!canChangePriv(dlist.list.luid, userRights.uuid, priv)"
                  >
                    <q-icon size="xs" class="q-py-none q-px-none" :color="userRights.priv === priv ? 'orange-6' : 'black'"
                      style="padding-top:10px;padding-bottom:10px;"
                      :name="privIcons[priv]"
                      @click="actionRights('priv', dlist.list.luid, {...userRights, priv: priv})"
                    />
                  </q-chip>
                </div>
                </div>
              </div>
            </q-item>

            <q-item class="row no-wrap">
              <div class="col-auto q-mr-sm">
                <q-chip square dense color="grey-1"
                  clickable
                  @click="actionRights('new', dlist.list.luid, { email: selTab[dlist.list.luid].newUser, priv: 4 })"
                  :disabled="Boolean(!validateEmail(selTab[dlist.list.luid].newUser) || (dlist.rights.map(x => x.email).indexOf(selTab[dlist.list.luid].newUser) + 1))"
                >
                  <q-icon size="sm" class="q-py-sm q-mt-sm q-ml-none" :color="'black'"
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
        </q-list>
      </div>
    </div>
  </q-drawer>
</template>
<style scoped>
.user-item {
  display: flex;
}
</style>
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
      privMap: PrivMap(),
      editingListName: this.resetEditionList()
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
      return { cuid: '', title: '', width: 0, type: 0, active: false, wipe: false }
    },
    resetEditionList () {
      return { luid: '', title: '' }
    },
    editList (luid) {
      if (this.editingListName.luid === luid) {
        this.actionList('changename', luid, { name: this.editingListName.title })
        this.editingListName.title = ''
        this.editingListName.luid = ''
      } else {
        this.editingListName.title = this.solst.dlists.filter(x => x.list.luid === luid)[0].list.dat.name
        this.editingListName.luid = luid
      }
    },
    editCol (action, col, luid, event) {
      switch (action) {
        case 'edit':
          this.editingCol = {
            cuid: col.cuid,
            title: col.title,
            width: col.width,
            type: col.type,
            active: col.active,
            wipe: false
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
          if (this.editingCol.cuid === col.cuid && /visibility/.test(action)) {
            this.editingCol.active = { visibility: false, visibility_off: true }[action]
            break
          }
          if (this.editingCol.cuid === col.cuid && /(delete|support)/.test(action)) {
            this.editingCol.wipe = { delete: false, support: true }[action]
            break
          }
          this.editingCol = {
            cuid: col.cuid,
            title: col.title,
            width: col.width,
            type: col.type,
            active: col.active,
            wipe: this.editingCol.wipe
          }
          if (action === 'edit') {
            break
          }
          if (action === 'unfold_more') {
            action = event.shiftKey || event.ctrlKey || event.altKey ? 'keyboard_arrow_up' : 'keyboard_arrow_down'
          }
          this.actionCol(`unitaction-${action}`, luid)
          this.editingCol = this.resetEditionCol()
          break
      }
    },
    btnIcon (col, colIndex, dlist) {
      var beingEdited = this.editingCol.cuid === col.cuid
      var btnData = [
        col.active && !beingEdited ? (colIndex !== dlist.list.dat.cols.filter(x => x.active).length - 1 ? (colIndex ? 'unfold_more' : 'keyboard_arrow_down') : (colIndex ? 'keyboard_arrow_up' : '')) : '',
        beingEdited ? 'check' : (col.active ? 'edit' : ''),
        beingEdited ? 'close' : '',
        col.active ? (beingEdited ? (this.editingCol.active ? 'visibility' : 'visibility_off') : '') : 'visibility_off',
        col.active ? (beingEdited ? (this.editingCol.active ? '' : (this.editingCol.wipe ? 'delete' : 'support')) : '') : ''
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

      // update patients
      if ('sdlists' in server) {
        for (var luid in server.sdlists.map(x => x.list.luid)) {
          this.$emit('setEmpties', server.sdlists.map(x => x.list.luid)[luid], false)
        }
      }
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
    actionList (action, luid, dat) {
      var sendVal = { action: action, luid: luid }
      if (dat) {
        sendVal = { ...sendVal, dat: dat }
      }
      $.ajax({
        dataType: 'json',
        type: 'post',
        url: `${this.server}/solst`,
        data: JSON.stringify(sendVal)
      }).done((server) => {
        this.parseServerDrawer(server)
      })
    }
  }
}
</script>
