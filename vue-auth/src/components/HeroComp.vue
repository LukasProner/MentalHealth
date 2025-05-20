<template>
    <div class="hero"> 
        <h2>Inšpirujte sa</h2>
        <h2>existujúcimi testami</h2>
        <h2>Vytvorte testy so</h2>
        <h2>širokou variabilitou možností</h2>
        <ButtonComp text="Začať tvorbu testov" type="submit" fontSize="1.5rem" @click = "makeTest" />
    </div>
</template>

<script>
import ButtonComp from './ButtonComp.vue'; 
import { useRouter } from 'vue-router';
export default {
    name: "HeroComp", 
    components: {
        ButtonComp 
    },
    setup(){
        const router = useRouter();
        const makeTest = () => {
            router.push(`/tests`);
        }
    
        return{
            makeTest,
        }
    }
};
</script>
<style>
.hero {
    background-image: url('../assets/Rectangle 1.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    height: 600px;
    padding: 80px 100px;
    text-align: left;
}

.hero h2 {
    padding: 0;
    margin: 0;
    margin-bottom: 10px;
    font-size: 3rem;
    font-weight: bold;
    text-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
}

@media (max-width: 768px) {
    .hero {
        padding: 60px 40px;
        height: auto; 
        background-size: 1000px
    }

    .hero h2 {
        font-size: 2rem;  
    }
}
</style>