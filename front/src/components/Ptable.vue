<template>
  <div class="q-pa-md q-gutter-sm">
    <q-table separator="cell"
      :columns="dlist.list.dat.cols.filter(col => col.active)"
      :data="pts"
      :rows-per-page-options="[50, 25, 10]"
    >
      <template #top-left>
        <q-chip text-color="white" square class="q-ma-xs text-bold"
          :style="`border: 1.5px solid black;border-radius: 0px;background: #${dlist.list.luid.substring(0, 6).toUpperCase()};`"
        >
        <q-item-label class="caps text-bold text-white" overline
        >{{ dlist.list.dat.name }}</q-item-label>
        </q-chip>
      </template>
      <template v-slot:header="props">
        <q-tr>
          <q-th>
            <div class="row no-wrap">
              <q-btn dense flat  icon="add_circle_outline" class="col-auto"
                @click="actionPts('new', { puid: '', luid: luid, dat: {} })"
              />
              <div class="col q-pt-sm q-ml-sm">
                Baseline
              </div>
            </div>
          </q-th>
          <q-th v-for="col in props.cols.filter(x => x.active)" :key="col.cuid" :style="`width:${col.width}px;`">
            {{col.title}}
          </q-th>
        </q-tr>
      </template>
      <template v-slot:body="props">
        <q-tr no-hover>
          <baseline
            v-model="editBL"
            :puid="props.row.puid"
            :pts="pts"
            :baselineData="props.row.dat.baseline"
            @changeBaseline="cellChangeBaseline"
          />
          <q-td
            v-for="col in dlist.list.dat.cols.filter(x => x.active).map(y => y.cuid)"
            :key="col"
            :style="`padding:0px;width:${colColDict[col].width}px`"
          >
            <div v-if="colColDict[col].type !== 1" class="wrapper">
              <span v-if="false">
                {{props.row.dat[col]}}
                {{colColDict[col].type === 0}}
                {{props.row.puid}}
                {{parseTracker(props.row.puid, col)}}
              </span>
              <q-input dense autogrow textarea square borderless spellcheck="false"
                v-if="colColDict[col].type === 0"
                :value="props.row.dat[col].text"
                @input="cellChangeText(props.row.puid, col, { text: $event })"
                class="soinput" style="vertical-align: top;"
              >
                <template #append v-if="parseTracker(props.row.puid, col)">
                  <q-icon
                    :name="{ 2: 'hourglass_empty', 1: 'done_all' }[parseTracker(props.row.puid, col)]"
                    size="xs"
                    class="q-pa-none q-ma-none"
                  />
                </template>
              </q-input>
            </div>
            <div v-else>
              <div class="row no-wrap" style="padding:0px"
                v-for="(task, taskIndex) in props.row.dat[col].tasks"
                :key="`${props.row.puid}${col}${taskIndex}`"
              >
                <div class="col">
                  <q-input dense class="q-px-xs"  color="black"
                    :value="task.text"
                    @input="cellChangeTask(props.row.puid, col, taskIndex, 'text', $event)"
                  >
                    <template v-slot:before>
                      <q-checkbox size="xs" color="dark"
                        :value="task.check"
                        @input="cellChangeTask(props.row.puid, col, taskIndex, 'check', $event)"
                      />
                    </template>
                    <template v-slot:after>
                      <q-btn icon="delete" :disable="false" dense size="sm" flat :class="taskIndex !== props.row.dat[col].tasks.length - 1 ? 'q-mr-lg' : ''"
                        @click="cellChangeTask(props.row.puid, col, taskIndex, 'delete', null)"
                      />
                      <q-btn v-if="taskIndex === props.row.dat[col].tasks.length - 1" icon="add_task" dense size="sm" flat
                        @click="cellChangeTask(props.row.puid, col, taskIndex, 'add', null)"
                      />
                    </template>
                  </q-input>
                </div>
              </div>
            </div>
          </q-td>
        </q-tr>
      </template>
    </q-table>
  </div>
</template>
<style>
.soinput2 {
  border-left: 0.5px solid black;
  border-right: 0.5px solid black;
}
.soinput {
  flex:0.1;
  display: flex;
  background: #FFFFFF;
}
.sotinput {
  font-size:10pt;
  border: 0.5px solid black;
  border-radius: 3px;
  height:18px;
}
.wrapper, html, body {
  height: 100%;
  margin: 0;
}
.wrapper {
  display: flex;
  flex-direction: column;
}
.q-textarea.q-field--dense .q-field__native {
  padding: 0px;
  margin: 0px;
  height: 100%;
}
.tinytag {
  height:22px;
  padding-left:4px;
  padding-right:4px;
}
</style>
<script>
import Baseline from './Baseline.vue'
import $ from 'jquery'

// async function asyncDummy (vueFunction) {
//   await vueFunction()
//   return true
// }

