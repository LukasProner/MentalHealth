<template>
  <nav class="navbar navbar-expand-md navbar-dark bg-dark mb-4">
    <div class="container-fluid">
      <router-link to="/" class="navbar-brand">Home</router-link>

      <div>
        <ul class="navbar-nav me-auto mb-2 mb-md-0" v-if="!auth">
        <!-- <ul class="navbar-nav me-auto mb-2 mb-md-0"> -->
          <li class="nav-item">
            <router-link to="/login" class="nav-link">Login</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/register" class="nav-link">Register</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/draw" class="nav-link" >Draw</router-link>
          </li>
        </ul>

        <ul class="navbar-nav me-auto mb-2 mb-md-0" v-if="auth">
          <li class="nav-item">
            <!-- <a href="#" class="nav-link" @click="logout">Logout</a> -->
            <router-link to="/login" class="nav-link" @click="logout">Logout</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/draw" class="nav-link" >Draw</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/tests" class="nav-link" >Create test</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/choosetest" class="nav-link" >All tests</router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script lang="ts">
import {computed,ref} from 'vue';
import {useStore} from "vuex";

export default {
  name: "NavBar",
  setup() {
    const store = useStore();
    const loading = ref(true);  // Stav pre overovanie
    const auth = computed(() => store.state.authenticated)

    const checkAuth = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/user/', {
          method: 'GET',
          headers: {'Content-Type': 'application/json'},
          credentials: 'include',
        });
        if (response.ok) {
          store.commit('SET_AUTHENTICATED', true);  // Nastaví stav používateľa na prihlásený
        } else {
          store.commit('SET_AUTHENTICATED', false);
        }
      } catch (error) {
        store.commit('SET_AUTHENTICATED', false);
        store.dispatch('setAuth', false); 
      }
      finally {
          loading.value = false;  // Nastaví `loading` na false po overení
        }
    }

    const logout = async () => {
      await fetch('http://localhost:8000/api/logout/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
      });
      store.commit('SET_AUTHENTICATED', false);
      store.dispatch('setAuth', false); 
    }
    checkAuth();

    return {
      auth,
      logout
    }
  }
}
</script>