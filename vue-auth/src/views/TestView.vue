
<template>
  <div class="all">
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
      
        <ul class="questions-container">
          <li v-for="(question, index) in questions" :key="question.id">
            <div v-if="!isEditingQuestion(question)" class="question-card" @click="enableEditingQuestion(question)">
              <p class="question-text">{{ question.text }}</p>
              <div v-if="question.image_url!==null" >
                <img :src="question.image_url" alt="Question Image" class="question-image" />
              </div>
              <ul v-if="question.options && question.options.length > 0" class="options-list">
                <li v-for="(option, index) in question.options" :key="index" class="option-item">
                  <p class="option-text">{{ option.text }}</p>
                  <p v-if="option.hasValue" class="option-value">Hodnota: {{ option.value }}</p>
                </li>
              </ul>

              <div v-if="question.showCategoryInput" class="category-section" @click.stop>
                <p class="category-label">Aktuálna kategória: {{ question.category }}</p>
                <input v-model="question.newCategory" placeholder="Zadajte novú kategóriu" 
                      @blur="saveCategory(index)" class="category-input"/>
              </div>

              <div class="buttons">
                <ButtonComp text="Pridať kategóriu" @click.stop="toggleCategoryInput(index)" fontSize="1rem"/>
                <ButtonComp text="Upraviť otázku" @click.stop="enableEditingQuestion(question)" fontSize="1rem"/>
                <!-- <ButtonComp text="Odstrániť" @click.stop="deleteQuestion(question.id, index)" fontSize="1rem"/> -->
                <ButtonComp @click.stop="deleteQuestion(question.id, index)" fontSize="1rem">
                  <i class="bi bi-trash3"></i> 
                </ButtonComp>
                <!-- <ButtonComp text="Kopírovať otázku" @click.stop="copyQuestion(question, index)" fontSize="1rem"/> -->
                <ButtonComp @click.stop="copyQuestion(question, index)" fontSize="1rem">
                  <i class="bi bi-copy"></i>
                </ButtonComp>
              </div>
            </div>

            <div v-else class="question-form">
              <input v-model="question.text" placeholder="Zadajte novú otázku" class="input-field question-input"/>

              <select v-model="question.type" class="input-field select-field">
                <option value="boolean">Áno/Nie</option>
                <option value="choice">Viac možností</option>
                <option value="text">Textová odpoveď</option>
                <option value="drawing">Kreslenie</option>
              </select>

              <div v-if="question.type==='choice'" class="options-section">
                <div v-for="(option, optIndex) in question.options" :key="optIndex" class="choice-item">
                  <input v-model="option.text" placeholder="Upravte možnosť" class="input-field option-input"/>
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="option.hasValue" />
                    Pridať hodnotenie
                  </label>
                  <input v-if="option.hasValue" type="number" v-model.number="option.value" placeholder="Hodnota"  class="value-input"/>
                  <button @click="removeOptionUpdate(question, optIndex)" class="button remove-button">×</button>
                </div>
                <ButtonComp text="Pridať možnosť" @click="addOptionUpdate(question)" fontSize="1rem">
                  <i class="bi bi-plus-circle-dotted"></i>
                </ButtonComp>
              </div>
              <ButtonComp text="Uložiť" @click="disableEditingQuestion(question)" fontSize="1rem"/>
            </div>
          </li>
        </ul>
      <!-- </div> -->
      

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
          <div v-for="(option, index) in options" :key="index" class="option-item">
            <input v-model="option.text" placeholder="Zadaj možnosť" class="input-field option-input"/>
            <label class="checkbox-label">
              <input type="checkbox" v-model="option.hasValue" class="checkbox-input" />
              Pridať hodnotenie
            </label>
            <input
              v-if="option.hasValue" type="number" v-model.number="option.value" placeholder="Hodnota" class="input-field value-input"
            />
            <button @click="removeOption(index)" class="button remove-button">
              ×
            </button>
          </div>
          <ButtonComp text="Pridať novú možnosť" @click="addOption" fontSize="1rem"/>
        </div>
        <div v-if="imageUrl!==''">
          <img :src="imageUrl" alt="Question Image" class="question-image" />
        </div>

        <div class="buttons-container">
          <label for="file-upload" class="custom-file-upload">
            <i class="bi bi-image"></i> Nahrať obrázok
          </label>
          <input id="file-upload" type="file" @change="handleImageUpload" />

          <ButtonComp text="Uložiť" @click="addQuestion" fontSize="1rem"/>
        </div>
      </div>
      <div v-if="testId && !loading && !error">
        <div class="button-group">
          <SendDataComp :testId="testId" :testCode="testCode" class="export"/>
          <ButtonComp :text="showScaling ? 'Zavrieť' : 'Vytvoriť škálovanie'" @click="toggleScaling" fontSize="1rem"/>
          <ButtonComp :text="isTestOpen ? 'Zavrieť' : 'Pridať test'" @click="chooseDefaultTest" fontSize="1rem"/>
          <Import :testId="testId" @import-complete="handleImportComplete" />
        </div>
        
        <div v-if="isTestOpen" class="test-selection">
          <h3>Vyberte test</h3>
          <ul class="test-list">
            <li v-for="test in defaultTests" :key="test.id" @click="selectTest(test)" class="test-item">
            <i class="bi bi-file-earmark-arrow-down"></i>
              {{ test.name }}
            </li>
          </ul>
        </div>
        <div v-if="showScaling" class="scaling-container">
          <h3 class="ScaleH3">Škalovanie výsledkov</h3>
          
          <div v-for="(scale, index) in scales" :key="index" class="scale-item">
              <input type="number" v-model.number="scale.min" placeholder="Minimálne body" class="min" />
              <input type="number" v-model.number="scale.max" placeholder="Maximálne body" class="max"/>
              <input v-model="scale.response" placeholder="Odpoveď (napr. Výborný výkon)" />
              <input v-model="scale.category" placeholder="Vyber kategoriu" />
              <button @click="removeScale(index)" class="button remove-button">×</button>
          </div>
          <div style="display: flex;gap: 10px; text-align: center; justify-content: center;">
            <ButtonComp text="Pridať nové škálovanie" @click="addScale" fontSize="1rem"/>
            <ButtonComp text="Uložiť škálovanie" @click="actualizeScales" fontSize="1rem"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import { useStore } from 'vuex';
