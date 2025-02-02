
<template>
  <div v-if="test" class = "test-detail">
    <div class="routing">
      <ButtonComp text="Odpovede" fontSize="1rem" @click="goToResponses" />
      <ButtonComp text="Otazky" fontSize="1rem" @click="redirectToQuestions" />
    </div>
    <hr class="line" />
    <h1>{{ test.name }}</h1>


    <form class="form-container">
      <div v-for="question in sortedQuestions(test.questions)" :key="question.id" class="question-card">
        <p>{{ question.text }}</p>
        <!-- Textová odpoveď -->
        <input v-if="question.question_type === 'text'" v-model="answers[question.id]" type="text" />

        <div v-if="question.question_type === 'choice'">
          <label v-for="option in question.options" :key="option">
            <input type="radio" :value="option" v-model="answers[question.id]" /> {{option.text}}
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
    <ExportData :testId="test.id" class="export"/>
    {{ test.test_code }}
    <SendDataComp :testId="test.id" :testCode="test.test_code" class="export"/>

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
import ButtonComp from '@/components/ButtonComp.vue';
import SendDataComp from '@/components/SendDataComp.vue';

export default {
  components: {
    ExportData,
    ButtonComp,
    SendDataComp
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
      router.push(`/tests/${route.params.id}/responses`)
    };
    const redirectToQuestions = () => {
      router.push(`/tests/${route.params.id}/`);
    };

    return {
      answers,
      test,
      error,
      loading,
      testCode, // Pridávame testový kód
      goToResponses,
      sortedQuestions,
      redirectToQuestions
    };
  },
};
</script>

<style scoped>
.test-detail {
  margin: 0 auto;
  max-width: 800px;
  display: flex;
  justify-content: center;
  flex-direction: column;
}
.routing{
  display: flex;
  justify-content: space-evenly;
  margin-top:10px;
}
.line {
  height: 4px;
  background-color: black;
  border: none;
  border-radius: 2px; /* Zaoblené okraje */
  width: 100%;
  margin-top: 10px;
}
h1 {
  text-align: center ;
}

.form-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: var(--color-background);
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
.question-card{
  background-color: white;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 4px 4px 0 var(--color-lightblue);
  padding: 15px;
}

.question-card p {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 10px;
}
input[type="text"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1rem;
}
input[type="radio"] {
  margin-right: 5px;
}
label {
  display: block;
  margin-bottom: 5px;
  font-size: 1rem;
  cursor: pointer;
}
.export{
  margin-top: 20px;
  padding-top: 20px;
  margin:auto;
}
</style>
