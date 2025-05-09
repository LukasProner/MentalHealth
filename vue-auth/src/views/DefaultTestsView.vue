<template>
  <div class="container">
    <h1>Zoznam testov</h1>

    <div v-if="loading" class="loading">Načítavam testy...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <ul v-else>
      <li v-for="test in tests" :key="test.id">
        <router-link v-if="test.id" :to="`/defaulttest/${test.id}`" class="test-link">
          <i class="bi bi-file-earmark"></i>
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
<style scoped>
  .container {
    max-width: 800px;
    margin: 40px auto;
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    text-align: center;
  }

  h1 {
    font-size: 24px;
    color: #333;
    margin-bottom: 20px;
  }

  ul {
    list-style: none;
    padding: 0;
  }

  li {
    background: #f8f9fa;
    margin: 8px 0;
    padding: 12px;
    border-radius: 5px;
    transition: 0.3s;
  }

  .test-link {
    display: flex;
    align-items: center;
    justify-content: center; 
    text-decoration: none;
    color: #313840;
    font-weight: bold;
    transition: 0.3s;
  }

  .test-link i {
    font-size: 20px;
    margin-right: auto; 
    color: #333;
  }

  .test-name {
    flex-grow: 1;
    text-align: center;
  }

  a {
    text-decoration: none;
    color: #007bff;
    font-weight: bold;
    transition: 0.3s;
  }

  a:hover {
    color: #0056b3;
  }

  li:hover {
    background: #e2e6ea;
    transform: scale(1.02);
  }

  .loading {
    color: #007bff;
    font-weight: bold;
  }

  .error {
    color: #dc3545;
    font-weight: bold;
  }
</style>
  