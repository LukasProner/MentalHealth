<template>
    <div>
      <h1>Odpovede na test</h1>
      <div v-if="submission">
        <h2>{{ submission.test_name }}</h2>
        <ul>
          <li v-for="answer in submission.answers" :key="answer.question_text">
            <strong>{{ answer.question_text }}</strong> ({{ answer.question_type }}): {{ answer.answer }}
          </li>
        </ul>
      </div>
      <div v-else>
        <p>Načítavam odpovede...</p>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        submission: null,
      };
    },
    created() {
      const testCode = "získaj_kód_testu"; // Zmeňte podľa potreby
      fetch(`/api/submissions/${testCode}/`)
        .then((response) => response.json())
        .then((data) => {
          this.submission = data;
        })
        .catch((error) => {
          console.error("Error fetching submission:", error);
        });
    },
  };
  </script>
  