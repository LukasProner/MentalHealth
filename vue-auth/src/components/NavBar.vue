<template>
  <header>
    <router-link to="/" class="logo">
      <h1>PsyToolsApp.com</h1>
    </router-link>
    <div class="hamburger" id="hamburger-icon">
      &#9776;
    </div>
    <nav class="navigation">
      <router-link to="/tests" >Vytvoriť test</router-link>
      <router-link to="/contact" >Kontakt</router-link>
      <router-link to="/documentation" >Dokumentácia</router-link>
      <router-link to="/choosetest" >Moje testy</router-link>
      <router-link to="/default" >Zoznam testov</router-link>
      
      <router-link v-if="!auth" to="/login" class="btn">Prihlásiť</router-link>
      <router-link v-if="!auth" to="/register" class="btn register">Register</router-link>
    
      <router-link v-if="auth" to="/login" class="btn" @click="logout">Logout</router-link>
    </nav>
  </header>
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

<style scoped>
header {
    background-color: var(--color-white);
    padding: 10px 20px;
    text-align: center;
    display: flex;
    align-items: center; /* Vertikálne zarovnanie */
    justify-content: space-between;
}

header .logo {
  text-decoration: none;
}

header .logo h1 {
    margin: 0;
    font-size: 2rem;
    padding-left: 50px;
    text-decoration: none;
    font-weight: bold;
    
}

.hamburger {
    display: none;
    font-size: 2rem;
    cursor: pointer;
}

@media (max-width: 1107px) {
    header {
        justify-content: space-between;
        padding: 10px 20px;
    }
    .hamburger {
        display: block;
        font-size: 2rem;
        cursor: pointer;
    }
}
.navigation {
    display: flex;
    text-align: center;
}

.navigation a {
    padding: 8px;
    margin: 5px;
    text-decoration: none;
    color: var(--color-h1);
    font-size: 1rem;
    transition: background-color 0.3s;
    border-radius: 10px;
}

.navigation a:hover {
    background-color: var(--color-lightblue);
}

.navigation .btn {
    text-decoration: none;
    color: var(--color-h2);
    background-color: var(--color-login);
    font-size: 0.9rem;
    font-weight: bold;
    text-align: center;
    transition: background-color 0.3s;   
    outline: none; 
    box-shadow: none;
    border: none;
}

.navigation .btn:hover {
    background-color: var(--color-lightblue);
    outline: none;
}

.navigation .register {
    background-color: var(--color-h2);
    color: var(--color-white);
}

.navigation .register:hover {
    background-color: var(--color-login);
    color: var(--color-h2);
}

@media (max-width: 1107px) {
    .navigation {
        display: none;
        width: 100%;
    }

    .hamburger.active + .navigation {
        display: flex;
        flex-direction: column;
        width: 230px;
        background-color: var(--color-white);
        position: absolute;
        top: 40px;
        right: 0;
        z-index: 100;
    }

    .navigation a {
        padding: 10px;
        color: var(--color-h1);
        text-align: center;
        border-bottom: 1px solid #ddd;
    }

    .navigation a:hover {
        background-color: var(--color-lightblue);
    }

    .navigation a.btn {
        font-weight: bold;
        display: block;
    }
}


</style>