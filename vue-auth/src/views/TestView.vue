<template>
  <div>
    <!-- Načítavanie a chybové hlásenia -->
    <div v-if="loading" class="loading">
      <p>Načítavam údaje...</p>
    </div>
    <div v-if="error" class="error">
      <p>{{ error }}</p>
    </div>

    <div v-if="!testId && !loading && !error" class="create-test">
      <h1>Vytvoriť test</h1>
      <input v-model="testName" placeholder="Názov testu" />
      <ButtonComp text="Vytvoriť test" fontSize="1rem" @click="createTest" />
    </div>

<!-- som prihlaseny -->
    <div v-if="testId && !loading && !error" class="test">
      <h2 class="test-name" @click="enableEditing">
        <span v-if="!isEditing" >{{ testName }}</span>
        <input
          v-else
          v-model="editedName"
          @blur="saveTestName"
          @keydown.enter="saveTestName"
        />
      </h2>
      <h3 class="test-code">Kód testu : {{testCode}}</h3>
      
      <div v-if="questions.length > 0">
       
        <ul>
          <li v-for="(question, index) in questions" :key="question.id">
            <div v-if="!isEditingQuestion(question)">
              <p>{{ question.text }}</p>
              <ul v-if="question.options && question.options.length > 0">
                <li v-for="(option, index) in question.options" :key="index">
                  <p>{{ option.text }}</p>
                  <p v-if="option.hasValue">Hodnota: {{ option.value }}</p>
                </li>
              </ul>
              <div v-if="question.showCategoryInput">
                <p >Aktuálna kategória: {{ question.category }}</p>
                <input 
                  v-model="question.newCategory" 
                  placeholder="Zadajte novú kategóriu" 
                  @blur="saveCategory(index)"
                />
              </div>

              <button @click="toggleCategoryInput(index)">Pridať kategóriu</button>
              <button @click="enableEditingQuestion(question)">Upraviť otázku</button>
              <button @click="deleteQuestion(question.id, index)">Odstrániť</button>
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
                <button @click="addOptionUpdate(question)">Pridať možnosť</button>
              </div>
              <button @click="disableEditingQuestion(question)">Uložiť</button>

              <!-- <div v-else>
                <button @click="disableEditingQuestion(question)">Uložiť</button>
              </div> -->
            </div>
          </li>
        </ul>
      </div>
      
      <!-- pridávanie nových otázok -->

      <div class="question-form">
      <input
        v-model="questionText"
        placeholder="Zadaj otázku"
        class="input-field question-input"
      />
      <select v-model="questionType" class="input-field select-field">
        <option value="boolean">Áno/Nie</option>
        <option value="choice">Viac možností</option>
        <option value="text">Textová odpoveď</option>
        <option value="drawing">Kreslenie</option>
      </select>

      <div v-if="questionType === 'choice'" class="options-section">
        <h3>Pridať možnosti</h3>
        <div
          v-for="(option, index) in options"
          :key="index"
          class="option-item"
        >
          <input
            v-model="option.text"
            placeholder="Zadaj možnosť"
            class="input-field option-input"
          />
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="option.hasValue"
              class="checkbox-input"
            />
            Pridať hodnotenie
          </label>
          <input
            v-if="option.hasValue" type="number" v-model.number="option.value" placeholder="Hodnota" class="input-field value-input"
          />
          <button @click="removeOption(index)" class="button remove-button">
            Odstrániť
          </button>
        </div>
        <button @click="addOption" class="button add-option-button">
          Pridať novú možnosť
        </button>
      </div>

      <div class="buttons-container">
        <button @click="addQuestion" class="button primary-button">
          Pridať otázku
        </button>
        <button @click="chooseDefaultTest" class="button secondary-button">
          {{ isTestOpen ? "Zavrieť" : "Pridať test" }}
        </button>
      </div>

      <div v-if="isTestOpen" class="test-selection">
        <h2>Vyber test</h2>
        <ul class="test-list">
          <li
            v-for="test in defaultTests"
            :key="test.id"
            @click="selectTest(test)"
            class="test-item"
          >
            {{ test.name }}
          </li>
        </ul>
      </div>
    </div>
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
        <input 
          v-model="scale.category" 
          placeholder="Vyber kategoriu" 
        />
        <button @click="removeScale(index)">Odstrániť</button>
      </div>
      <button @click="addScale">Pridať nové škálovanie</button>

      <!-- Uložiť škálovanie -->
      <button @click="actualizeScales">Uložiť škálovanie</button>
      <Import :testId="testId" @import-complete="handleImportComplete" />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import Import from '../components/Import.vue';
