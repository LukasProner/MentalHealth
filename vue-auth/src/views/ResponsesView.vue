<template>
    <div>
        <h1>Odpovede</h1>
        <div v-if="loading">
            <p>Načítavam odpovede...</p>
        </div>
        <div v-else-if="error">
            <p>{{ error }}</p>
        </div>
        <div v-else>
            <div v-for="response in responses" :key="response.submitted_at">
                <h2>{{ response.submitted_at }}</h2>
                <ul>
                    <li v-for="answer in response.answers" :key="answer.answer_id">
                        <strong>{{ answer.question }}</strong> {{ answer.answer }} 
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>
<script>
import {ref,onMounted} from 'vue';
import { useRoute } from 'vue-router';

export default{
    setup(){
        const loading = ref(true);
        const error = ref('');
        const responses = ref([]);
        const route = useRoute();
    
        const fetchResponses = async()=>{
            try{
                const response = await fetch(`http://localhost:8000/api/tests/${route.params.id}/responses/`,{
                    headers: {'Content-Type': 'application/json'},
                    credentials:'include',
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
            responses.value = await response.json();
            } catch (err) {
                error.value = 'Odpovede sa nepodarilo načítať. Skontrolujte, či máte oprávnenie.';
                console.error('Error:', err);
            } finally {
                loading.value = false;
            }
        };
        onMounted(fetchResponses);
        return{
            error,
            responses,
            loading,
        }
    }
}
</script>





<!-- <template>
    <div>
      <h1>Odpovede na test</h1>
      <div v-if="loading">
        <p>Načítavam odpovede...</p>
      </div>
      <div v-else-if="error">
        <p>{{ error }}</p>
      </div>
      <div v-else>
        <div v-for="response in responses" :key="response.submitted_at">
          <h2>Odoslané: {{ response.submitted_at }}</h2>
          <ul>
            <li v-for="answer in response.answers" :key="answer.question">
              <strong>{{ answer.question }}:</strong> {{ answer.answer }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { useRoute } from 'vue-router';
  
  export default {
    setup() {
      const route = useRoute();
      const responses = ref([]);
      const error = ref('');
      const loading = ref(true);
  
      const fetchResponses = async () => {
        try {
          const response = await fetch(`http://localhost:8000/api/tests/${route.params.id}/responses/`, {
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
          });
  
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
  
          responses.value = await response.json();
        } catch (err) {
          error.value = 'Odpovede sa nepodarilo načítať. Skontrolujte, či máte oprávnenie.';
          console.error('Error:', err);
        } finally {
          loading.value = false;
        }
      };
  
      onMounted(fetchResponses);
  
      return {
        responses,
        error,
        loading,
      };
    },
  };
  </script>
   -->