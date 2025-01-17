<template>
    <div>
      <div v-if="auth">Hi, you are logged in!</div>
      <canvas ref="canvas" width="500" height="500" style="border:1px solid #000000;"></canvas>
      <button @click="saveDrawing">Odoslať obrázok</button>
    </div>
  </template>
  
  <script>
  import { onMounted } from 'vue';
  import { useStore } from "vuex";
  export default {
    setup() {
      const store = useStore();

      const checkAuth = async () => {
        try {
          const response = await fetch('http://localhost:8000/api/user/', {
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
          });

          if (response.ok) {
            const content = await response.json();
            if (content && content.name) {
              store.dispatch('setAuth', true);
            } else {
              store.commit('setAuth', false);
            }
          } else {
            store.commit('setAuth', false);
          }
        } catch (e) {
          store.commit('setAuth', false);
        }
      };

      // Overenie autentifikácie pri montovaní komponentu
      onMounted(() => {
        checkAuth();
      });
      },
    methods: {
      saveDrawing() {
        const canvas = this.$refs.canvas;
        const dataURL = canvas.toDataURL(); // Convert canvas to Base64 image
        console.log(dataURL); // Skontroluj, či sa zobrazuje kompletný reťazec
        this.uploadImage(dataURL);
      },
      uploadImage(dataURL) {
        // Send the image to the backend
        fetch('http://localhost:8000/api/upload-image/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ image: dataURL })
        })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          console.log('Image saved:', data);
        }).catch(error => {
          console.error('Error:', error);
        });
      }
    },
    mounted() {
      const canvas = this.$refs.canvas;
      const ctx = canvas.getContext('2d');
  
      // Add event listeners to enable drawing
      canvas.addEventListener('mousedown', (e) => {
        ctx.beginPath();
        ctx.moveTo(e.offsetX, e.offsetY);
        canvas.addEventListener('mousemove', draw);
      });
  
      canvas.addEventListener('mouseup', () => {
        canvas.removeEventListener('mousemove', draw);
      });
  
      function draw(e) {
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
      }
    }
  }
  </script>