export default {
  name: 'Ptable',
  components: { Baseline },
  props: {
    pts: {
      type: Array,
      required: false,
      default () { return [] }
    },
    dlist: {
      type: Object,
      required: false,
      default () { return {} }
    },
    colDict: {
      type: Array,
      required: false,
      default () { return [] }
    },
    changeTracker: {
      type: Object,
      required: false,
      default () { return {} }
    }
  },
  model: {
    prop: 'pts',
    event: 'update'
  },
  data () {
    return {
      editBL: {},
      lastModif: 0
    }
  },
  computed: {
    luid () {
      return this.dlist.list.luid
    },
    server () {
      return this.$store.state.server
    },
    colColDict () {
      return this.colDict.reduce((acc, x) => { var y = {}; y[x.cuid] = x; return { ...acc, ...y } }, {})
    }
  },
  created () {
    this.makeEditBL()
  },
  methods: {
    makeEditBL () {
      for (var i in this.pts) {
        if (!(this.pts[i].puid in this.editBL)) {
          this.editBL[this.pts[i].puid] = false
        }
      }
    },
    parseTracker (puid, cuid) {
      return puid in this.changeTracker.data ? (cuid in this.changeTracker.data[puid] ? (this.changeTracker.data[puid][cuid] ? 2 : 1) : 0) : 0
    },
    parseBaseline (puid) {
      var baseLine = this.pts[this.pts.map(x => x.puid).indexOf(puid)].dat.baseline

      var yob = new Date(baseLine.dob).getFullYear()
      var age = isNaN(yob) ? baseLine.age : new Date().getFullYear() - yob

      var soa = new Date(baseLine.admit).getTime()
      var los = isNaN(soa) ? 0 : Math.floor((new Date().getTime() - new Date(baseLine.admit).getTime()) / 86400000)

      var retval = {
        name: `${baseLine.surname}, ${baseLine.name}`,
        id: `${age}${age ? ' ' : ''}${baseLine.gender.length ? baseLine.gender : (age ? ' yo' : '')}`,
        mrn: `${baseLine.mrn}${baseLine.mrn.length && baseLine.insurance.length ? ' / ' : ''}${baseLine.insurance}`,
        room: `${baseLine.room}`,
        dates: `${baseLine.admit.length ? 'A ' : ''}${baseLine.admit.length ? baseLine.admit : ''}`,
        los: `${los ? 'LOS ' : ''}${los ? String(los) : ''}${los ? 'd' : ''}`
      }

      for (var key in retval) {
        if (retval[key].replace(' / ', '').replace(' ', '') === '') {
          delete retval[key]
        }
      }

      return retval
    },
    getRowHeights () {
      // this.rowHeights = this.pts.map((x, y) => `ptableqtr${y}`).filter(z => document.getElementById(z)).map(row => 45)
      // asyncDummy(this.getRowHeightsDummy)
    },
    getRowHeightsDummy () {
      // setTimeout(() => {
      //   this.rowHeights = this.pts.map((x, y) => `ptableqtr${y}`).filter(z => document.getElementById(z)).map(row => document.getElementById(row).clientHeight)
      // }, 1)
    },
    updateVModel (puid, cuid) {
      this.$emit('update', this.pts)
      this.$emit('recordChange', this.luid, puid, cuid)
    },
    cellChangeBaseline (puid, key, event) {
      var ptIndex = this.pts.map(x => x.puid).indexOf(puid)
      this.pts[ptIndex].dat.baseline[key] = event
      this.updateVModel(puid, 'baseline')
    },
    cellChangeTask (puid, cuid, taskIndex, key, event) {
      var ptIndex = this.pts.map(x => x.puid).indexOf(puid)
      switch (key) {
        case 'delete':
          this.pts[ptIndex].dat[cuid].tasks = this.pts[ptIndex].dat[cuid].tasks.filter((x, y) => y !== taskIndex)
          this.pts[ptIndex].dat[cuid].tasks = this.pts[ptIndex].dat[cuid].tasks.length ? this.pts[ptIndex].dat[cuid].tasks : [{ text: '', check: false }]
          break
        case 'add':
          this.pts[ptIndex].dat[cuid].tasks.push({ text: '', check: false })
          break
        default:
          this.pts[ptIndex].dat[cuid].tasks[taskIndex][key] = event
      }
      this.updateVModel(puid, cuid)
    },
    cellChangeText (puid, cuid, event) {
      var ptIndex = this.pts.map(x => x.puid).indexOf(puid)
      this.pts[ptIndex].dat[cuid] = event
      this.updateVModel(puid, cuid)
    },
    // init reception of bunch of stuff by server
    actionPts (action, info) {
      $.ajax({
        dataType: 'json',
        type: 'post',
        url: `${this.server}/pts`,
        data: JSON.stringify({ action: action, puids: [info.puid], luids: [info.luid], dat: info.dat })
      }).done((server) => {
        this.$emit('ptsFromServer', server)
      })
    }
  }
}
</script>
