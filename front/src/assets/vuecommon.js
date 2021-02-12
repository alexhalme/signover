import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export const EventBus = new Vue()

export const Store = new Vuex.Store({
  state: {
    server: ''
  },
  mutations: {
    changeServerURL (state, server) {
      state.server = server
    }
  }
})
