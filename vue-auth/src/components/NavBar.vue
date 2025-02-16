<template>
  <header>
    <router-link to="/" class="logo">
      <h1>PsyToolsApp.com</h1>
    </router-link>
    <div class="hamburger" id="hamburger-icon" @click="toggleHamburger">
      &#9776;
    </div>
    <nav class="navigation" :class="{'active': isActive}">
      <!-- <router-link to="/tests" >Vytvoriť test</router-link> -->
      <!-- <span class="separator"></span> -->
      <!-- <router-link to="/contact" >Kontakt</router-link> -->
      <div class="tooltip-container">
        <router-link to="/tests">Vytvoriť test</router-link>
        <span class="tooltip-text">Vytvorte nový test</span>
      </div>
      <div class="separator"></div>
      <div class="tooltip-container">
        <router-link to="/documentation">Dokumentácia</router-link>
        <span class="tooltip-text">Dokumentácia</span>
      </div>
      <div class="separator"></div>
      <div class="tooltip-container">
        <router-link to="/choosetest">Moje testy</router-link>
        <span class="tooltip-text">Vami vytvorené testy</span>
      </div>
      <div class="separator"></div>
      <div class="tooltip-container">
        <router-link to="/default">Zoznam testov</router-link>
        <span class="tooltip-text">Dostupne vopred prirpavené testy</span>
      </div>
      <!-- <div class="separator"></div>
      <router-link to="/documentation" >Dokumentácia</router-link>
      <div class="separator"></div>
      <router-link to="/choosetest" title="Vytvorte nový test" >Moje testy</router-link>
      <div class="separator"></div>
      <router-link to="/default" >Zoznam testov</router-link>
       -->
      <router-link v-if="!auth" to="/login" class="btn">Prihlásiť</router-link>
      <router-link v-if="!auth" to="/register" class="btn register">Register</router-link>
    
      <router-link v-if="auth" to="/login" class="btn" @click="logout">Logout</router-link>
    </nav>
  </header>
</template>

<script lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue';
import { useStore } from "vuex";

export default {
  name: "NavBar",
  setup() {
    const store = useStore();
    const loading = ref(true);  // Stav pre overovanie
    const auth = computed(() => store.state.authenticated);
    const isActive = ref(false); // Stav pre aktívny hamburger

    const checkAuth = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/user/', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
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
      } finally {
        loading.value = false;  // Nastaví `loading` na false po overení
      }
    };

    const logout = async () => {
      await fetch('http://localhost:8000/api/logout/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });
      store.commit('SET_AUTHENTICATED', false);
      store.dispatch('setAuth', false); 
    };

    const toggleHamburger = () => {
      isActive.value = !isActive.value; // Prepnúť stav zobrazenia navigácie
    };

    // Zavrie navigáciu pri kliknutí mimo
    const closeNavigationOnClickOutside = (event: MouseEvent) => {
      const nav = document.querySelector('.navigation');
      const hamburger = document.querySelector('.hamburger');
      if (nav && !nav.contains(event.target as Node) && !hamburger?.contains(event.target as Node)) {
        isActive.value = false; // Skryje navigáciu
      }
    };

    // Pridá event listener pri načítaní komponentu
    onMounted(() => {
      document.addEventListener('click', closeNavigationOnClickOutside);
    });

    // Odstráni event listener pri unmountovaní komponentu
    onBeforeUnmount(() => {
      document.removeEventListener('click', closeNavigationOnClickOutside);
    });

    checkAuth();

    return {
      auth,
      logout,
      isActive,
      toggleHamburger
    };
  }
};
</script>

<style scoped>

/* Kontajner pre tooltip */
.tooltip-container {
    position: relative;
    display: inline-block;
    display: flex;
    text-align: center;
    justify-content: center;
}

/* Štýl tooltipu */
.tooltip-container .tooltip-text {
    position: absolute;
    top: 100%;  
    left: 50%;
    transform: translateX(-50%);
    background-color: white;
    color: var(--color-button-hover);
    font-weight: bold;
    padding: 6px 10px;
    border-radius: 5px;
    white-space: nowrap;
    font-size: 0.8rem;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease-in-out, visibility 0s linear 0.3s;
    border: 3px solid var(--color-lightblue);
}

.tooltip-container:hover .tooltip-text {
    opacity: 1;
    visibility: visible;
    transition-delay: 2s;  
}

.tooltip-container:not(:hover) .tooltip-text {
    transition-delay: 0s;  
}


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

@media (max-width: 1195px) {
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
    justify-content: center;
}

.navigation a {
    padding: 8px;
    margin: 5px;
    text-decoration: none;
    color: var(--color-h1);
    font-size: 1rem;
    transition: background-color 0.3s;
    border-radius: 10px;
    text-align: center; /* Zarovnanie textu na stred */
    min-width: 109px; /* Minimálna šírka */
    max-width: 200px; /* Maximálna šírka */
}

.navigation a:hover {
    background-color: var(--color-lightblue);
}
.separator {
  content: '';
  width: 5px;
  height: 50px;
  background-color: var(--color-lightblue);
  border-radius: 5px;
  display: inline-block;
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

@media (max-width: 1195px) {
    .navigation {
        display: none;
        width: 100%;
    }

    .navigation.active {
        display: flex;
        flex-direction: column;
        width: 230px;
        background-color: var(--color-white);
        position: absolute;
        top: 50px;
        right: 0;
        z-index: 100;
        border-radius: 8px;
        border-bottom: solid var(--color-lightblue);
        border-left:solid var(--color-lightblue);
        border-color: var(--color-lightblue);
    }

    .navigation a {
        padding: 10px;
        color: var(--color-h1);
        text-align: center;
        border-bottom: 1px solid #ddd;
        width: 100%;
    }

    .navigation a:hover {
        background-color: var(--color-lightblue);
    }

    .navigation a.btn {
        font-weight: bold;
        display: block;
        margin:auto;
        margin-bottom: 10px;
    }
    .separator {
        display: none;
    }
}

</style>
