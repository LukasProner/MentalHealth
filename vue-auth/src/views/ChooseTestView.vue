
<template>
  <div class="test-list">
    <h1>Zoznam vašich testov</h1>

    <div class="loading" v-if="loading">
      <p>Načítavam testy...</p>
    </div>

    <div class="error" v-if="error">
      <p>{{ error }}</p>
    </div>

    <div class="test-grid" v-else>
      <router-link to="/tests" class="test-card add-test">
        <span class="plusko">+</span>
      </router-link>

      <div class="test-card" v-for="test in sortedTests(tests)" :key="test.id">
        <div class="test-header" @click="goToTest(test.id)">
          <div class="test-name">
            {{ test.name }}
            <p>Vytvorený {{ getDate(test.created_at) }}</p>
          </div>
          <button class="delete-btn" @click.stop="deleteTest(test.id)">×</button> 
          <!-- bez stop kliknutie na vnútorný element spustilo aj správanie nadradeného -->
        </div>
      </div>
    </div>
  </div>
  <FooterComp></FooterComp>
</template>

<script>
import {ref, onMounted} from 'vue';
import {useStore} from 'vuex';
import FooterComp from '@/components/FooterComp.vue';
import router from '@/router';

export default{
  components:{FooterComp},
  setup(){
    const tests=ref([]);
    const loading= ref(true);
    const error=ref(null);
    const store=useStore();

    const fetchTests=async()=>{
      try{
        const response= await fetch('http://localhost:8000/api/tests/',{
          headers:{'Content-Type': 'application/json' },
          credentials: 'include', 
        });

        if(!response.ok){
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data= await response.json();
        tests.value= data; 
      }catch (err){
        error.value ='Chyba pri načítavaní testov. Skontrolujte autentifikáciu.';
        console.error('Error:', err);
      }finally{
        loading.value = false; 
      }
    };
    const getDate =(dateString)=>{
      const date = new Date(dateString);  
      const day = date.getDate();  
      const month = date.getMonth() + 1;  
      const year = date.getFullYear();  
      return `${day < 10 ? '0' + day : day}.${month < 10 ? '0' + month : month}.${year}`;  
    }
    const deleteTest=async(testId)=>{
      try{
        const response = await fetch(`http://localhost:8000/api/tests/${testId}/`, {
          method: 'DELETE',
          // headers: { 'Content-Type': 'application/json' },
          credentials: 'include', 
        });

        if (!response.ok) {
          throw new Error(`Chyba pri odstraňovaní testu. Status: ${response.status}`);
        }

        tests.value = tests.value.filter(test => test.id !== testId);
      }catch(err){
        console.error('Error:',err);
      }
    };
    const goToTest=(testId)=>{
      router.push({name:'testDetail',params:{ id: testId }});
    };

    onMounted(async()=>{
      // await store.dispatch('checkAuth'); 
      // if (store.getters.isAuthenticated) {
        await fetchTests(); 
      // } else {
      //   error.value = 'Nie ste prihlásený. Prihláste sa na prístup k testom.'; 
      //   loading.value = false;
      // }
    });
    const sortedTests = (tests) => {
      return [...tests].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    };

    return {
      tests,
      loading,
      error,
      getDate,
      deleteTest,
      sortedTests,
      goToTest
    };
  },
};
</script>
<style scoped>
.test-list{
  text-align: center;
  min-height: 800px;
  padding: 20px;
}
.test-grid{
  display: flex;
  max-width: 800;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px;
}
.test-card{
  display: flex;
  flex-direction: column;
  border-radius: 10px;
  width: 150px;
  height: 150px;
  background-color: var(--color-lightGray);
  justify-content: center;
  align-items: center;
  box-shadow:  0 4px 4px 0 var(--color-lightblue);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}
.test-card:hover{
  transform: scale(1.05);
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
}

.add-test {
  background-color: #f5f5f5;
  border: 2px dashed #aaa;
  text-decoration: none;
}

.add-test .plusko {
  font-size: 2rem;
  color: #666;
  font-weight: bold;
  text-decoration: none;
}
.test-card .test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 100%;
  padding: 10px;
  box-sizing: border-box;
}

.test-card .test-name {
  font-size: 1rem;
  font-weight: bold;
  color: #333;
  text-decoration: none;
}
.test-name p {
  margin-bottom: auto; 
  padding: 5px;
  font-weight:100;
  font-size: 80%;
}
.delete-btn {
  position: absolute; 
  top: 10px; 
  right: 10px; 
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: gray;
  cursor: pointer;
  padding: 0;
  margin: 0;
  transition: color 0.2s;
  outline: none;
}

.delete-btn:hover {
  color: black;
}
</style>
