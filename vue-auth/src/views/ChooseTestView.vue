
<template>
  <div class="test-list">
    <h1>Zoznam vašich testov</h1>

    <div class="loading" v-if="loading">
      <p>Načítavam testy...</p>
    </div>

    <div class="error" v-if="error">
      <p>{{ error }}</p>
    </div>

    <div class="test-grid" v-else>
      <router-link to="/tests" class="test-card add-test">
        <span class="add-icon">+</span>
      </router-link>

      <div class="test-card" v-for="test in tests" :key="test.id">
        <div class="test-header">
          <router-link
            v-if="test.id"
            :to="{ name: 'testDetail', params: { id: test.id } }"
            class="test-name"
          >
            {{ test.name }}
            <p>Vytvorený {{ getDate(test.created_at) }}</p>
          </router-link>
          <button class="delete-btn" @click.stop="deleteTest(test.id)">×</button>
        </div>
      </div>
    </div>
  </div>
  <FooterComp></FooterComp>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import FooterComp from '@/components/FooterComp.vue';

export default {
  components:{FooterComp},
  setup() {
    const tests = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const store = useStore();

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
        loading.value = false; 
      }
    };
    const getDate = (dateString) => {
      const date = new Date(dateString); // Vytvorenie objektu Date
      const day = date.getDate(); // Získanie dňa
      const month = date.getMonth() + 1; // Získanie mesiaca, +1 pretože mesiace sú počítané od 0
      const year = date.getFullYear(); // Získanie roka
      return `${day < 10 ? '0' + day : day}.${month < 10 ? '0' + month : month}.${year}`; // Formátovanie dátumu
    }
    const deleteTest = async (testId) => {
      try {
        const response = await fetch(`http://localhost:8000/api/tests/${testId}/`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include', // Zahŕňa cookies pre autentifikáciu
        });

        if (!response.ok) {
          throw new Error(`Chyba pri odstraňovaní testu. Status: ${response.status}`);
        }

        // Odstránime test z lokálneho zoznamu
        tests.value = tests.value.filter(test => test.id !== testId);
      } catch (err) {
        console.error('Error:', err);
      }
    };

    onMounted(async () => {
      await store.dispatch('checkAuth'); 
      if (store.getters.isAuthenticated) {
        await fetchTests(); 
      } else {
        error.value = 'Nie ste prihlásený. Prihláste sa na prístup k testom.'; 
        loading.value = false;
      }
    });

    return {
      tests,
      loading,
      error,
      getDate,
      deleteTest,
    };
  },
};
</script>
<style scoped>
.test-list{
  text-align: center;
  min-height: 800px;
  padding: 20px;
}
.test-grid{
  display: flex;
  max-width: 800;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px;
}
.test-card{
  display: flex;
  flex-direction: column;
  border-radius: 10px;
  width: 150px;
  height: 150px;
  background-color: var(--color-lightGray);
  justify-content: center;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}
.test-card:hover{
  transform: scale(1.05);
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
}

.add-test {
  background-color: #f5f5f5;
  border: 2px dashed #aaa;
  text-decoration: none;
}

.add-test .add-icon {
  font-size: 2rem;
  color: #666;
  font-weight: bold;
  text-decoration: none;
}
.test-card .test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 100%;
  padding: 10px;
  box-sizing: border-box;
}

.test-card .test-name {
  font-size: 1rem;
  font-weight: bold;
  color: #333;
  text-decoration: none;
}
.test-name p {
  margin-bottom: auto; 
  padding: 5px;
  font-weight:100;
  font-size: 80%;
}
.delete-btn {
  position: absolute; 
  top: 10px; 
  right: 10px; 
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #f44336;
  cursor: pointer;
  padding: 0;
  margin: 0;
  transition: color 0.2s;
}

.delete-btn:hover {
  color: #d32f2f;
}
</style>
