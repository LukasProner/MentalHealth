<template>
    <div class="header"><h1>Documentation</h1></div>
    <hr class="line">
    <div v-if="loading"> nacitavam</div>

    <ul v-else class="container">
        <li v-for = "test in tests" :key="test.id" class="test">
            <i class="bi bi-file-earmark"></i>
            <router-link :to="`/documentation/${test.id}`"> {{ test.name }}</router-link>>
        </li>
    </ul>

</template>

<script>
import { onMounted, ref } from 'vue';

export default{
    setup(){
        const tests = ref([]);
        
        const fetchTests = async() =>{
            try{
                const response = await fetch(`http://localhost:8000/api/tests/default/`,{
                    method:'GET',
                    credentials: 'include',
                });
                const data = await response.json();
                console.log("data = ",data)
                tests.value = data.tests;
                console.log("tests", tests)
            }catch(err){
                console.log(err);
            }
        }
            
        onMounted(fetchTests)

        return {
            tests,
        };
    }

}
</script>



<style scoped>
    .header h1{
        text-align: center;
        margin-bottom: 0px;
    }
    .line{
        height: 8px;
        margin: 10px 80px;
        border-radius: 10px;
    }

    .container{
        background-color:whitesmoke;
        box-shadow: 5px 5px var(--color-lightblue);
        max-width: 800px;
        margin: 20px auto;
        padding: 10px;
        border-radius: 10px;
    }

    .test{
        display: flex; 
        background-color: brown;
        margin: 10px;
        /* text-align: center; */
        align-items: center;
        padding: 10px;
        transition:0.3s;
    }

    .test a {
        margin-left: auto; /* Posunie link na pravú stranu */
    }



    .test:hover{
        background-color:rgb(28, 180, 235);
        transform: scale(1.02);
    }
</style>