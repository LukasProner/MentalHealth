<template>
  <div class="registration-container">
    <form @submit.prevent="submit">
      <h1 class="h3 mb-3 fw-normal">Please register</h1>
  
      <input v-model="data.name" class="form-control" placeholder="Name" required>
  
      <input v-model="data.email" type="email" class="form-control" placeholder="Email" required>
  
      <input v-model="data.password" type="password" class="form-control" placeholder="Password" required>
  
      <ButtonComp text="Register" type="submit" fontSize="1rem" />

    </form>
  </div>
</template>
  
<script lang="ts">
  import {reactive} from 'vue';
  import {useRouter} from "vue-router";
  import ButtonComp from '@/components/ButtonComp.vue';
  
  export default {
    components: {
      ButtonComp
    },
    name: "RegisterView",
    setup() {
      const data = reactive({
        name: '',
        email: '',
        password: ''
      });
      const router = useRouter();
  
      const submit = async () => {
        const response = await fetch('http://localhost:8000/api/register/', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(data)
        });
        if(response.ok){
          await router.push('/login');
        }else{
          const errorData = await response.json();
          alert("Registrácia zlyhala: " + JSON.stringify(errorData));
        }
      }
  
      return {
        data,
        submit
      }
    }
  }
</script>

<style scoped>
  .registration-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 90vh;
    background-color: var(--color-background);
  }
  form{
    background-color: var(--color-white);
    padding: 30px;
    border-radius: 16px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-bottom: 100px;
  }
  form input {
    width: 100%;
    padding: 10px 15px;
    font-size: 16px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    outline: none;
    transition: border-color 0.3s ease;
  }
  form input:focus {
    border-color: var(--color-lightblue);
    box-shadow:  0 4px 4px 0 var(--color-lightblue);
  }

  form h1{
    text-align: center;
    margin: 0px;
    padding: 0px;
  }
  form h1.mb-3 {
    margin-bottom: 0px !important;
  }
</style>