import ButtonComp from '../components/ButtonComp.vue';

export default {
  components: {
    Import,
    ButtonComp
  },
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
    const defaultTests = ref([]);
    const isTestOpen = ref(false);
    const editingQuestion = ref(null);

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
    const enableEditingQuestion = (question) => {
      editingQuestion.value = question; // Nastavíme otázku, ktorú upravujeme
    };
    const isEditingQuestion = (question) => {
      return editingQuestion.value === question;
    };
    const disableEditingQuestion =async(question) => {
      // Ak nie je typ otázky "choice", odstránime možnosti
      console.log('disableEditingQuestion',question)
      console.log('disableType',question.type)
      if (question.type !== "choice") {
        question.options = [];
      }
      try {
        // Príprava dát na aktualizáciu
        const updatedData = {
          text: question.text,
          question_type: question.type,
          options: question.options,
          category: question.category,
        };

        // Volanie funkcie na aktualizáciu otázky na serveri
        const updatedQuestion = await updateQuestion(question.id, updatedData);

        // Po úspešnej aktualizácii môžeme nastaviť otázku ako neaktívnu pre editáciu
        editingQuestion.value = null; // Ukončíme úpravy
        console.log('Otázka bola aktualizovaná:', updatedQuestion);
      } catch (error) {
        console.error('Chyba pri aktualizácii otázky:', error);
      }
      editingQuestion.value = null; // Ukončíme úpravy
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
  const addOptionUpdate = (question)=> {
    question.options.push({ text: "", hasValue: false, value: null });
  };

  const removeOption = (index) => {
    options.value.splice(index, 1);
  };

  const chooseDefaultTest = () =>{
    isTestOpen.value = !isTestOpen.value
    return null
  }

  const fetchDefaultTests = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/tests/default/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include', 
      });
      console.log('response',response)

      if (!response.ok) {
        throw new Error(`HTTP chyba! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log('data',data)
      defaultTests.value = data.tests;
    } catch (err) {
      error.value = 'Chyba pri načítavaní testov. Skontrolujte autentifikáciu.';
      console.error('Error:', err);
    } finally {
      loading.value = false;
    }
  };

  const selectTest = async (test) => {
    try {
      const response = await fetch(`http://localhost:8000/api/tests/${test.id}/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP chyba! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Questions from selected test:', data.questions);
      questions.value.push(...data.questions.sort((a, b) => a.id - b.id));

      // Iterácia cez otázky a ich uloženie k aktuálnemu testu
      for (const question of data.questions) {
        const newQuestion = {
          text: question.text,
          question_type: question.question_type,
          options: question.options || [],
          category: question.category || 'Nezaradená',
        };

        // Voláme API na pridanie otázky
        await fetch(`http://localhost:8000/api/tests/${testId.value}/questions/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newQuestion),
          credentials: 'include',
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error(`Chyba pri ukladaní otázky: ${response.status}`);
            }
            return response.json();
          })
          // .then((savedQuestion) => {
          //   questions.value.push(savedQuestion);
          // })
          .catch((err) => {
            console.error('Chyba pri ukladaní otázky:', err);
          });
      }
      console.log(data)
      const scale_response = await fetch(`http://localhost:8000/api/tests/${test.id}/scales/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });
      if (!response.ok) {
        throw new Error(`HTTP chyba! Status: ${response.status}`);
      }
      const temp_scales = await scale_response.json();
      console.log('Scales from selected test:', temp_scales);

      await fetch(`http://localhost:8000/api/tests/${testId.value}/scales/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(temp_scales),
        credentials: 'include',
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`Chyba pri ukladaní škál: ${response.status}`);
          }
          return response.json();
        })
        .then((savedScales) => {
          console.log('Uložené škály:', savedScales);
        })
        .catch((err) => {
          console.error('Chyba pri ukladaní škál:', err);
        });

      
      isTestOpen.value = false; 
    } catch (err) {
      error.value = 'Chyba pri načítavaní otázok z vybraného testu.';
      console.error('Error:', err);
    }
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
        console.log('Response data:', data); 
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
      console.log('Aktualizujem otázku:', questionId, updatedData);
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
          throw new Error(`Chyba pri aktualizácii: ${response.statusText}`);
        }

        const responseData = await response.json(); // Parsovanie odpovede na JSON
        // console.log('Otázka bola aktualizovaná:', responseData);
        return responseData;
      } catch (error) {
        console.error('Chyba pri aktualizácii otázky:', error);
        throw error; // Re-throw, ak potrebuješ chybu ošetriť vyššie
      }
    };

    const addScale = () => {
      scales.value.push({ min: 0, max: 0, response: '' });
    };

    const removeScale = (index) => {
      scales.value.splice(index, 1);
    };

    const saveScales = () => {
      const formattedScales = scales.value.map((scale) => ({
          min_points: scale.min,
          max_points: scale.max,
          response: scale.response,
          category: scale.category,
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
    const actualizeScales = async () => {
      try {
          const response = await fetch(`http://localhost:8000/api/tests/${testId.value}/scales/`, {
              method: 'DELETE',
              headers: {
                  'Content-Type': 'application/json',
              },
          });

          if (!response.ok) {
              const error = await response.json();
              console.error('Chyba pri odstránení škál:', error);
              throw new Error(error.detail || 'Chyba pri odstraňovaní škál');
          }
          saveScales();
      } catch (error) {
          console.error('Chyba pri aktualizácii škál:', error.message || error);
      }
    };

    const toggleCategoryInput = (index) => {
      const question = questions.value[index];
      question.showCategoryInput = !question.showCategoryInput;
    };
    const saveCategory = (index) => {
      const question = questions.value[index];
      if (question.newCategory) {

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
    const handleImportComplete = async (data,scalesData) => {
        console.log("Import bol úspešne dokončený!");
        for (const question of data) {
            try {
                questions.value.push(question);
            } catch (error) {
                console.error("Chyba pri pridávaní otázky:", error);
            }
        }
        for (const scale of scalesData) {
            try {
              scales.value.push({
                min: scale.min_points,
                max: scale.max_points,
                response: scale.response,
                category: scale.category
            });
              // scales.value.push({ scale.min_points, scale.max_points, scale.response, scale.category });
            } catch (error) {
                console.error("Chyba pri pridávaní scale:", error);
            }
        }
    };

    // Načítanie komponentu
    onMounted(() => {
      checkAuth();
      fetchDefaultTests();
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
      chooseDefaultTest,
      isTestOpen,
      defaultTests,
      selectTest,
      handleImportComplete,
      actualizeScales,
      enableEditingQuestion,
      editingQuestion,
      disableEditingQuestion,
      isEditingQuestion,
      addOptionUpdate,
    };
  },
};
</script>

<style scoped>
h3 {
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 10px;
}
.create-test {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: #f9fafb;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  margin: 20px auto;
}

.create-test input {
  width: 80%;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  outline: none;
  margin-bottom: 16px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.create-test input:focus {
  border-color: var(--color-lightblue);
}

.create-test button {
  background-color: var(--color-lightblue);
  color: var(--color-h1);
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
  transition: background-color 0.3s ease;
}
.test{
  border-radius: 8px;
  padding: 15px;
  margin: 10px 0;
  max-width: 800px;
  margin: auto;
  text-align: center;
}

.test-name {
  background-color: #f9f9f9;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
  position: relative;
  transition: all 0.3s ease-in-out;
}

.test-name span {
  cursor: pointer;
  color: var(--color-primary);
}

.test-name input {
  font-size: 1.8rem;
  padding: 10px;
  width: 100%;
  background-color: #fff;
  border: 2px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
  transition: border-color 0.2s ease;
}

.test-name input:focus {
  border-color: var(--color-primary);
  outline: none;
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
