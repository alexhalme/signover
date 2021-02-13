<template>
  <div class="q-pa-md q-gutter-sm">
    <q-table
      :columns="dlist.list.dat.cols.filter(col => col.active)"
      :data="pts"
    >
      <template v-slot:header="props">
        <!--<q-th :style="`width:${props.col.width};`">-->
        <q-tr>
          <q-th class="row no-wrap">
            <q-btn dense flat  icon="add_circle_outline" class="col-auto"
              @click="actionPts('new', { puid: '', luid: luid, dat: {} })"
            />
            <div class="col q-pt-xs">
              Baseline
            </div>
          </q-th>
          <q-th v-for="col in props.cols" :key="col.cuid">
            {{col.title}}
          </q-th>
        </q-tr>
      </template>
      <template v-slot:body="props">
        <q-tr>
          <q-td>
          </q-td>
          <q-td v-for="col in dlist.list.dat.cols.map(x => x.cuid)" :key="col">
            {{props.row.dat[col]}}
            {{colColDict[col].type === 0}}
            {{props.row.puid}}
            <q-input
              v-if="colColDict[col].type === 0"
              :value="props.row.dat[col].text"
              @input="cellChange(props.row.puid, col, { text: $event })"
            />
            <div v-if="colColDict[col].type === 1">
              <div class="row no-wrap">
                <div class="col">
                  <div class="float-right">
                    <q-btn dense icon="add_task"
                      @click="cellChange(props.row.puid, col, { tasks: [props.row.dat[col].tasks, [{ text: '', check: true}]].flat() })"
                    />
                  </div>
                </div>
              </div>
              <div class="row no-wrap" v-for="(task, taskIndex) in props.row.dat[col].tasks" :key="`${props.row.puid}${col}${taskIndex}`">
                <div class="col">
                  <q-input
                    :value="task.text"
                  />
                </div>
                <div class="col-auto">
                  <q-checkbox
                    :value="task.check"
                  />
                  <q-btn name="delete" />
                </div>
              </div>
            </div>
          </q-td>
        </q-tr>
      </template>
      <!--<template v-slot:body="props">
        <q-tr>
          <q-td>
            {{props.baseline}}
          </q-td>
          <q-td v-for="col in Object.keys(props.row).filter(x => x !== 'baseline')" :key="`${props.rowIndex}${col}`">
              <q-input
                v-if="colDict[col].type === 0"
                v-model="props.row[col].text"
                outlined dense
              >
              </q-input>
            {{colDict[col].type}}
            {{col}} {{props.row[col]}}
          </q-td>
        </q-tr>
      </template>-->
    </q-table>
  </div>
</template>
<script>
import $ from 'jquery'

export default {
  name: 'Ptable',
  props: {
    pts: {
      type: Object,
      required: false,
      default () { return {} }
    },
    dlist: {
      type: Array,
      required: false,
      default () { return [] }
    },
    colDict: {
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
    cellChange (puid, cuid, event) {
      var ptIndex = this.pts.map(x => x.puid).indexOf(puid)
      this.pts[ptIndex].dat[cuid] = event
      this.$emit('update', this.pts)
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
