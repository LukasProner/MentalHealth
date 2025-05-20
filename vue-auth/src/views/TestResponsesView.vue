<template>
  <div class="test-responses">
    <div class="routing">
      <ButtonComp text="Odpovede" fontSize="1rem" @click="goToResponses" />
      <ButtonComp text="Otazky" fontSize="1rem" @click="redirectToQuestions" />
    </div>
    <hr class="line" />
    <div v-if="loading" class="loading">
      <p>Načítavam odpovede...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="responses.length === 0">
      <p class="no-responses">Na tento test ešte nebolo odpovedané.</p>
    </div>
    <div v-else class = "form-container">
      <div v-for="question in sortedQuestions(test.questions)" :key="question.id" class="question-card">
        <div v-if="question.question_type!=='drawing'" class="answers-list">
          <h3>{{ question.text }} </h3>
          <div v-if="question.image_url!==null">
            <img :src="question.image_url" alt="Question Image" class="question-image" />
          </div>
          <ul>
            <li v-for="response in responses" :key="response.submitted_at" class="response-item">
              <div v-for="answer in response.answers" :key="answer.answer_id">
                <div v-if="(answer.question_id) == (question.id)" class="answer">
                  <!-- <div v-if="(answer.question_type) == 'choice'" > -->
                    {{ answer.answer }} 
                  <!-- </div> -->
                </div>
              </div>
            </li>
          </ul>
        </div>
        <div v-else class="drawing-section">
          <h3>{{ question.text }}</h3>
          <p>Táto otázka vyžaduje vizualizáciu.</p>
          <ButtonComp text="Vizualizovať obrázok" @click="redirectToDrawing(question.id)" fontSize="1rem" />
        </div>
      </div>
    </div>
  </div>
</template>
  
<script>
  import { ref, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import ButtonComp from '@/components/ButtonComp.vue';
  import { useStore } from 'vuex';
  
  export default {
    components: {
      ButtonComp,
    },
    setup() {
      const store = useStore();
      const loading = ref(true);
      const error = ref('');
      const responses = ref([]);
      const test = ref(null);
      const route = useRoute();
      const router = useRouter();

      const checkAuth=async()=>{
        try{
          await store.dispatch('checkAuth');
        }catch(err){
          error.value='Chyba pri overovani prihlasenia.';
        } 
      };


      const fetchResponses=async()=>{
        try{
          const response=await fetch(`http://localhost:8000/api/tests/${route.params.id}/responses/`,
            {
              // headers: { 'Content-Type': 'application/json' },
              credentials: 'include',
            }
          );
          if(!response.ok){
            throw new Error(`responses error: ${response.status}`);
          }
          responses.value =await response.json();
        }catch (err){
          error.value ='Odpovede sa nepodarilo načítať. Skontrolujte, či máte oprávnenie.';
          console.error('Error:', err);
        }
      };
  
      const fetchTest=async(testId)=>{
        try{
          // Fetch test vrátane otázok
          const response=await fetch(`http://localhost:8000/api/tests/${testId}/`, {
            // headers:{'Content-Type': 'application/json' },
            credentials:'include',
          });
          if(!response.ok){
            throw new Error(`fetch test error: ${response.status}`);
          }
          test.value =await response.json();
        }catch (err){
          error.value = 'Test sa nepodarilo načítať. Skontrolujte, či existuje alebo máte oprávnenie.';
          console.error('Error:', err);
        }
      };
  
      const redirectToDrawing=(question_id)=>{
        console.log("id otazky",question_id);
        router.push(`/draw/${question_id}/`);
      };
      
      const redirectToQuestions=()=>{
        router.push(`/tests/${route.params.id}/`);
      };

      const goToResponses=()=>{
        router.push(`/tests/${route.params.id}/responses`)
      };
      const sortedQuestions=(questions)=>{
        return [...questions].sort((a,b)=>a.id-b.id);
      } 
      const initializeData=async()=>{
        loading.value=true;
        await Promise.all([fetchTest(route.params.id), fetchResponses()]);
        loading.value=false;
      };
  
      onMounted(async()=>{
        loading.value=true;
        await checkAuth();  
        await initializeData(); 
        loading.value = false;
      });
  
      return{
        error,
        responses,
        test,
        loading,
        redirectToDrawing,
        redirectToQuestions,
        sortedQuestions,
        checkAuth
      };
    },
  };
</script>

<style scoped>
  .test-responses {
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
  .form-container {
    width: 100%;
    margin: 0 auto;
    padding: 20px;
    background: var(--color-background);
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }
  .question-card {
    background: white;
    border-left: 6px solid var(--color-button-hover);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.05);
    transition: 0.3s;
  }
  .question-card:hover {
    background: #f1f1f1;
  }

  .answers-list {
    list-style: none;
    padding: 0;
  }

  .response-item {
    margin-top: 8px;
  }
  .answer {
    background: #e9ecef;
    padding: 10px;
    border-radius: 5px;
    font-size: 1rem;
    margin-top: 5px;
    transition: 0.3s;
  }

  .answer:hover {
    background: #dee2e6;
  }

  .drawing-section {
    text-align: center;
    padding: 10px;
  }
  h3 {
    text-align: left;
    color: var(--color-h1);
    font-size: 1.3rem;
  }
  .drawing-section p {
    font-style: italic;

  }

  /* .drawing-button {
    background: #28a745;
    color: white;
    padding: 8px 15px;
    font-size: 1rem;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: 0.3s;
  }

  .drawing-button:hover {
    background: #218838;
  } */

  .loading, .error, .no-responses {
    text-align: center;
    font-weight: bold;
    font-size: 1.2rem;
    padding: 15px;
    border-radius: 5px;
  }
  .question-image {
    width: 90%;  
    height: auto;  
    display: block;  
    margin: 10px auto;
  }

  .error {
    background-color: #ffdddd;
    color: #d9534f;
  }

  .no-responses {
    background-color: #f8d7da;
    color: #721c24;
  }
</style>
  