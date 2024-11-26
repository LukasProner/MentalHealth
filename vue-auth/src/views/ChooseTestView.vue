<template>
  <div>
    <h1>Vyberte test</h1>
    <div v-if="loading">
      <p>Načítavam testy...</p>
    </div>

    <div v-if="error">
      <p>{{ error }}</p>
    </div>

    <ul v-else>
      <li v-for="test in tests" :key="test.id">
        <router-link v-if="test.id" :to="{ name: 'testDetail', params: { id: test.id } }">
          {{ test.name }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';

export default {
  setup() {
    const tests = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const store = useStore();

    // Funkcia na načítanie testov
    const fetchTests = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/tests/', {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include', // Zahŕňa cookies pre autentifikáciu
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        tests.value = data; // Uloženie testov do premennej
      } catch (err) {
        error.value = 'Chyba pri načítavaní testov. Skontrolujte autentifikáciu.';
        console.error('Error:', err);
      } finally {
        loading.value = false; // Ukončenie načítania
      }
    };

    // Pri načítaní komponentu
    onMounted(async () => {
      await store.dispatch('checkAuth'); // Overenie autentifikácie cez Vuex store
      if (store.getters.isAuthenticated) {
        await fetchTests(); // Ak je používateľ prihlásený, načítaj testy
      } else {
        error.value = 'Nie ste prihlásený. Prihláste sa na prístup k testom.'; // Ak nie je prihlásený
        loading.value = false;
      }
    });

    return {
      tests,
      loading,
      error,
    };
  },
};
</script>
