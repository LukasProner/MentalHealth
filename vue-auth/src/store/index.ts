// import {Commit, createStore} from 'vuex'

// export default createStore({
//     state: {
//         authenticated: false
//     },
//     mutations: {
//         SET_AUTH: (state: { authenticated: boolean }, auth: boolean) => state.authenticated = auth
//     },
//     actions: {
//         setAuth: ({commit}: { commit: Commit }, auth: boolean) => commit('SET_AUTH', auth)
//     },
//     modules: {}
// })
import { Commit, createStore } from 'vuex';

export default createStore({
  state: {
    authenticated: false,
  },
  mutations: {
    SET_AUTH: (state: { authenticated: boolean }, auth: boolean) => state.authenticated = auth,
  },
  actions: {
    setAuth: ({ commit }: { commit: Commit }, auth: boolean) => commit('SET_AUTH', auth),

    // Nová akcia na kontrolu autentifikácie
    async checkAuth({ commit }: { commit: Commit }) {
      try {
        const response = await fetch('http://localhost:8000/api/user/', {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include', // Zahŕňa cookies pre autentifikáciu
        });

        if (response.ok) {
          commit('SET_AUTH', true); // Ak je používateľ autentifikovaný
        } else {
          commit('SET_AUTH', false); // Ak nie je autentifikovaný
        }
      } catch (error) {
        console.error('Chyba pri overovaní autentifikácie:', error);
        commit('SET_AUTH', false); // Ak zlyhá požiadavka, považuj používateľa za neautentifikovaného
      }
    },
  },
  getters: {
    // Getter na kontrolu autentifikácie
    isAuthenticated: (state: { authenticated: boolean }) => state.authenticated,
  },
  modules: {},
});
