<template>
    <div>
      <h1>Zoznam testov</h1>
      <div v-if="loading">Načítavam testy...</div>
      <div v-else-if="error">{{ error }}</div>
      <ul v-else>
        <li v-for="test in tests" :key="test.id">
          <router-link v-if="test.id" :to="{name:'testDetail', params: {id: test.id} }">
            {{ test.name }}
          </router-link>
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  
  export default {
    setup() {
      const tests = ref([]); // Reactive premenná pre testy
      const loading = ref(true); // Stav načítavania
      const error = ref(null); // Stav pre chyby
  
      const fetchTests = async () => {
        try {
          const response = await fetch(`http://localhost:8000/api/tests/default/`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include', 
          });
          console.log('response',response)
  
          if (!response.ok) {
            throw new Error(`HTTP chyba! Status: ${response.status}`);
          }
  
          const data = await response.json();
          tests.value = data.tests; // Uloženie testov do premennej
        } catch (err) {
          error.value = 'Chyba pri načítavaní testov. Skontrolujte autentifikáciu.';
        } finally {
          loading.value = false; // Ukončenie načítavania
        }
      };
  
      onMounted(fetchTests); // Spustenie fetchTests pri načítaní komponentu
  
      return {
        tests,
        loading,
        error,
      };
    },
  };
  </script>
  