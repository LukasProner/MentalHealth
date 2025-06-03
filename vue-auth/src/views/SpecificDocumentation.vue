<template>
    <h1 class="title">{{ docTitle}}</h1> 
    <div v-html="docContent" class="contentClass"></div>
</template>

<script>
import ButtonComp from '@/components/ButtonComp.vue';
import { onMounted, ref } from 'vue';
import { useRoute,useRouter } from 'vue-router';


export default{
    
    setup(){
        const docTitle = ref('');
        const docContent = ref('');
        const route = useRoute();

        const fetchDocs = async()=>{
            try{
                const response = await fetch(`http://localhost:8000/api/documentation/${route.params.id}/`,{
                    method:"GET",
                    credentials:"include",
                })
                if(!response.ok){
                    throw new Error(`responses error: ${response.status}`);
                }
                const data = await response.json();
                docTitle.value = data.title;
                docContent.value = data.content;
            }catch(err){
                console.error('Error:', err);
            }
        }
        onMounted(fetchDocs);
        return{
            docTitle,
            docContent
        }
    }
}
</script>

<style scoped>
    .title{
        text-align: center;
        box-shadow: 5px 5px 5px var(--color-lightblue,0.8);
        margin: 50px;
        background-color: var(--color-lightblue);
        border-radius: 20px;
        padding: 10px;
    }
    .contentClass{
        text-align: left;
        margin: 0 40px 50px 40px;
        background-color: antiquewhite;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0px -10px var(--color-lightblue);
    }
    
</style>