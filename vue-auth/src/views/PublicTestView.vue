<!-- <template>
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
                <input type="radio" :value="option" v-model="answers[question.id]" /> {{ option.text }}
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
          <button @click="evaluateTest" type="submit">Odoslať odpovede</button>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, toRaw } from 'vue';
import { useRoute } from 'vue-router';

export default {
  setup() {
    const route = useRoute(); 
    const testId = route.params.id; 

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
    const evaluateTest = async () => {
      try {
          console.log(answers)
          const response = await fetch(`http://localhost:8000/api/tests/${test.value.id}/evaluate/`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                  test_code: testCode.value, // Pridáme testový kód
                  answers: Object.entries(answers.value).map(([question_id, answer]) => ({
                      question_id,
                      answer,
                  }))
              }),
              credentials: 'include',
          });

          if (!response.ok) {
              const data = await response.json();
              throw new Error(data.error || 'Chyba pri vyhodnocovaní');
          }

          const data = await response.json();
          console.log('Výsledok testu:', data);
          // Zobraz odpoveď používateľovi
          alert(`Dosiahnuté body: ${data.total_points}\nOdpoveď: ${data.response}`);
      } catch (err) {
          console.error('Chyba pri vyhodnocovaní:', err.message || err);
      }
    };

    return {
      test,
      testCode,
      error,
      answers,
      verifyCode,
      submitAnswers,
      evaluateTest,
    };
  },
};

  </script>
   -->

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
                <input type="radio" :value="option" v-model="answers[question.id]" /> {{ option.text }}
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
          <button @click="evaluateTest" type="submit">Odoslať odpovede</button>
        </form>
        
        <!-- Zobrazenie odpovedí po vyhodnotení -->
        <div v-if="evaluationResult">
          <h2>Výsledok testu</h2>
          <div v-for="result in evaluationResult" :key="result.category">
            <p><strong>Kategória:</strong> {{ result.category }}</p>
            <p><strong>Dosiahnuté body:</strong> {{ result.total_points }}</p>
            <p><strong>Odpoveď:</strong> {{ result.response }}</p>
          </div>
  
          <!-- Zobrazenie odpovedí používateľa -->
          <h3>Vaše odpovede:</h3>
          <ul>
            <li v-for="(answer, question_id) in answers" :key="question_id">
              Otázka {{ question_id }}: {{ answer }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, toRaw } from 'vue';
  import { useRoute } from 'vue-router';
  
  export default {
    setup() {
      const route = useRoute(); 
      const testId = route.params.id; 
  
      const test = ref(null);
      const testCode = ref('');
      const error = ref('');
      const answers = ref({});
      const evaluationResult = ref(null); // Pridáme stav pre výsledok vyhodnotenia
  
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
  
      const evaluateTest = async () => {
        try {
            console.log(answers)
            const response = await fetch(`http://localhost:8000/api/tests/${test.value.id}/evaluate/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    test_code: testCode.value, // Pridáme testový kód
                    answers: Object.entries(answers.value).map(([question_id, answer]) => ({
                        question_id,
                        answer,
                    }))
                }),
                credentials: 'include',
            });
  
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Chyba pri vyhodnocovaní');
            }
  
            const data = await response.json();
            console.log('Výsledok testu:', data);
            evaluationResult.value = data.total_score; // Uložíme výsledok vyhodnotenia
  
            // Zobraz odpoveď používateľovi
            alert(`Dosiahnuté body: ${data.total_score[0].total_points}\nOdpoveď: ${data.total_score[0].response}`);
        } catch (err) {
            console.error('Chyba pri vyhodnocovaní:', err.message || err);
        }
      };
  
      return {
        test,
        testCode,
        error,
        answers,
        verifyCode,
        submitAnswers,
        evaluateTest,
        evaluationResult, // Vrátim aj stav pre výsledky
      };
    },
  };
  </script>
  