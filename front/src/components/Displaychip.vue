<template>
  <q-chip v-if="dkey in dict" :outline="outline" square :class="`${classes} tinytag q-py-none p-my-none`" :color="color">
    {{ dict[dkey] }}
  </q-chip>
</template>
<style>
.tinytag {
  height:22px;
  padding-left:4px;
  padding-right:4px;
}
</style>
<script>
export default {
  name: 'Displaychip',
  props: {
    dict: {
      type: Object,
      required: false,
      default () { return {} }
    },
    dkey: {
      type: String,
      required: false,
      default () { return '' }
    },
    classes: {
      type: String,
      required: false,
      default () { return '' }
    },
    color: {
      type: String,
      required: false,
      default () { return 'white' }
    }
  },
  computed: {
    cclasses () {
      return this.classes.replace('outline', '')
    },
    outline () {
      return /outline/.test(this.classes)
    }
  }
}
</script>
