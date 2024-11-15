<template>
  <div>
    <!-- Zobrazí informáciu o načítavaní, kým sa dáta načítajú -->
    <div v-if="!test">
      <p>Načítavam údaje o teste...</p>
    </div>

    <!-- Zobrazí test, ak je načítaný -->
    <div v-else>
      <h1>Otázky pre test: {{ test.name }}</h1>
      <ul>
        <li v-for="question in test.questions" :key="question.id">
          <!-- Zobrazenie otázky a možnosti odpovedí -->
          <div>{{ question.text }}</div>
          <div>
            <input type="radio" :name="'question-' + question.id" value="true"> Áno
            <input type="radio" :name="'question-' + question.id" value="false"> Nie
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
      test: null // Pôvodne bolo `null`, ktoré skontrolujeme
    };
  },
  created() {
    // Získanie ID testu z parametrov URL
    const testId = this.$route.params.id;

    // Načítanie konkrétneho testu podľa ID
    fetch(`http://localhost:8000/api/tests/${testId}/`)
      .then(response => response.json())
      .then(data => {
        this.test = data; // Pri načítaní sa aktualizuje objekt testu
      })
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
      });
  }
};
</script>