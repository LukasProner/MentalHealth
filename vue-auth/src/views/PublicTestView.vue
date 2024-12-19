<template>
    <div>
      <div v-if="!test">
        <h1>Overenie testového kódu</h1>
        <p>Zadajte kód, ktorý ste dostali od psychológa:</p>
        <input v-model="testCode" placeholder="Testový kód" />
        <button @click="verifyCode">Overiť</button>
        <p v-if="error" style="color: red">{{ error }}</p>
      </div>
  
      <div v-else>
        <h1>{{ test.name }}</h1>
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
          <button type="submit">Odoslať odpovede</button>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  import { ref } from 'vue';
import { useRoute } from 'vue-router';

export default {
  setup() {
    const route = useRoute(); // Získanie prístupu k route
    const testId = route.params.id; // Dynamický parameter `id` z URL

    const test = ref(null);
    const testCode = ref('');
    const error = ref('');
    const answers = ref({});

    const verifyCode = async () => {
      try {
        console.log(testCode.value);
        const response = await fetch(`http://localhost:8000/api/tests/${testId}/public/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ test_code: testCode.value }),
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.error || 'Unknown error occurred');
        }

        test.value = await response.json();
      } catch (err) {
        error.value = err.message;
      }
    };

    const submitAnswers = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/tests/${test.value.id}/submit/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            test_code: testCode.value, // Pridáme testový kód
            answers: Object.entries(answers.value).map(([question_id, answer]) => ({
              question_id,
              answer,
            }))
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to submit answers');
        }

        alert('Odpovede boli úspešne odoslané!');
      } catch (err) {
        console.error(err);
        alert('Nastala chyba pri odosielaní odpovedí.');
      }
    };

    return {
      test,
      testCode,
      error,
      answers,
      verifyCode,
      submitAnswers,
    };
  },
};

  </script>
  