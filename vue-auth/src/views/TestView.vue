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
      <select v-model="answer">
        <option :value="true">Áno</option>
        <option :value="false">Nie</option>
      </select>
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
      answer: true
    };
  },
  methods: {
    createTest() {
      const newTest = { name: this.testName };
      fetch('http://localhost:8000/api/tests/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newTest)
      })
      .then(response => response.json())
      .then(data => {
        this.testId = data.id; // Uloženie ID nového testu
        this.testName = ''; // Reset názvu testu
      });
    },
    addQuestion() {
      const newQuestion = { text: this.questionText, answer: this.answer };
      fetch(`http://localhost:8000/api/tests/${this.testId}/questions/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newQuestion)
      })
      .then(response => response.json())
      .then(data => {
        this.questionText = ''; // Reset textu otázky
      });
    }
  }
};
</script>