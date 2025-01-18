<template>
    <div>
      <h1>Kresliaci skicár</h1>
      
      <!-- Kresliace plátno -->
      <canvas 
        ref="canvas"
        :width="canvasWidth"
        :height="canvasHeight"
        @mousedown="startDrawing"
        @mousemove="draw"
        @mouseup="stopDrawing"
        @mouseleave="stopDrawing"
      ></canvas>
  
      <!-- Tlačidlá pre ovládanie -->
      <div class="controls">
        <button @click="clearCanvas">Vymazať plátno</button>
        <button @click="downloadImage">Stiahnuť obrázok</button>
        <button @click="saveDrawing">Uložiť a pokračovať</button>
        <button @click="startRecording">Začať nahrávanie</button>
        <button @click="stopRecording">Zastaviť nahrávanie</button>
      </div>
  
      <!-- Prehrávanie video záznamu -->
      <div v-if="videoUrl">
        <h2>Prehrávanie záznamu</h2>
        <video :src="videoUrl" controls autoplay></video>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { useRoute } from 'vue-router';
  
  export default {
    setup() {
        const route = useRoute(); // Prístup k aktuálnej trase
        const questionId = Number(route.query.question_id); // Získaj parameter z query

        console.log("Query ID:", questionId);

        return { questionId }; // Ak ho chceš použiť v šablóne
    },
  
    data() {
      return {
        canvasWidth: 500,
        canvasHeight: 500,
        drawing: false,
        lineColor: '#000000',
        lineWidth: 5,
        ctx: null,
        recorder: null,
        stream: null,
        videoUrl: null,
        mediaChunks: [],
      };
    },
    methods: {
  startRecording() {
    // Zachytenie obrazovky
    navigator.mediaDevices.getDisplayMedia({ video: true })
      .then(stream => {
        this.mediaRecorder = new MediaRecorder(stream);
        this.chunks = []; // Uloženie fragmentov videa

        this.mediaRecorder.ondataavailable = event => {
          if (event.data.size > 0) {
            this.chunks.push(event.data); // Ukladanie dát
          }
        };

        this.mediaRecorder.onstop = this.saveRecording;

        this.mediaRecorder.start(); // Začiatok nahrávania
      })
      .catch(err => {
        console.error("Error accessing display media:", err);
      });
    },
    stopRecording() {
        if (this.mediaRecorder) {
        this.mediaRecorder.stop(); // Zastavenie nahrávania
        }
    },
    saveRecording() {
        const blob = new Blob(this.chunks, { type: 'video/webm' });
        const formData = new FormData();
        formData.append('video', blob);
         formData.append('question_id', this.questionId);
        // Odoslanie videa na backend
        fetch('http://localhost:8000/api/save_video/', {
            method: 'POST',
            body: formData,
        })
      .then(response => response.json())
      .then(data => {
        console.log('Video uložené:', data);
      })
      .catch(error => {
        console.error('Chyba pri ukladaní videa:', error);
      });
    },
  
      // Začiatok kreslenia
      startDrawing(event) {
        this.drawing = true;
        this.ctx = this.$refs.canvas.getContext('2d');
        this.ctx.beginPath();
        this.ctx.moveTo(event.offsetX, event.offsetY);
      },
  
      // Kreslenie na plátne
      draw(event) {
        if (!this.drawing) return;
  
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.strokeStyle = this.lineColor;
        this.ctx.lineWidth = this.lineWidth;
  
        this.ctx.lineTo(event.offsetX, event.offsetY);
        this.ctx.stroke();
      },
  
      // Zastavenie kreslenia
      stopDrawing() {
        if (!this.drawing) return;
        this.drawing = false;
        this.ctx.closePath();
      },
  
      // Vymazanie plátna
      clearCanvas() {
        const canvas = this.$refs.canvas;
        this.ctx = canvas.getContext('2d');
        this.ctx.clearRect(0, 0, canvas.width, canvas.height);
      },
  
      // Stiahnutie obrázka
      downloadImage() {
        const canvas = this.$refs.canvas;
        const dataUrl = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = dataUrl;
        a.download = 'skica.png';
        a.click();
      },
  
      // Uloženie kresby
      saveDrawing() {
        const canvas = this.$refs.canvas;
        const dataURL = canvas.toDataURL();
        fetch('http://localhost:8000/api/save_drawing/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            question_id: this.questionId,
            image: dataURL,
          }),
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then((data) => {
            console.log('Image saved:', data);
          })
          .catch((error) => {
            console.error('Error:', error);
          });
      },
    },
  };
  </script>
  
  <style scoped>
  .controls {
    margin-top: 10px;
  }
  button {
    margin-right: 10px;
    padding: 8px;
    font-size: 14px;
    cursor: pointer;
  }
  canvas {
    border: 1px solid #000;
  }
  </style>
  