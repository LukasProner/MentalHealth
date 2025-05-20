
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
        <div v-if="question.image_url!==null">
          <img :src="question.image_url" alt="Question Image" class="question-image" />
        </div>
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
    <div style="display: flex; justify-content: center; margin: 20px 0 30px 0; gap: 10px;"> 
      <ExportData :testId="test.id" class="export"/>
      <SendDataComp :testId="test.id" :testCode="test.test_code" class="export"/>
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
    const store=useStore();  
    const route=useRoute(); 
    const router=useRouter();

    const answers=ref({});
    const test=ref(null);
    const testCode=ref('');  
    const error=ref('');
    const loading=ref(true);

    const fetchTest=async(testId)=>{
      try {
        const response = await fetch(`http://localhost:8000/api/tests/${testId}/`,{
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        test.value = await response.json();
        console.log(test.value)
      }catch(err){
        error.value = 'Test sa nepodarilo načítať. Skontrolujte, či existuje alebo máte oprávnenie.';
        console.error('Error:',err);
      }finally{
        loading.value = false;
      }
    };

    const init=async()=>{
      await store.dispatch('checkAuth');
      if(store.getters.isAuthenticated){
        const testId = route.params.id; 
        await fetchTest(testId);
      }else{
        error.value = 'Nie ste prihlásený. Prihláste sa na prístup k testu.';
        loading.value = false;
      }
    };
    init();
    
    onMounted(init);

    const sortedQuestions=(questions)=>{
        return [...questions].sort((a, b)=>a.id-b.id);
    };
  


    const goToResponses=()=>{
      router.push(`/tests/${route.params.id}/responses`)
    };
    const redirectToQuestions=()=>{
      router.push(`/tests/${route.params.id}/`);
    };

    return{
      answers,
      test,
      error,
      loading,
      testCode,  
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
    border-radius: 2px;  
    width: 100%;
    margin-top: 10px;
  }
  h1 {
    text-align: center ;
  }

  .form-container {
    width: 100%;
    margin: 0 auto;
    padding: 20px;
    background: var(--color-background);
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }
  .question-card{
    background-color: white;
    border-left: 6px solid var(--color-lightblue);
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
  .question-image {
    width: 90%;  
    height: auto;  
    display: block;  
    margin: 10px auto;
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
