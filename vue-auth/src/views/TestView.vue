<template>
  <div>
    <!-- Načítavanie a chybové hlásenia -->
    <div v-if="loading">
      <p>Načítavam údaje...</p>
    </div>
    <div v-if="error">
      <p>{{ error }}</p>
    </div>

    <!-- Formulár pre vytvorenie testu -->
    <div v-if="!testId && !loading && !error">
      <h1>Vytvoriť test</h1>
      <input v-model="testName" placeholder="Názov testu" />
      <button @click="createTest">Vytvoriť test</button>
    </div>

    <!-- Formulár pre pridávanie otázok k testu -->
    <div v-if="testId && !loading && !error">
      <h2>
        <span v-if="!isEditing" @dblclick="enableEditing">{{ testName }}</span>
        <input
          v-else
          v-model="editedName"
          @blur="saveTestName"
          @keydown.enter="saveTestName"
        />
      </h2>
      
      <!-- Zoznam pridanych otázok -->
      <div v-if="questions.length > 0">
        <h3>Otázky:</h3>
        <ul>
          <li v-for="(question, index) in questions" :key="question.id">
            <p>{{ question.text }}</p>
            <button @click="deleteQuestion(question.id, index)">Odstrániť</button>
          </li>
        </ul>
      </div>

      <input v-model="questionText" placeholder="Zadaj otázku" />
      <select v-model="questionType">
        <option value="boolean">Áno/Nie</option>
        <option value="choice">Viac možností</option>
        <option value="text">Textová odpoveď</option>
      </select>

      <!-- Pre otázky typu "choice" pridávanie možností -->
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
    const store = useStore();

    // Reaktívne premenné
    const testName = ref('');
    const editedName = ref('');
    const isEditing = ref(false);
    const testId = ref(null);
    const questionText = ref('');
    const questionType = ref('boolean');
    const options = ref([]);
    const newOption = ref('');
    const loading = ref(false);
    const error = ref(null);
    const questions = ref([]); // Premenná pre uloženie otázok

    // Overenie prihlásenia
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

    // Vytvorenie testu
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
        .then((response) => response.json())
        .then((data) => {
          testId.value = data.id;
          testName.value = newTest.name;
          editedName.value = newTest.name;
        })
        .catch(console.error);
    };

    // Povoliť režim úprav
    const enableEditing = () => {
      isEditing.value = true;
      editedName.value = testName.value;
    };

    // Uložiť upravený názov testu
    const saveTestName = () => {
      if (editedName.value.trim() === testName.value) {
        isEditing.value = false;
        return;
      }

      fetch(`http://localhost:8000/api/tests/${testId.value}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: editedName.value }),
        credentials: 'include',
      })
        .then((response) => {
          if (response.ok) {
            testName.value = editedName.value;
          } else {
            throw new Error('Nepodarilo sa uložiť názov testu.');
          }
        })
        .catch((err) => {
          error.value = err.message;
        })
        .finally(() => {
          isEditing.value = false;
        });
    };

    // Pridanie možnosti pre otázku typu "choice"
    const addOption = () => {
      if (newOption.value.trim()) {
        options.value.push(newOption.value.trim());
        newOption.value = '';
      }
    };

    // Odstránenie možnosti
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
        options: options.value.join(','), // Možnosti sú spojené do CSV reťazca
      };

      // Poslanie otázky na backend
      fetch(`http://localhost:8000/api/tests/${testId.value}/questions/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newQuestion),
        credentials: 'include',
      })
        .then((response) => response.json())
        .then((data) => {
          questions.value.push(data); // Pridanie otázky do zoznamu
          questionText.value = ''; // Resetovanie textu otázky
          questionType.value = 'boolean'; // Resetovanie typu otázky
          options.value = []; // Resetovanie možností
        })
        .catch(console.error);
    };

    // Odstránenie otázky
    const deleteQuestion = (questionId, index) => {
      fetch(`http://localhost:8000/api/questions/${questionId}/`, {
        method: 'DELETE',
        credentials: 'include',
      })
        .then((response) => {
          if (response.ok) {
            // Odstrániť otázku z lokálneho zoznamu
            console.log("no co je toto")
            questions.value.splice(index, 1);
          } else {
            throw new Error('Nepodarilo sa odstrániť otázku.');
          }
        })
        .catch((err) => {
          error.value = err.message;
        });
    };

    // Načítanie komponentu
    onMounted(() => {
      checkAuth();
    });

    return {
      testName,
      editedName,
      isEditing,
      testId,
      questionText,
      questionType,
      options,
      newOption,
      loading,
      error,
      questions, // Zoznam otázok
      createTest,
      enableEditing,
      saveTestName,
      addOption,
      removeOption,
      addQuestion,
      deleteQuestion, // Funkcia na odstránenie otázky
    };
  },
};
</script>
