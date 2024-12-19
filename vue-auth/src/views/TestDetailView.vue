
<template>
  <div v-if="test">
    <h1>{{ test.name }}</h1>
    <!-- Pole pre testový kód -->
    <div>
      <label for="test_code">Testový kód:</label>
      <input v-model="testCode" id="test_code" type="text" required />
    </div>
    
    <form @submit.prevent="submitAnswers">
      <div v-for="question in test.questions" :key="question.id">
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
      <button type="submit">Submit</button>
    </form>
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
import { useRoute } from 'vue-router';

export default {
  setup() {
    const store = useStore(); // používame Vuex store
    const route = useRoute(); // používame Vue Router

    const answers = ref({});
    const test = ref(null);
    const testCode = ref(''); // Testový kód
    const error = ref('');
    const loading = ref(true);

    // Funkcia na načítanie testu
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
      } catch (err) {
        error.value = 'Test sa nepodarilo načítať. Skontrolujte, či existuje alebo máte oprávnenie.';
        console.error('Error:', err);
      } finally {
        loading.value = false;
      }
    };

    // Funkcia na odoslanie odpovedí
    const submitAnswers = async () => {
      try {
        console.log('Odosielam odpovede:', answers.value);
        console.log('Testový kód:', testCode.value);

        const response = await fetch(`http://localhost:8000/api/tests/${test.value.id}/submit/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            test_code: testCode.value, // Pridáme testový kód
            answers: Object.entries(answers.value).map(([question_id, answer]) => ({
              question_id,
              answer,
            }))
          }),
        });

        if (!response.ok) {
          const errorMessage = await response.text();
          throw new Error(`Failed to submit test. Server response: ${errorMessage}`);
        }

        alert('Test submitted successfully!');
      } catch (error) {
        console.error(error);
        alert('An error occurred.');
      }
    };

    // Načítanie testu
    const init = async () => {
      await store.dispatch('checkAuth');
      if (store.getters.isAuthenticated) {
        const testId = route.params.id; // Získanie testId zo smeru URL
        await fetchTest(testId);
      } else {
        error.value = 'Nie ste prihlásený. Prihláste sa na prístup k testu.';
        loading.value = false;
      }
    };
    init();

    // Funkcia na inicializáciu
    onMounted(async () => {
      await store.dispatch('checkAuth');
      if (store.getters.isAuthenticated) {
        const testId = route.params.id; // Získanie testId zo smeru URL
        await fetchTest(testId);
      } else {
        error.value = 'Nie ste prihlásený. Prihláste sa na prístup k testu.';
        loading.value = false;
      }
    });

    return {
      answers,
      test,
      error,
      loading,
      submitAnswers,
      testCode, // Pridávame testový kód
    };
  },
};
</script>
