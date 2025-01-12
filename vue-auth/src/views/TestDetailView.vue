
<template>
  <div v-if="test">
    <h1>{{ test.name }}</h1>
    <button @click="goToResponses" >Odpovede</button>
    <form>
      <div v-for="question in sortedQuestions(test.questions)" :key="question.id">
        <p>{{ question.text }}</p>
        <input v-if="question.question_type === 'text'" v-model="answers[question.id]" type="text" />
        <div v-if="question.question_type === 'choice'">
          <label v-for="option in question.options" :key="option">
            <input type="radio" :value="option" v-model="answers[question.id]" /> {{ option }}
          </label>
        </div>
        <div v-if="question.question_type === 'boolean'">
          <label>
            <input type="radio" value="Yes" v-model="answers[question.id]" /> Yes
          </label>
          <label>
            <input type="radio" value="No" v-model="answers[question.id]" /> No
          </label>
        </div>
      </div>
    </form>
    <ExportData :testId="test.id" />
  </div>
  <div v-else-if="loading">
    <p>Loading test data...</p>
  </div>
  <div v-else>
    <p>{{ error }}</p>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRoute, useRouter } from 'vue-router';
import ExportData from '@/components/Export.vue';

export default {
  components: {
    ExportData,
  },
  setup() {
    const store = useStore(); // používame Vuex store
    const route = useRoute(); // používame Vue Router
    const router = useRouter();

    const answers = ref({});
    const test = ref(null);
    const testCode = ref(''); // Testový kód
    const error = ref('');
    const loading = ref(true);

    const fetchTest = async (testId) => {
      try {
        const response = await fetch(`http://localhost:8000/api/tests/${testId}/`, {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        test.value = await response.json();
        console.log(test.value)
      } catch (err) {
        error.value = 'Test sa nepodarilo načítať. Skontrolujte, či existuje alebo máte oprávnenie.';
        console.error('Error:', err);
      } finally {
        loading.value = false;
      }
    };

    const init = async () => {
      await store.dispatch('checkAuth');
      if (store.getters.isAuthenticated) {
        const testId = route.params.id; 
        await fetchTest(testId);
      } else {
        error.value = 'Nie ste prihlásený. Prihláste sa na prístup k testu.';
        loading.value = false;
      }
    };
    init();
    

    onMounted(async () => {
      try {
        const testId = route.params.id; // Získanie testId zo smeru URL
        const response = await fetch(`http://localhost:8000/api/tests/${testId}/`);
        
        if (response.ok) {
          const data = await response.json();
          test.value = data; // Nastav dáta pre zobrazenie testu
          console.log(test.value)
        } else if (response.status === 401) {
          // Neautentifikovaný prístup k testu, ktorý nie je admin test
          error.value = 'Test nie je dostupný. Prihláste sa na prístup.';
        } else if (response.status === 403) {
          // Používateľ nemá oprávnenie na prístup
          error.value = 'Nemáte oprávnenie na zobrazenie tohto testu.';
        } else if (response.status === 404) {
          // Test neexistuje
          error.value = 'Test neexistuje.';
        }
      } catch (err) {
        error.value = 'Došlo k chybe pri načítaní testu.';
      } finally {
        loading.value = false;
      }
    });

    const sortedQuestions = (questions) => {
        return [...questions].sort((a, b) => a.id - b.id);
    };
  


    const goToResponses = () =>{
      router.push(`${route.params.id}/responses`)
    }

    return {
      answers,
      test,
      error,
      loading,
      testCode, // Pridávame testový kód
      goToResponses,
      sortedQuestions
    };
  },
};
</script>
