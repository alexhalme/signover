<template>
  <div class="q-pa-md q-gutter-sm">
      <div class="col-1">
        <div class="float-right">
    <q-dialog :value="display.show" seamless position="bottom">
      <q-card >
        <q-linear-progress :value="ratio" color="pink" />

        <q-card-section class="row items-center no-wrap">
          <div class="col-auto q-mr-md">
            <q-icon :color="display.color" name="info" size="md"/>
          </div>
          <div class="col">
            <div class="row" v-for="(line, lineIndex) in display.text" :key="lineIndex">
              {{line}}
            </div>
          </div>
          <div class="col">
            <div class="float-right">
              <q-btn flat round icon="close" v-close-popup />
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
  </div>
  </div>
</template>
<script>
import { EventBus } from 'assets/vuecommon.js'

export default {
  name: 'Notification',
  data () {
    return {
      ratio: 0.0,
      display: { show: false, text: [], color: 'grey-6', time: 0, duration: 1 }
    }
  },
  created () {
    EventBus.$on('notify', (text, color, duration) => {
      this.display = {
        show: true,
        text: text,
        color: color,
        time: duration ? (new Date().getTime() / 1000) : 0,
        duration: duration
      }
      if (duration) {
        this.checkTimeout()
      }
    })
  },
  methods: {
    // possibility to remove notif with a timeout (set duration !== 0)
    // when called from MainLayout, use makeNotification() method
    checkTimeout () {
      // case where no delay - user removes it him/herself
      if (this.display.time === 0) {
        return false
      }
      // for the progressbar
      this.ratio = Math.min(((new Date().getTime() / 1000) - this.display.time) / this.display.duration, 1)

      // check if delay enough to remove
      if (this.display.time + this.display.duration < (new Date().getTime() / 1000)) {
        this.display.show = false
        this.ratio = 0
      } else {
        setTimeout(this.checkTimeout, 100)
      }
    }
  }
}
</script>
