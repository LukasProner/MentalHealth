
<template>
    <div v-if="test" class = "test-detail">
      <h1>{{ test.name }}</h1>
      <form class="form-container">
        <div v-for="question in sortedQuestions(test.questions)" :key="question.id" class="question-card">
          <p>{{ question.text }}</p>
          <input v-if="question.question_type==='text'" v-model="answers[question.id]" type="text" />
  
            <div v-if="question.question_type==='choice'">
                <label v-for="option in question.options" :key="option">
                    <input type="radio" :value="option" v-model="answers[question.id]" /> {{option.text}}
                </label>
            </div>
  
            <div v-if="question.question_type==='boolean'">
                <label>
                    <input type="radio" value="Yes" v-model="answers[question.id]" /> Yes
                </label>
                <label>
                <input type="radio" value="No" v-model="answers[question.id]" /> No
                </label>
            </div>
            </div>
        </form>
        <div style="display: flex; justify-content: center; margin: 20px 0 30px 0; gap: 10px;"> 
            <ExportData :testId="test.id" class="export"/>
            <ButtonComp @click="evaluateTest" type="submit" text="Odoslať odpovede" fontSize = '1 rem'/>
            <!-- <button @click="evaluateTest" type="submit">Odoslať odpovede 111</button> -->
        </div>
        <div v-if="showModal" class="modal" @click.self="closeModal">
            <div class="modal-content">
              <!-- <button class="close-btn" @click="closeModal">×</button> -->
              <h2>Výsledok testu</h2>
              <div v-for="result in evaluationResult" :key="result.category">
                <p> {{ result.response }}</p>
              </div>
              <!-- <button @click="closeModal">Zatvoriť</button> -->
            </div>
        </div>
    </div>
    <div v-else-if="loading" class="loading">
      <p>Loading test data...</p>
    </div>
    <div v-else class = "error">
      <p>{{ error }}</p>
    </div>
  </template>
  
<script>
  import{ref,onMounted} from 'vue';
  import{useStore} from 'vuex';
  import{useRoute, useRouter } from 'vue-router';
  import ExportData from '@/components/Export.vue';
  import ButtonComp from '@/components/ButtonComp.vue';
  
  export default {
    components: {
      ExportData,
      ButtonComp
    },
    setup() {
      const store = useStore(); 
      const route = useRoute();
      const router = useRouter();
      const answers = ref({});
      const test = ref(null);
      const testCode = ref(''); 
      const error = ref('');
      const loading = ref(true);
      const evaluationResult = ref(null);
      const showModal = ref(false);

      const evaluateTest=async()=>{
        try{
            // console.log(answers)
            const response=await fetch(`http://localhost:8000/api/tests/${test.value.id}/evaluate/`,{
                method:'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    test_code: testCode.value,
                    answers: Object.entries(answers.value).map(([question_id, answer]) => ({
                        question_id,
                        answer,
                    }))
                }),
                credentials: 'include',
            });
            const data = await response.json();
            console.log('Výsledok testu:', data);
            evaluationResult.value = data.total_score; 
            showModal.value = true;
  
        } catch (err) {
            console.error('Chyba pri vyhodnocovaní:',err);
        }
      };

      const closeModal=()=>{
        showModal.value = false;
      };
      
      onMounted(async()=>{
        try{
          const testId = route.params.id;  
          // console.log(testId)
          const response = await fetch(`http://localhost:8000/api/tests/${testId}/`);
          
          if (response.ok){
            const data=await response.json();
            test.value = data;  
            console.log(test.value)
          } 
        }catch(err){
          error.value='chyba pri načítaní testu';
        } finally{
          loading.value=false;
        }
      });
  
      const sortedQuestions=(questions)=>{
          return [...questions].sort((a, b) => a.id - b.id); //spread operator (...), ktorý vytvorí kópiu poľa questions.
      };
    
  
  
      const goToResponses=()=>{
        router.push(`/tests/${route.params.id}/responses`)
      };
      const redirectToQuestions=()=>{
        router.push(`/tests/${route.params.id}/`);
      };
  
      return {
        answers,
        test,
        error,
        loading,
        testCode, 
        goToResponses,
        sortedQuestions,
        redirectToQuestions,
        evaluateTest,
        closeModal,
        showModal,
        evaluationResult
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
  .close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 24px;
    font-weight: bold;
    cursor: pointer;
    color: #555;
    outline: none;
  }
  .form-container {
    max-width: 800px;
    /* margin: 0 auto; */
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
    border-left: 6px solid var(--color-button-hover);

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
    max-width: 800px;
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    text-align: center;
  }

  .modal-content h2 {
    margin-bottom: 10px;
    color: var(--color-h1);
  }

  .modal-content button {
    margin-top: 10px;
    padding: 5px 10px;
    border: none;
    background: #007bff;
    color: white;
    cursor: pointer;
    border-radius: 5px;
  }

  .modal-content button:hover {
    background: #0056b3;
  }
  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #e0f2fe;
    color: #0284c7;
    padding: 20px;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    font-weight: bold;
    font-size: 16px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

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
  