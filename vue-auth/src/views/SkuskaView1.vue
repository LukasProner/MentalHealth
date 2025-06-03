<template>
    <input type="text" v-model="testName">
    <button @click="createTest">Pridat Test</button>


    <ul class="celok">
        <li v-for="(test,index) in tests" :key="index" class="zoznam">
            {{ test }}
        </li>
    </ul>
</template>

<script>
import { ref } from 'vue';


export default{
    
    setup(){
        const tests = ref(['aaaaa aaa','bbbbbbbbbbbb','ccccccccccccc','dddddddddddd dddddddddddd','eeeeee  eeeeeeeee eeeeeeeee','ffffffffff ffffffffff']);
        const testName = ref('');

        const createTest=()=>{
            if(testName.value.trim===''){
                alert("Nazov nesmie byt prazdny");
            }else{
                tests.value.push(testName.value);
                testName.value='';
            }
        }

        return{
            tests,
            testName,
            createTest
        }

    }
}
</script>

<style scoped>

    .celok{
        display: flex;
        margin: 0 50px;
        flex-wrap: wrap;
        gap: 20px;
        list-style: none;
    }

    .zoznam{
        margin: 20px auto;
        background-color: aqua;
        width: 150px;
        height: 150px;
        text-align: center;
        text-decoration: none;
    }
</style>