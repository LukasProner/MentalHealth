<template>
  <div>
    <div v-if="loading">
      <p>Načítavam údaje o teste...</p>
    </div>
    <div v-if="error">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="test">
      <h1>Otázky pre test: {{ test.name }}</h1>
      <ul>
        <li v-for="question in test.questions" :key="question.id">
          <div>
            <strong>{{ question.text }}</strong>
          </div>
          <div v-if="question.question_type === 'boolean'">
            <input type="radio" :name="'question-' + question.id" value="true"> Áno
            <input type="radio" :name="'question-' + question.id" value="false"> Nie
          </div>
          <div v-else-if="question.question_type === 'choice'">
            <div v-for="(option, index) in question.options" :key="index">
              <input type="radio" :name="'question-' + question.id" :value="option"> {{ option }}
            </div>
          </div>
          <div v-else-if="question.question_type === 'text'">
            <textarea :name="'question-' + question.id" rows="4" cols="50"></textarea>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      test: null,
      loading: true,
      error: null,
      auth: false
    };
  },
  methods: {
    async checkAuth() {
      try {
        const response = await fetch('http://localhost:8000/api/user/', {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include'
        });

        if (response.ok) {
          const content = await response.json();
          this.auth = !!content.name;
        } else {
          this.auth = false;
        }
      } catch {
        this.auth = false;
      }
    },
    async fetchTest(testId) {
      try {
        const response = await fetch(`http://localhost:8000/api/tests/${testId}/`, {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include'
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        this.test = await response.json();
      } catch (error) {
        this.error = 'Test sa nepodarilo načítať. Skontrolujte, či existuje alebo máte oprávnenie.';
        console.error('Error:', error);
      } finally {
        this.loading = false;
      }
    }
  },
  async created() {
    await this.checkAuth();

    if (!this.auth) {
      this.error = 'Nie ste prihlásený. Prihláste sa na prístup k testu.';
      this.loading = false;
      return;
    }

    const testId = this.$route.params.id;
    await this.fetchTest(testId);
  }
};
</script>
