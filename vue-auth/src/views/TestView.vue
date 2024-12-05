<!-- <template>
  <div>
    <div v-if="!testId">
      <h1>Vytvoriť test</h1>
      <input v-model="testName" placeholder="Názov testu" />
      <button @click="createTest">Vytvoriť test</button>
    </div>

    <div v-if="testId">
      <h2>Pridať otázky k testu</h2>
      <input v-model="questionText" placeholder="Zadaj otázku" />
      <select v-model="questionType">
        <option value="boolean">Áno/Nie</option>
        <option value="choice">Viac možností</option>
        <option value="text">Textová odpoveď</option>
      </select>

      <div v-if="questionType === 'choice'">
        <h3>Pridať možnosti</h3>
        <input v-model="newOption" placeholder="Zadaj možnosť" />
        <button @click="addOption">Pridať možnosť</button>
        <ul>
          <li v-for="(option, index) in options" :key="index">
            {{ option }} <button @click="removeOption(index)">Odstrániť</button>
          </li>
        </ul>
      </div>

      <button @click="addQuestion">Pridať otázku</button>
    </div>
  </div>
</template>


<script>
export default {
  data() {
    return {
      testName: '',
      testId: null,
      questionText: '',
      questionType: 'boolean',
      options: [],
      newOption: ''
    };
  },
  methods: {
    createTest() {
      const newTest = { name: this.testName };
      fetch('http://localhost:8000/api/tests/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newTest),
        credentials: 'include'
      })
      .then(response => response.json())
      .then(data => {
        this.testId = data.id;
        this.testName = '';
      })
      .catch(console.error);
    },
    addOption() {
      if (this.newOption.trim()) {
        this.options.push(this.newOption.trim());
        this.newOption = '';
      }
    },
    removeOption(index) {
      this.options.splice(index, 1);
    },
    addQuestion() {
      const newQuestion = {
        text: this.questionText,
        question_type: this.questionType,
        options: this.options.join(',') // Spojí možnosti do CSV reťazca
      };
      fetch(`http://localhost:8000/api/tests/${this.testId}/questions/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newQuestion),
        credentials: 'include'
      })
      .then(response => response.json())
      .then(() => {
        this.questionText = '';
        this.questionType = 'boolean';
        this.options = [];
      })
      .catch(console.error);
    }
  }
};
</script> -->

<template>
  <div>
    <div v-if="loading">
      <p>Načítavam údaje...</p>
    </div>
    <div v-if="error">
      <p>{{ error }}</p>
    </div>
    <div v-if="!testId && !loading && !error">
      <h1>Vytvoriť test</h1>
      <input v-model="testName" placeholder="Názov testu" />
      <button @click="createTest">Vytvoriť test</button>
    </div>

    <div v-if="testId && !loading && !error">
      <h2>Pridať otázky k testu</h2>
      <input v-model="questionText" placeholder="Zadaj otázku" />
      <select v-model="questionType">
        <option value="boolean">Áno/Nie</option>
        <option value="choice">Viac možností</option>
        <option value="text">Textová odpoveď</option>
      </select>

      <div v-if="questionType === 'choice'">
        <h3>Pridať možnosti</h3>
        <input v-model="newOption" placeholder="Zadaj možnosť" />
        <button @click="addOption">Pridať možnosť</button>
        <ul>
          <li v-for="(option, index) in options" :key="index">
            {{ option }} <button @click="removeOption(index)">Odstrániť</button>
          </li>
        </ul>
      </div>

      <button @click="addQuestion">Pridať otázku</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';

export default {
  setup() {
    // Prístup k Vuex store
    const store = useStore();

    // Reaktívne premenné
    const testName = ref('');
    const testId = ref(null);
    const questionText = ref('');
    const questionType = ref('boolean');
    const options = ref([]);
    const newOption = ref('');
    const loading = ref(false);
    const error = ref(null);

    // Metóda na overenie prihlásenia používateľa pomocou Vuex akcie
    const checkAuth = async () => {
      loading.value = true;
      try {
        await store.dispatch('checkAuth');
      } catch (err) {
        error.value = 'Chyba pri overovaní prihlásenia.';
      } finally {
        loading.value = false;
      }
    };

    const createTest = () => {
      if (!store.getters.isAuthenticated) {
        error.value = 'Nie ste prihlásený. Prihláste sa, aby ste mohli vytvoriť test.';
        return;
      }

      const newTest = { name: testName.value };
      fetch('http://localhost:8000/api/tests/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newTest),
        credentials: 'include',
      })
      .then(response => response.json())
      .then(data => {
        testId.value = data.id;
        testName.value = '';
      })
      .catch(console.error);
    };

    // Pridanie možnosti / trim - odstrani medzery
    const addOption = () => {
      if (newOption.value.trim()) {
        options.value.push(newOption.value.trim());
        newOption.value = '';
      }
    };

    // Odstránenie možnosti - splice odstrani hodnotu index a iba 1 prvok
    const removeOption = (index) => {
      options.value.splice(index, 1);
    };

    // Pridanie otázky
    const addQuestion = () => {
      if (!store.getters.isAuthenticated) {
        error.value = 'Nie ste prihlásený. Prihláste sa, aby ste mohli pridávať otázky.';
        return;
      }

      const newQuestion = {
        text: questionText.value,
        question_type: questionType.value,
        options: options.value.join(','), // Spojí možnosti do CSV reťazca
      };
      fetch(`http://localhost:8000/api/tests/${testId.value}/questions/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newQuestion),
        credentials: 'include',
      })
      .then(response => response.json())
      .then(() => {
        questionText.value = '';
        questionType.value = 'boolean';
        options.value = [];
      })
      .catch(console.error);
    };

    // Zavoláme overenie prihlásenia pri načítaní komponentu
    onMounted(() => {
      checkAuth();
    });

    // Vrátime premenné a metódy, ktoré budú použité v šablóne
    return {
      testName,
      testId,
      questionText,
      questionType,
      options,
      newOption,
      loading,
      error,
      createTest,
      addOption,
      removeOption,
      addQuestion,
    };
  }
};
</script>
