<template>
  <div>
    <h1>Vyberte test</h1>
    <ul>
      <!-- Kliknutím na názov testu sa presmeruje na stránku s otázkami testu -->
      <li v-for="test in tests" :key="test.id">
        <router-link :to="{ name: 'testDetail', params: { id: test.id } }">
          {{ test.name }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<!-- <script>
export default {
  data() {
    return {
      tests: []
    };
  },
  created() {
    // Načítanie zoznamu testov pri vytvorení komponentu
    fetch('http://localhost:8000/api/tests/')
      .then(response => response.json())
      .then(data => {
        this.tests = data;
      })
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
      });
  }
};
</script> -->
<script>
import { ref, onMounted } from 'vue';

export default {
  setup() {
    const tests = ref([]);

    onMounted(() => {
      // Načítanie zoznamu testov pri vytvorení komponentu
      fetch('http://localhost:8000/api/tests/')
        .then(response => response.json())
        .then(data => {
          tests.value = data;
        })
        .catch(error => {
          console.error('There was a problem with the fetch operation:', error);
        });
    });

    return {
      tests
    };
  }
};
</script>