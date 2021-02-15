<template>
  <div class="q-pa-md q-gutter-sm">
    <q-table separator="cell"
      :columns="dlist.list.dat.cols.filter(col => col.active)"
      :data="pts"
    >
      <template v-slot:header="props">
        <!--<q-th :style="`width:${props.cols[0].width};`">-->
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
          <q-th v-for="col in props.cols" :key="col.cuid" :style="`width:${col.width}px;`">
            {{col.title}} {{col.width}}
          </q-th>
        </q-tr>
      </template>
      <template v-slot:body="props">
        <q-tr no-hover>
          <q-td>
            {{props.row.dat.baseline}}
            <div class="row no-wrap">
              <div class="col">
                <q-input dense borderless style="font-size:8pt;border: 0.5px solid black;border-radius: 3px;height:15px;"
                  :value="props.row.dat.baseline.name"
                >
                <template #before>
                  <span style="font-size:8pt;height:15px;">
                    dafs
                  </span>
                </template>
                </q-input>
              </div>
              <div class="col">
              </div>
            </div>
          </q-td>
          <q-td
            v-for="col in dlist.list.dat.cols.map(x => x.cuid)"
            :key="col"
            :style="`padding:0px;width:${colColDict[col].width}px`"
          >
            <div v-if="colColDict[col].type !== 1" class="wrapper">
              <span v-if="false">
                {{props.row.dat[col]}}
                {{colColDict[col].type === 0}}
                {{props.row.puid}}
              </span>
              <q-input dense autogrow textarea square borderless spellcheck="false"
                v-if="colColDict[col].type === 0"
                :value="props.row.dat[col].text"
                @input="cellChangeText(props.row.puid, col, { text: $event })"
                class="soinput" style="vertical-align: top;"
              />
            </div>
            <!-- :style="`height:${rowHeights[props.rowIndex] - 20}px;`" -->
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
                    <template v-slot:prepend>
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
  flex:0.5;
  display: flex;
  background: #FFFFFF;
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
.q-input {
  height: 1em;
  border-top-width: 0em;
  border-bottom-width: 0em;
}
</style>
<script>
import $ from 'jquery'

// async function asyncDummy (vueFunction) {
//   await vueFunction()
//   return true
// }

export default {
  name: 'Ptable',
  props: {
    pts: {
      type: Array,
      required: false,
      default () { return {} }
    },
    dlist: {
      type: Object,
      required: false,
      default () { return [] }
    },
    colDict: {
      type: Array,
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
      emptyCell: {
        9: { },
        0: { text: '' },
        1: { tasks: [] }
      }
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
  methods: {
    getRowHeights () {
      // this.rowHeights = this.pts.map((x, y) => `ptableqtr${y}`).filter(z => document.getElementById(z)).map(row => 45)
      // asyncDummy(this.getRowHeightsDummy)
    },
    getRowHeightsDummy () {
      // setTimeout(() => {
      //   this.rowHeights = this.pts.map((x, y) => `ptableqtr${y}`).filter(z => document.getElementById(z)).map(row => document.getElementById(row).clientHeight)
      // }, 1)
    },
    updateVModel () {
      this.$emit('update', this.pts)
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
      this.updateVModel()
    },
    cellChangeText (puid, cuid, event) {
      var ptIndex = this.pts.map(x => x.puid).indexOf(puid)
      this.pts[ptIndex].dat[cuid] = event
      this.updateVModel()
    },
    // init reception of bunch of stuff by server
    actionPts (action, info) {
      $.ajax({
        dataType: 'json',
        type: 'post',
        url: `${this.server}/pts`,
        data: JSON.stringify({ action: action, puid: info.puid, luid: info.luid, dat: info.dat })
      }).done((server) => {
        this.parseServerPts(server)
      })
    }
  }
}
</script>
