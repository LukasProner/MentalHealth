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
      <h3>Kód testu : {{testCode}}</h3>
      
      <!-- Zoznam pridanych otázok -->
      <div v-if="questions.length > 0">
        <h3>Otázky:</h3>
        <ul>
          <li v-for="(question, index) in questions" :key="question.id">
            <p>{{ question.text }}</p>
            <button @click="toggleCategoryInput(index)">Pridať kategóriu</button>

            <!-- Textové pole na zadanie kategórie -->
            <div v-if="question.showCategoryInput">
              <input 
                v-model="question.newCategory" 
                placeholder="Zadajte novú kategóriu" 
                @blur="saveCategory(index)"
              />
            </div>
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

      <div v-if="questionType === 'choice'">
        <h3>Pridať možnosti</h3>
        <div v-for="(option, index) in options" :key="index" class="option-item">
          <input v-model="option.text" placeholder="Zadaj možnosť" />
          <label>
            <input type="checkbox" v-model="option.hasValue" />
            Pridať hodnotenie
          </label>
          <input 
            v-if="option.hasValue" 
            type="number" 
            v-model.number="option.value" 
            placeholder="Hodnota" 
          />
          <button @click="removeOption(index)">Odstrániť</button>
        </div>
        <button @click="addOption">Pridať novú možnosť</button>
      </div>
      <button @click="addQuestion">Pridať otázku</button>
    </div>
    
    <!-- Sekcia pre škalovanie testu -->
    <div v-if="testId && !loading && !error">
      <h3>Škalovanie výsledkov</h3>
      <div v-for="(scale, index) in scales" :key="index" class="scale-item">
        <input 
          type="number" 
          v-model.number="scale.min" 
          placeholder="Minimálne body" 
        />
        <input 
          type="number" 
          v-model.number="scale.max" 
          placeholder="Maximálne body" 
        />
        <input 
          v-model="scale.response" 
          placeholder="Odpoveď (napr. Výborný výkon)" 
        />
        <button @click="removeScale(index)">Odstrániť</button>
      </div>
      <button @click="addScale">Pridať nové škálovanie</button>

      <!-- Uložiť škálovanie -->
      <button @click="saveScales">Uložiť škálovanie</button>
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
    const questions = ref([]); 
    const scales = ref([]);
    const testCode = ref([]);
    const questionCategory= ref('');

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
          return fetch(`http://localhost:8000/api/tests/${data.id}/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        });
      })
      .then((response) => response.json())
      .then((testDetails) => {
        // Tu môžete spracovať detaily testu vrátane kódu
        console.log('Test details:', testDetails);
        testCode.value = testDetails.test_code; // Príklad - ak je vrátený "code"
        console.log('Test code', testCode)
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

  const addOption = () => {
    options.value.push({ text: '', hasValue: false, value: null }); // Predvolene nemá hodnotenie
  };


  const removeOption = (index) => {
    options.value.splice(index, 1);
  };

  const addQuestion = () => {
    const newQuestion = {
      text: questionText.value,
      question_type: questionType.value,
      options: options.value, 
      category: questionCategory.value || 'Nezaradená'
    };

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
        questions.value.push(data);
        questionText.value = '';
        questionType.value = 'boolean';
        options.value = [];
        questionCategory.value = ''; 
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

    const updateQuestion = async (questionId, updatedData) => {
      try {
        const response = await fetch(`http://localhost:8000/api/questions/${questionId}/`, {
          method: 'PUT', 
          headers: {
            'Content-Type': 'application/json', // Označenie, že telo požiadavky je JSON
          },
          credentials: 'include', // Zabezpečenie, že cookies (napr. JWT) budú odoslané
          body: JSON.stringify(updatedData), // Serializácia dát na JSON
        });

        if (!response.ok) {
          // Ak odpoveď nie je úspešná (napr. 4xx alebo 5xx)
          throw new Error(`Chyba pri aktualizácii: ${response.statusText}`);
        }

        const responseData = await response.json(); // Parsovanie odpovede na JSON
        console.log('Otázka bola aktualizovaná:', responseData);
        return responseData;
      } catch (error) {
        console.error('Chyba pri aktualizácii otázky:', error);
        throw error; // Re-throw, ak potrebuješ chybu ošetriť vyššie
      }
    };
    // Pridanie nového škálovania
    const addScale = () => {
      scales.value.push({ min: 0, max: 0, response: '' });
    };

    // Odstránenie škálovania
    const removeScale = (index) => {
      scales.value.splice(index, 1);
    };

    const saveScales = () => {
      // Upraviť formát scales na to, čo očakáva backend
      const formattedScales = scales.value.map((scale) => ({
          min_points: scale.min,
          max_points: scale.max,
          response: scale.response,
      }));

      fetch(`http://localhost:8000/api/tests/${testId.value}/scales/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formattedScales),
        credentials: 'include',
      })
        .then((response) => {
            if (!response.ok) {
                return response.json().then((err) => {
                    console.error('Backendová chyba (plná odpoveď):', err);
                    throw new Error(
                        err.detail || JSON.stringify(err) || 'Neznáma chyba'
                    );
                });
            }
            return response.json();
        })
        .then((data) => {
            console.log('Scales uložené:', data);
        })
        .catch((err) => {
            console.error('Chyba pri ukladaní:', err.message || err);
        });
      };


    const toggleCategoryInput = (index) => {
      const question = questions.value[index];
      question.showCategoryInput = !question.showCategoryInput;
    };
    const saveCategory = (index) => {
      const question = questions.value[index];
      console.log('savujem categoriu')
      if (question.newCategory) {
        console.log('savujem categoriu2')

        question.category = question.newCategory;
        console.log(question.category)
        question.newCategory = ''; // Resetovať textové pole
      }
      question.showCategoryInput = false; // Skryť input po uložení
      updateQuestion(question.id, { 
        category: question.category, // Aktualizovaná kategória
        text: question.text, // Nezabudni na text otázky (ak je povinný)
        question_type: question.question_type // Ak je potrebný aj typ otázky
      })
      .then(response => {
        console.log('Kategória bola úspešne aktualizovaná:', response);
      })
      .catch(error => {
        console.error('Chyba pri aktualizácii kategórie:', error);
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
      scales,
      addScale,
      removeScale,
      saveScales,
      testCode,
      toggleCategoryInput,
      saveCategory,
      updateQuestion,
    };
  },
};
</script>