import Import from '../components/Import.vue';
import ButtonComp from '../components/ButtonComp.vue';
import SendDataComp from '../components/SendDataComp.vue';

export default {
  components: {
    Import,
    ButtonComp,
    SendDataComp
  },
  name: 'SkuskaOpica',
  setup() {
    const store=useStore();
    const testName = ref('');
    const editedName = ref('');
    const isEditing = ref(false);
    const testId = ref(null);
    const questionText = ref('');
    const questionType = ref('choice');
    const options = ref([]);
    const newOption = ref('');
    const loading=ref(false);
    const error = ref(null);
    const questions=ref([]); 
    const scales = ref([]);
    const testCode = ref([]);
    const questionCategory= ref('');
    const defaultTests=ref([]);
    const isTestOpen = ref(false);
    const editingQuestion=ref(null);
    const showScaling = ref(false);
    const selectedImage = ref(null);
    const imageUrl = ref("");
    const added=ref(false);
 
    const handleImageUpload=async(event)=>{
      const file=event.target.files[0];
      const formData=new FormData();
      formData.append("image", file);
      try{
        const response = await fetch("http://localhost:8000/api/upload-image/",{
          method: "POST",
          body: formData,
          credentials: "include",
        });
        if(!response.ok){
          throw new Error(`Chyba pri nahrávaní obrázka: ${response.status}`);
        }
        const data=await response.json();
        console.log('Server response:', data);
        console.log('URL obrázka:', data.image_url);
        imageUrl.value = data.image_url; 
      }catch(error){
        console.error('Chyba pri nahrávaní obrázka:', error);
      }
    };

 
    const addQuestion =async()=>{
      if(questionType.value!=="choice"){
        options.value=[];
      }
      const newQuestion={
        text: questionText.value,
        question_type:questionType.value,
        options: options.value,
        category: questionCategory.value || 'Nezaradená',
        image_url: imageUrl.value|| null, 
      };

      try{
        const response=await fetch(`http://localhost:8000/api/tests/${testId.value}/questions/`,{
          method: 'POST',
          headers:{
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newQuestion),
          credentials:'include',
        });

        if(!response.ok){
          throw new Error(`chyba pri ukladani: ${response.status}`);
        }

        const data = await response.json();
        // console.log('Response data:', data);

        questions.value.push(data);
        questionText.value ='';
        questionType.value ='choice';
        options.value =[];
        questionCategory.value= '';
        imageUrl.value='';  
        addOption();

      }catch(error){
        console.error('chyba pri ukladani:', error);
      }
    };


    const checkAuth=async()=>{
      loading.value=true;
      try{
        await store.dispatch('checkAuth');
      }catch(err){
        error.value='Chyba pri overovaní prihlásenia.';
      }finally{
        loading.value= false;
      }
    };

    const createTest=async()=>{
      if(!store.getters.isAuthenticated){
        error.value = 'Nie ste prihlásený. Prihláste sa, aby ste mohli vytvoriť test.';
        return;
      }

      const newTest={name: testName.value};

      try{
        const createResponse=await fetch('http://localhost:8000/api/tests/',{
          method:'POST',
          headers:{
            'Content-Type': 'application/json',
          },
          body:JSON.stringify(newTest),
          credentials:'include',
        });

        if(!createResponse.ok){
          throw new Error(`chyba pri vytvoreni testu: ${createResponse.status}`);
        }

        const data=await createResponse.json();

        testId.value=data.id;
        testName.value=newTest.name;
        editedName.value=newTest.name;

        const detailsResponse= await fetch(`http://localhost:8000/api/tests/${data.id}/`,{
          method:'GET',
          // headers: {
          //   'Content-Type': 'application/json',
          // },
          credentials: 'include',
        });

        if(!detailsResponse.ok){
          throw new Error(`Chyba - detail testu: ${detailsResponse.status}`);
        }

        const testDetails=await detailsResponse.json();
        // console.log('Test details:', testDetails);

        testCode.value=testDetails.test_code;  
        // console.log('Test code', testCode);

        addOption();  

      }catch(err){
        console.error('Chyba pri vytváraní testu:', err);
      }
    };

 
    const enableEditing=()=>{
      isEditing.value=true;
      editedName.value = testName.value;
    };
    const enableEditingQuestion=(question)=>{
      editingQuestion.value = question;  
    };
    const isEditingQuestion=(question)=>{
      return editingQuestion.value===question;
    };
    const disableEditingQuestion =async(question)=>{
      // console.log('disableEditingQuestion',question)
      // console.log('disableType',question.type)
      if(question.type!=="choice"){
        question.options=[];
      }
      try{
        const updatedData={
          text: question.text,
          question_type: question.type,
          options: question.options,
          category: question.category,
        };

        const updatedQuestion=await updateQuestion(question.id, updatedData);

        editingQuestion.value = null;  
        // console.log('Otázka bola aktualizovaná:', updatedQuestion);
      }catch(error){
        // console.error('Chyba pri aktualizácii otázky:', error);
      }
      editingQuestion.value=null; 
    };

    const saveTestName=async()=>{
      if(editedName.value.trim()===testName.value){
        isEditing.value=false;
        return;
      }

      try{
        const response=await fetch(`http://localhost:8000/api/tests/${testId.value}/`,{
          method: 'PUT',
          headers:{
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ name: editedName.value }),
          credentials: 'include',
        });

        if (!response.ok){
          throw new Error('Nepodarilo sa uložiť názov testu.');
        }

        testName.value = editedName.value;
      }catch (err){
        error.value =err.message;
      }finally{
        isEditing.value=false;
      }
    };

  const addOption=()=>{
    options.value.push({text: '', hasValue:false, value:null });  
  };
  const addOptionUpdate=(question)=>{
    question.options.push({ text:"", hasValue:false, value:null });
  };

  const removeOption=(index)=>{
    options.value.splice(index, 1);
  };
  const removeOptionUpdate=(question,optIndex)=>{
    question.options.splice(optIndex, 1);
  };

  const chooseDefaultTest=()=>{
    isTestOpen.value = !isTestOpen.value
    return null
  }

  const fetchDefaultTests=async()=>{
    try{
      const response = await fetch(`http://localhost:8000/api/tests/default/`, {
        method: 'GET',
        // headers: { 'Content-Type': 'application/json' },
        credentials: 'include', 
      });
      // console.log('response',response)

      if (!response.ok) {
        throw new Error(`chyba: ${response.status}`);
      }

      const data = await response.json();
      // console.log('data',data)
      defaultTests.value = data.tests;
    }catch(err){
      error.value = 'Chyba pri načítavaní testov. Skontrolujte autentifikáciu.';
      // console.error('Error:', err);
    }finally{
      loading.value = false;
    }
  };

 
  const selectTest=async(test)=>{
    try{
      const response = await fetch(`http://localhost:8000/api/tests/${test.id}/`,{
        method: 'GET',
        // headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });

      if(!response.ok){
        throw new Error(`chyba ${response.status}`);
      }

      const data=await response.json();
      // console.log('Questions from selected test:', data);

      for(const question of data.questions){
        const newQuestion = {
          text: question.text,
          question_type: question.question_type,
          options: question.options||[],
          category: question.category||'Nezaradená',
        };

        const saveResponse=await fetch(`http://localhost:8000/api/tests/${testId.value}/questions/`,{
          method:'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newQuestion),
          credentials: 'include',
        });

        if(!saveResponse.ok){
          throw new Error(`Chyba pri ukladaní otázky: ${saveResponse.status}`);
        }

        const savedQuestion=await saveResponse.json();
        questions.value.push(savedQuestion);
      }

      // Získanie škál
      const scaleResponse= await fetch(`http://localhost:8000/api/tests/${test.id}/scales/`,{
        method: 'GET',
        // headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });

      if(!scaleResponse.ok){
        throw new Error(`HTTP chyba! Status: ${scaleResponse.status}`);
      }

      const tempScales= await scaleResponse.json();
      // console.log('Scales from selected test:', tempScales);

      for (const scale of tempScales){
        scales.value.push({
          min: scale.min_points,
          max: scale.max_points,
          response: scale.response,
          category: scale.category
        });
      }

      const saveScalesResponse = await fetch(`http://localhost:8000/api/tests/${testId.value}/scales/`,{
        method:'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(tempScales),
        credentials: 'include',
      });

      if(!saveScalesResponse.ok){
        throw new Error(`Chyba pri ukladaní škál: ${saveScalesResponse.status}`);
      }

      const savedScales = await saveScalesResponse.json();
      // console.log('Uložené škály:', savedScales);

      isTestOpen.value= false;
    }catch(err){
      error.value = 'Chyba pri načítavaní otázok z vybraného testu.';
      // console.error('Error:', err);
    }
  };


  const copyQuestion=async(question,index)=>{
    // console.log('Kopírujem otázku:', question);

    const newQuestion={
      text: question.text,
      question_type: question.type,
      options: question.options,
      category: question.category,
    };

    try{
      const response=await fetch(`http://localhost:8000/api/tests/${testId.value}/questions/`,{
        method: 'POST',
        headers:{
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newQuestion),
        credentials: 'include',
      });

      if(!response.ok){
        throw new Error(`chyba pri kopírovaní: ${response.status}`);
      }

      const data = await response.json();
      questions.value.push(data);
    } catch (err) {
      console.error('chyba pri kopirovani', err);
    }
  };

  const deleteQuestion=async(questionId,index)=>{
    try{
      const response = await fetch(`http://localhost:8000/api/questions/${questionId}/`,{
        method:'DELETE',
        credentials:'include',
      });

      if(!response.ok){
        throw new Error('Nepodarilo sa odstrániť otázku.');
      }

      // console.log("otazka bola odstranena");
      questions.value.splice(index, 1);

    }catch(err){
      error.value = err.message;
      console.error('chyba pri odstraneni otazky', err);
    }
  };


  const updateQuestion=async(questionId, updatedData)=>{
    // console.log('aktualizujem otázku-', questionId, updatedData);
    try{
      const response = await fetch(`http://localhost:8000/api/questions/${questionId}/`,{
        method: 'PUT', 
        headers: {
          'Content-Type': 'application/json',  
        },
        credentials: 'include',  
        body: JSON.stringify(updatedData),  
      });

      if(!response.ok){
        throw new Error(`Chyba pri aktualizácii:${response.statusText}`);
      }

      const responseData = await response.json(); 
      return responseData;
    }catch(error){
      console.error('chyba pri aktualizácii:',error);
      throw error;  
    }
  };

    const addScale=()=>{
      scales.value.push({min:0,max:0,response:'' });
    };

    const removeScale=(index)=>{
      scales.value.splice(index, 1);
    };

    const saveScales=async()=>{
      const formattedScales = scales.value.map((scale)=>({
        min_points: scale.min,
        max_points: scale.max,
        response: scale.response,
        category: scale.category,
      }));

      try{
        const response=await fetch(`http://localhost:8000/api/tests/${testId.value}/scales/`,{
          method:'POST',
          headers:{
            'Content-Type': 'application/json',
          },
          body:JSON.stringify(formattedScales),
          credentials: 'include',
        });

        if(!response.ok){
          const err = await response.json();
          console.error(' savescales chyba:', err);
          throw new Error(err.detail || JSON.stringify(err) || 'Neznáma chyba');
        }

        const data=await response.json();
        console.log('Scales uložené:', data);
        // alert('Škálovanie bolo úspešne uložené!');
      } catch (err) {
        // console.error('chyba pri ukladani',err.message);
        // alert(`Chyba: ${err.message || 'Neznáma chyba pri ukladaní škál'}`);
      }
    };

  const actualizeScales=async()=>{
    try{
        const response=await fetch(`http://localhost:8000/api/tests/${testId.value}/scales/`,{
            method:'DELETE',
        });

        if(!response.ok){
            const error = await response.json();
            // console.error('chyba- delete 3kaly:', error);
            throw new Error(error.detail);
        }
        await saveScales(); 
    }catch(error){
        // console.error('Chyba pri aktualizácii škál:', error.message);
    }
  };

  const toggleCategoryInput=(index)=>{
    const question=questions.value[index];
    question.showCategoryInput = !question.showCategoryInput;
  };

  const saveCategory=async(index)=>{
    const question=questions.value[index];
    
    if(question.newCategory){
      question.category = question.newCategory;
      console.log(question.category);
      question.newCategory= ''; 
    }

    question.showCategoryInput=false;  

    try{
      const updatedQuestion={
        category: question.category, 
        text: question.text,  
        question_type: question.question_type, 
      };

      const response=await updateQuestion(question.id, updatedQuestion);
      // console.log('kategória bola aktualizovana', response);
    }catch(error){
      console.error('Chyba pri aktualizacii:', error);
    }
  };

  const handleImportComplete=async(data,scalesData)=>{
      // console.log("Import bol uspesny");
      for(const question of data){
          try{
              questions.value.push(question);
          }catch(error){
              // console.error("chyba pri pridavani otazky:", error);
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
          }catch(error){
              // console.error("Chyba pri pridavani scale", error);
          }
      }
      actualizeScales();
  };
  const toggleScaling=()=>{
    if(added.value===false){
      addScale();
      added.value=true
    }
    showScaling.value=!showScaling.value;
    console.log(showScaling.value)
    actualizeScales();
  };
   
  onMounted(()=>{
    checkAuth();
    fetchDefaultTests();
  });

  onUnmounted(()=>{
    // document.removeEventListener('click', handleClickOutside);
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
      questions,  
      createTest,
      enableEditing,
      saveTestName,
      addOption,
      removeOption,
      addQuestion,
      deleteQuestion,  
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
      removeOptionUpdate,
      toggleScaling,
      showScaling,
      copyQuestion,
      handleImageUpload,
      selectedImage,
      imageUrl,
    };
  },
};
</script>

<style scoped>

.all{
  background-color: var(--color-background);
  min-height: 100vh;
  padding-top: 20px;
}
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
  box-shadow: 0 4px 6px var(--color-lightblue);
  max-width: 500px;
  margin: 20px auto;
  margin-top:20px;
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
  box-shadow: 0 4px 6px var(--color-lightblue);
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
  background-color: var(--color-lightblue);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
  position: relative;
  transition: all 0.3s ease-in-out;
  border-radius: 10px;
  padding: 5px 0px 5px 0px;
}

.test-name span {
  cursor: pointer;
  color: white;
  text-shadow: 2px 2px 4px gray, -2px -2px 4px gray, 2px -2px 4px gray, -2px 2px 4px gray;
}

.test-name input {
  width: 98%;
  border: 2px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
  transition: border-color 0.2s ease;
}

.test-name input:focus {
  border-color: var(--color-primary);
  outline: none;
}
.questions-container {
  width: 100%;
  max-width: 800px;
  margin: auto;
  padding: 0px;
  list-style: none;
}
.question-image {
  width: 90%;  
  height: auto;  
  display: block; 
  margin: 10px auto;
}

.question-card {
  background: rgba(255, 255, 255, 0.2);
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 4px 8px var(--color-lightblue);
  margin-bottom: 15px;
}
.question-text {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.options-list {
  padding-left: 20px;
  text-align: left;
  list-style: none;
}

.option-value {
  font-size: 0.9rem;
  color: #666;
}

.category-section {
  margin-top: 10px;
}

.category-label {
  font-weight: bold;
}

.category-input {
  width: 100%;
  padding: 5px;
  margin-top: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.edit {
  background-color: #ffc107;
  color: black;
}


.choice-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.question-form {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px var(--color-lightblue);
  max-width: 800px;
  margin: auto;
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-field {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1rem;
}

.question-input:focus {
  box-shadow: 0 4px 6px var(--color-lightblue);
  outline: none;
}

.select-field {
  background-color: white;
  cursor: pointer;
}

.options-section {
  background: #ffffff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.option-input {
  flex: 1;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
}

.value-input {
  width: 80px;
  text-align: center;
}

.buttons-container {
  display: flex;
  justify-content: space-evenly;
  margin-top: 15px;
}

.button {
  padding: 6px 10px;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
}

.custom-file-upload {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;  
  cursor: pointer;
  color: var(--color-h1);
  background-color: var(--color-lightblue);
  font-size: 16px;
  font-weight: bold;
  text-align: center;
  transition: 0.3s;
  padding: 0px 10px;
  border-radius: 5px;
  transition: background-color 0.3s, box-shadow 0.3s, transform 0.2s;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
  outline: none;
}

.custom-file-upload:hover {
  background-color: var(--color-button-hover);
  color: var(--color-white);
}

#file-upload {
  display: none;  
}
 

.remove-button {
  background-color: #dc3545;
  color: white;
}

.buttons{
  display: flex;
  justify-content: space-evenly;
  margin:10px 20px 0px 20px
}

.button-group {
  display: flex;
  flex-wrap: wrap; /* Povolenie zalomenia */
  gap: 10px;  
  align-items: center;
  justify-content: center;
  max-width: 800px;
}
@media (max-width: 600px) {
  .button-group {
    justify-content: space-between;
  }

  .button-group > * {
    flex: 1 1 calc(50% - 10px); /* Každé tlačidlo bude mať 50% šírky mínus gap */
    text-align: center;
  }
}

.scaling-container {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    max-width: 800px;
    margin: 20px auto;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

h3 {
    text-align: center;
    color: black;
    font-size: 1.4rem;
}

.scale-item {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #f9f9f9;
    padding: 10px;
    border-radius: 8px;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}

.scale-item input {
    flex: 1;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 1rem;
}
.scale-item .min,.max{
  width: 60px;
}
.test-selection {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  margin: 0 auto;
}

.test-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.test-item {
  text-align: left;
  background-color: #fff;
  padding: 10px 15px;
  margin: 5px 0;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.3s ease;
}

.test-item:hover {
  background-color: var(--color-lightblue);
  transform: translateY(-2px);
}

.test-item:active {
  background-color: #b2ebf2;
}

.test-item.selected {
  background-color: #80deea;
  font-weight: bold;
}
.test-item i{
  margin-right: 10px;
  font-size: 1.5rem;
  color:var(--color-lightblue)
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

.tooltip-container {
    position: relative;
    display: inline-block;
    display: flex;
    text-align: center;
    justify-content: center;
}

.tooltip-container .tooltip-text {
    position: absolute;
    top: 100%;  
    left: 50%;
    transform: translateX(-50%);
    background-color: white;
    color: var(--color-button-hover);
    font-weight: bold;
    padding: 6px 10px;
    border-radius: 5px;
    white-space: nowrap;
    font-size: 0.8rem;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease-in-out, visibility 0s linear 0.3s;
    border: 3px solid var(--color-lightblue);
}

.tooltip-container:hover .tooltip-text {
    opacity: 1;
    visibility: visible;
    transition-delay: 2s;  
}

.tooltip-container:not(:hover) .tooltip-text {
    transition-delay: 0s;  
}

</style>





