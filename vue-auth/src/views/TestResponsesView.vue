<template>
    <div>
      <div class="routing">
        <ButtonComp text="Odpovede" fontSize="1rem" @click="goToResponses" />
        <ButtonComp text="Otazky" fontSize="1rem" @click="redirectToQuestions" />
      </div>
      <div v-if="loading">
        <p>Načítavam odpovede...</p>
      </div>
      <div v-else-if="error">
        <p>{{ error }}</p>
      </div>
      <div v-else>
        <div v-for="question in sortedQuestions(test.questions)" :key="question.id">
          <div v-if="question.question_type !== 'drawing'">
            <h2>{{ question.text }} </h2>
            <ul>
              <li v-for="response in responses" :key="response.submitted_at">
                <!-- {{ response }} -->
                <div v-for="answer in response.answers" :key="answer.answer_id">
                    <!-- {{ answer.answer }} - {{ answer.question_id }} - {{ question.id }} -->
                    <div v-if="(answer.question_id) == (question.id)">
                        {{ answer.answer }}
                    </div>
                </div>
              </li>
            </ul>
          </div>
          <div v-else>
            <h2>{{ question.text }}</h2>
            <p>Táto otázka vyžaduje vizualizáciu.</p>
            <button @click="redirectToDrawing(question.id)">Vizualizovať obrázok</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import ButtonComp from '@/components/ButtonComp.vue';
  
  export default {
    components: {
      ButtonComp,
    },
    setup() {
      
      const loading = ref(true);
      const error = ref('');
      const responses = ref([]);
      const test = ref(null);
      const route = useRoute();
      const router = useRouter();
  
      const fetchResponses = async () => {
        try {
          // Fetch odpovede
          const response = await fetch(
            `http://localhost:8000/api/tests/${route.params.id}/responses/`,
            {
              headers: { 'Content-Type': 'application/json' },
              credentials: 'include',
            }
          );
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          responses.value = await response.json();
          console.log("No toto som este nevudel",responses.value);
        } catch (err) {
          error.value = 'Odpovede sa nepodarilo načítať. Skontrolujte, či máte oprávnenie.';
          console.error('Error:', err);
        }
      };
  
      const fetchTest = async (testId) => {
        try {
          // Fetch test vrátane otázok
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
        }
      };
  
      const redirectToDrawing = () => {
        router.push(`/draw/${route.params.id}/`);
      };
      
      const redirectToQuestions = () => {
        router.push(`/tests/${route.params.id}/`);
      };

      const goToResponses = () =>{
        router.push(`/tests/${route.params.id}/responses`)
      };
      const sortedQuestions = (questions) => {
        return [...questions].sort((a,b)=>a.id-b.id);
      } 
      const initializeData = async () => {
        loading.value = true;
        await Promise.all([fetchTest(route.params.id), fetchResponses()]);
        loading.value = false;
      };
  
      onMounted(initializeData);
  
      return {
        error,
        responses,
        test,
        loading,
        redirectToDrawing,
        redirectToQuestions,
        sortedQuestions,
      };
    },
  };
  </script>
  