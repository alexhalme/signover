<template>
  <q-td>
    <div v-if="puid.length ? edit[puid] : false">
      <div class="row no-wrap">
        <div class="col-auto q-pl-sm">
          <div class="row no-wrap"
            v-for="baseData in ['name', 'surname', 'mrn', 'insurance', 'dob', 'admit', 'room', 'age']"
            :key="`c1${baseData}`"
          >
            <span style="height:22px;">
              {{baseData}}
            </span>
          </div>
        </div>
        <div class="col">
          <div class="row no-wrap"
            v-for="baseData in ['name', 'surname', 'mrn', 'insurance', 'dob', 'admit', 'room']"
            :key="`c1${baseData}`"
          >
            <q-input dense borderless
              class="q-pl-xs q-ml-xs q-mb-xs sotinput"
              style="border: 0.5px solid black;height:18px;"
              :value="baselineData[baseData]"
              @input="$emit('changeBaseline', puid, baseData, $event)"
            />
            <q-btn-toggle v-if="baseData==='age' && false" dense flat push style="height:30px;padding:0px;"
              class="dense bg-black" text-color="white" toggle-color="grey-6" color="dark"
              :options="['M','F','X'].map(x => new Object({value: x, label: x}))"
              :value="baselineData.gender"
            />
          </div>
          <div class="row no-wrap">
            <div class="col">
              <div class="row no-wrap">

                <q-input dense borderless
                  class="q-pl-xs q-ml-xs q-mb-xs sotinput"
                  style="border: 0.5px solid black;height:18px;width:50px;"
                  :value="baselineData.age"
                  @input="$emit('changeBaseline', puid, 'age', $event)"
                />
                <span class="q-pl-xs"> gender </span>
                <q-input dense borderless
                  class="q-pl-xs q-ml-xs q-mb-xs sotinput"
                  style="width:30px;"
                  :value="baselineData.gender"
                  @input="$emit('changeBaseline', puid, 'gender', $event)"
                />
                <q-chip clickable square icon="save" class="q-pa-none q-pl-sm q-ma-none q-m" color="white" style="height:18px;"
                  @click="changeEdit(false)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="puid.length ? !edit[puid] : false">
      <div class="row no-wrap">
        <div class="col">
          <displaychip classes="text-bold"
            :dict="parseBaseline(puid)"
            dkey="name"
          />
          <displaychip classes="text-bold text-white" color="blue-6"
            :dict="parseBaseline(puid)"
            dkey="id"
          />
        </div>
        <div class="col-auto">
          <div class="float-right">
            <q-chip clickable square icon="edit" class="q-pa-none q-ma-none" color="white"
              @click="changeEdit(true)"
            />
          </div>
        </div>
      </div>
      <div class="row no-wrap">
        <displaychip classes=""
          :dict="parseBaseline(puid)"
          dkey="mrn"
        />
      </div>
      <div class="row no-wrap">
        <displaychip classes=""
          :dict="parseBaseline(puid)"
          dkey="dates"
        />
        <displaychip classes="text-white outline" color="black"
          :dict="parseBaseline(puid)"
          dkey="los"
        />
      </div>
    </div>
  </q-td>
</template>
<script>
import Displaychip from 'components/Displaychip.vue'

export default {
  name: 'Baseline',
  components: { Displaychip },
  props: {
    baselineData: {
      type: Object,
      required: false,
      default () { return {} }
    },
    puid: {
      type: String,
      required: false,
      default () { return '' }
    },
    edit: {
      type: Object,
      required: false,
      default () { return {} }
    },
    pts: {
      type: Array,
      required: false,
      default () { return [] }
    }
  },
  model: {
    prop: 'edit',
    event: 'update'
  },
  methods: {
    changeEdit (bool) {
      this.edit[this.puid] = bool
      this.$emit('update', JSON.parse(JSON.stringify(this.edit)))
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
    }
  }
}
</script>
