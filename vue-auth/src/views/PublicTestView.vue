   <template>
    <div class="all">
      <div v-if="!test" class="enter-code">
        <h1>Overenie kódu</h1>
        <p>Zadajte kód, ktorý ste dostali:</p>
        <input v-model="testCode" placeholder="Testový kód"/>
        <ButtonComp @click="verifyCode" text="Overiť" fontSize="1rem" class="custom-button" />
        <p v-if="error" style="color: red" class="error-message">{{ error }} </p>
      </div>
    
      <div v-else class="PublicTestView">
        <h1>{{ test.name }}</h1>
        <form @submit.prevent="submitAnswers">
          <div v-for="question in sortedQuestions(test.questions)" :key="question.id" class="question-card">
            <p>{{ question}}</p>
            <div v-if="question.image_url!==null">
              obrazok je - {{ question.image_url }} a {{ question.category }}<br>
              <img :src="question.image_url" alt="Question Image" class="question-image" />
            </div>
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
            <div v-if="question.question_type ==='drawing'" class="drawing-div">
              <ButtonComp @click.prevent="goDraw(question.id)" text="Prejsť ku kresleniu" fontSize = "0.95rem"/>
            </div>
          </div>
          <ButtonComp @click="evaluateTest" type="submit" text="Odoslať odpovede" fontSize = "0.95rem"/>
        </form>
        <div v-if="showModal" class="modal" @click="closeModal">
          <div class="modal-content">
            <h2>Výsledok testu</h2>
            <div v-for="result in evaluationResult" :key="result.category">
              <p> {{ result.response }}</p>
            </div>
            <!-- <button @click="closeModal">Zatvoriť</button> -->
          </div>
        </div>
        <!-- <div v-if="evaluationResult">
          <h2>Výsledok testu</h2>
          <div v-for="result in evaluationResult" :key="result.category">
            <p><strong>Kategória:</strong> {{ result.category }}</p>
            <p><strong>Dosiahnuté body:</strong> {{ result.total_points }}</p>
            <p><strong>Odpoveď:</strong> {{ result.response }}</p>
          </div>
  
          <h3>Vaše odpovede:</h3>
          <ul>
            <li v-for="(answer, question_id) in answers" :key="question_id">
              Otázka {{ question_id }}: {{ answer }}
            </li>
          </ul>
        </div> -->
      </div>
    </div>
  </template>
  
<script>
  import ButtonComp from '@/components/ButtonComp.vue';
  import router from '@/router';
  import { onMounted, ref, toRaw, watch } from 'vue';
  import { useRoute } from 'vue-router';
  
  export default {
    components:{
      ButtonComp,
    },
    setup() {
      const route = useRoute(); 
      const testId = route.params.id; 
  
      const test = ref(null);
      const testCode = ref('');
      const error = ref('');
      const answers = ref({});
      const evaluationResult = ref(null); // Pridáme stav pre výsledok vyhodnotenia
      const showModal = ref(false);

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
          localStorage.setItem('testCode', testCode.value);
        } catch (err) {
          error.value = err.message;
        }
      };

      const sortedQuestions = (questions) => {
        return [...questions].sort((a, b) => a.id - b.id);
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
          localStorage.removeItem('answers');
          // alert('Odpovede boli úspešne odoslané!');
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
            evaluationResult.value = data.total_score;
            showModal.value = true; 
  
            // Zobraz odpoveď používateľovi
            // alert(`Dosiahnuté body: ${data.total_score[0].total_points}\nOdpoveď: ${data.total_score[0].response}`);
        } catch (err) {
            console.error('Chyba pri vyhodnocovaní:', err.message || err);
        }
      };
      const goDraw = (question_id) => {
        console.log(question_id);
        saveAnswersToLocalStorage();
        console.log("test id je " + test.value.id);
        router.push({ path: '/draw', query: { question_id: question_id,testId :test.value.id } });
      };
      const saveAnswersToLocalStorage = () => {
        localStorage.setItem('answers', JSON.stringify(answers.value));
        console.log('Answers saved to local storage:', answers.value);
      };
      const loadAnswersFromLocalStorage = () => {
        const savedAnswers = localStorage.getItem('answers');
          if (savedAnswers) {
            answers.value = JSON.parse(savedAnswers);
          }
      };
      const loadTestCode = async () => {
        const savedCode = localStorage.getItem('testCode');
        if (savedCode) {
          testCode.value = savedCode;
          await verifyCode(); // Automatické overenie kódu
        }
      };
      const closeModal = () => {
        showModal.value = false;
      };
  
      onMounted(() => {
        loadAnswersFromLocalStorage();
        loadTestCode();
      });

      watch(answers, () => {
        saveAnswersToLocalStorage();
      });

      return {
        test,
        testCode,
        error,
        answers,
        verifyCode,
        submitAnswers,
        evaluateTest,
        evaluationResult, // Vrátim aj stav pre výsledky
        sortedQuestions,
        goDraw,
        closeModal,
        showModal,
      };
    },
  };
</script>

<style scoped>
.all{
  height: 98vh;
  display: flex;
  justify-content: center;
  flex-direction: column;
  background-color: var(--color-background);
  text-align: center;
}
.enter-code{
  display: flex;
  flex-direction: column;
  text-align: center;
  max-width: 800px;
  background-color: white;
  border-radius: 30px;
  margin: auto;
  margin-top: 15px;
  box-shadow: 1px 4px 4px 1px var(--color-lightblue);
  padding: 0px 40px 40px 40px;
}
.enter-code input{
  width: 100%;
  padding: 8px 9.5px;
  margin-bottom: 15px;
  font-size: 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.3s ease;
}
.enter-code input:focus {
  border-color: var(--color-lightblue);
  box-shadow:  0 4px 4px 0 var(--color-lightblue);
}
.custom-button {
  margin: 0px 40px;
}
 
.drawing-div{
  text-align: center;
}
.PublicTestView {
  margin: 0 auto;
  max-width: 800px;
  display: flex;
  justify-content: center;
  flex-direction: column;
}
.question-card{
  background-color: white;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 4px 4px 0 var(--color-lightblue);
  padding: 15px;
  text-align: left;
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
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  max-width: 800px;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.modal-content h2 {
  margin-bottom: 10px;
}

/* .modal-content button {
  margin-top: 10px;
  padding: 5px 10px;
  border: none;
  background: #007bff;
  color: white;
  cursor: pointer;
  border-radius: 5px;
} */
/* 
.modal-content button:hover {
  background: #0056b3;
} */

.error {
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #fee2e2;
    color: #b91c1c;
    padding: 20px;
    border: 1px solid #fecaca;
    border-radius: 8px;
    font-weight: bold;
    font-size: 16px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .error p{
    margin: 0;
  }
</style>
  