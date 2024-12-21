
<template>
  <div v-if="test">
    <h1>{{ test.name }}</h1>
    <button @click="goToResponses" >Odpovede</button>
    <form>
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
import { useRoute, useRouter } from 'vue-router';

export default {
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
      } catch (err) {
        error.value = 'Test sa nepodarilo načítať. Skontrolujte, či existuje alebo máte oprávnenie.';
        console.error('Error:', err);
      } finally {
        loading.value = false;
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
    };
  },
};
</script>
