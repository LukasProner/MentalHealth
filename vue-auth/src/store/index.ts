
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

    async checkAuth({ commit }: { commit: Commit }) {
      try {
        const response = await fetch('http://localhost:8000/api/user/', {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',  
        });

        if (response.ok) {
          commit('SET_AUTH', true);  
        } else {
          commit('SET_AUTH', false);  
        }
      } catch (error) {
        console.error('Chyba pri overovaní autentifikácie:', error);
        commit('SET_AUTH', false);  
      }
    },
  },
  getters: {
    isAuthenticated: (state: { authenticated: boolean }) => state.authenticated,
  },
  modules: {},
});
