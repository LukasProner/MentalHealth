
  <template>
    {{ message }}
  </template>
  
  <script lang="ts">
  import { onMounted, ref } from 'vue';
  import { useStore } from "vuex";
  
  export default {
    name: "HomeView",
    setup() {
      const message = ref('You are not logged in!');
      const store = useStore();
  
      onMounted(async () => {
        try {
          const response = await fetch('http://localhost:8000/api/user/', {
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
          });
  
          if (response.ok) {
            const content = await response.json();
            // Skontroluj, či obsah obsahuje meno (alebo inú vlastnosť, ktorú očakávaš)
            if (content && content.name) {
              message.value = `Hi ${content.name}`;
              await store.dispatch('setAuth', true);
            } else {
              message.value = 'You are not logged in!';
              await store.dispatch('setAuth', false);
            }
          } else {
            message.value = 'You are not logged in!';
            await store.dispatch('setAuth', false);
          }
        } catch (e) {
          message.value = 'You are not logged in!';
          await store.dispatch('setAuth', false);
        }
      });
  
      return {
        message
      }
    }
  }
  </script>