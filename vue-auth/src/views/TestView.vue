<template>
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
</script>
