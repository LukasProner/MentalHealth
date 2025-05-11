<template>
  <HeroComp />
  <ContentComp></ContentComp>
  <FooterComp></FooterComp>
</template>

<script lang="ts">
import { onMounted, ref } from 'vue';
import { useStore } from "vuex";
import HeroComp from "@/components/HeroComp.vue";
import ContentComp from '@/components/ContentComp.vue';
import FooterComp from '@/components/FooterComp.vue';

export default {
  name: "HomeView",
  components: {
    HeroComp, 
    ContentComp,
    FooterComp
  },
  setup() {
    // const message = ref('You are not logged in!');
    // const loading = ref(true); 
    const store = useStore();

    onMounted(async () => {
      // loading.value = true;
      try {
        await store.dispatch('checkAuth');
      } catch (err) {
        // error.value = 'Chyba pri overovaní prihlásenia.';
      } finally {
        // loading.value = false;
      }
    });


    // onMounted(async () => { //OPRAVIT CI POTREBNE
    //   try {
    //     const response = await fetch('http://localhost:8000/api/user/', {
    //       headers: {'Content-Type': 'application/json'},
    //       credentials: 'include',
    //     });

    //     if (response.ok) {
    //       const content = await response.json();
    //       if (content && content.name) {
    //         message.value = `Hi ${content.name}`;
    //         await store.dispatch('setAuth', true);
    //       } else {
    //         message.value = 'You are not logged in!';
    //         await store.dispatch('setAuth', false);
    //       }
    //     } else {
    //       message.value = 'You are not logged in!';
    //       await store.dispatch('setAuth', false);
    //     }
    //   } catch (e) {
    //     message.value = 'You are not logged in!';
    //     await store.dispatch('setAuth', false);
    //   } finally {
    //     loading.value = false; // Načítanie dokončené
    //   }
    // });

    return {
      // message,
      // loading
    }
  }
}
</script>
