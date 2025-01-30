<!-- 
<template>
  <div v-if="test">
    <h1>{{ test.name }}</h1>
    <button @click="goToResponses" >Odpovede</button>
    <form>
      <div v-for="question in sortedQuestions(test.questions)" :key="question.id">
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
    <ExportData :testId="test.id" />
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

export default {
  components: {
    ExportData,
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
      router.push(`${route.params.id}/responses`)
    }

    return {
      answers,
      test,
      error,
      loading,
      testCode, // Pridávame testový kód
      goToResponses,
      sortedQuestions
    };
  },
};
</script> -->

<template>
  <ul>
    <li v-for="(question) in questions" :key="question.id">
    
      <!-- Ak sa otázka neupravuje, zobraz normálny text -->
      <div v-if="!isEditingQuestion(question)">
        <p><strong>Otázka:</strong> {{ question.text }}</p>
        <p><strong>Typ otázky:</strong> {{ question.type }}</p>

        <ul v-if="question.options.length > 0">
          <li v-for="(option, optIndex) in question.options" :key="optIndex">
            <p>{{ option.text }} <span v-if="option.hasValue">(Hodnota: {{ option.value }})</span></p>
          </li>
        </ul>

        <button @click="enableEditing(question)">Upraviť otázku</button>
        <button @click="deleteQuestion(question.id)">Odstrániť</button>
      </div>

      <!-- Formulár na úpravu otázky -->
      <div v-else>
        <input v-model="question.text" placeholder="Zadajte novú otázku" />

        <select v-model="question.type">
          <option value="boolean">Áno/Nie</option>
          <option value="choice">Viac možností</option>
          <option value="text">Textová odpoveď</option>
          <option value="drawing">Kreslenie</option>
        </select>

        <!-- Ak je otázka typu "choice", zobraz možnosti -->
        <div v-if="question.type === 'choice'">
          <h3>Možnosti odpovedí</h3>
          <div v-for="(option, optIndex) in question.options" :key="optIndex">
            <input v-model="option.text" placeholder="Upravte možnosť" />
            <label>
              <input type="checkbox" v-model="option.hasValue" />
              Pridať hodnotenie
            </label>
            <input v-if="option.hasValue" type="number" v-model.number="option.value" placeholder="Hodnota" />
            <button @click="removeOption(question, optIndex)">Odstrániť</button>
          </div>
          <button @click="addOption(question)">Pridať možnosť</button>
        </div>

        <!-- Pre ostatné typy otázok -->
        <div v-else>
          <!-- Môžeš pridať ďalšiu logiku pre iné typy otázok -->
          <button @click="disableEditing(question)">Uložiť</button>
        </div>
      </div>
    </li>
  </ul>
</template>

<script>
export default {
  data() {
    return {
      questions: [
        {
          id: 1,
          text: "Je obloha modrá?",
          type: "boolean",
          options: [],
        },
        {
          id: 2,
          text: "Aké je hlavné mesto Slovenska?",
          type: "choice",
          options: [
            { text: "Bratislava", hasValue: false, value: 0 },
            { text: "Košice", hasValue: false, value: 0 },
          ],
        }
      ],
      // Pre ukladanie dočasného stavu úpravy otázky, nie je to súčasť databázy
      editingQuestion: null
    };
  },
  methods: {
    // Funkcia na povolenie úpravy otázky
    enableEditing(question) {
      this.editingQuestion = question; // Nastavíme otázku, ktorú upravujeme
    },

    // Funkcia na uloženie zmien a zrušenie úpravy
    disableEditing(question) {
      // Ak nie je typ otázky "choice", odstránime možnosti
      if (question.type !== "choice") {
        question.options = [];
      }
      this.editingQuestion = null; // Ukončíme úpravy
    },

    // Pridanie novej možnosti k otázke
    addOption(question) {
      question.options.push({ text: "", hasValue: false, value: 0 });
    },

    // Odstránenie možnosti zo zoznamu odpovedí
    removeOption(question, optIndex) {
      question.options.splice(optIndex, 1);
    },

    // Odstránenie otázky
    deleteQuestion(id) {
      this.questions = this.questions.filter(q => q.id !== id);
    },

    // Funkcia na zistenie, či je otázka v režime úpravy
    isEditingQuestion(question) {
      return this.editingQuestion === question;
    }
  }
};
</script>
