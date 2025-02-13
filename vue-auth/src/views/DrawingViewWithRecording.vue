   <template>
    <div>
      <h1>Kresliaci skicár</h1>
  
      <!-- Nástroje na kreslenie -->
      <div class="toolbar">
        <label>
          Farba pera:
          <input type="color" v-model="lineColor" />
        </label>
  
        <label>
          Hrúbka pera:
          <input type="range" v-model="lineWidth" min="1" max="20" />
          <span>{{ lineWidth }} px</span>
        </label>
      </div>
  
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
  import { useRoute, useRouter } from 'vue-router';
  
  export default {
    setup() {
      const route = useRoute();
      const questionId = Number(route.query.question_id);
      const testId = Number(route.query.testId);
      console.log("Query ID:", questionId);
      const router = useRouter();
      return { questionId,testId, router };
    },
  
    data() {
      return {
        canvasWidth: 500,
        canvasHeight: 500,
        drawing: false,
        lineColor: '#000000',  // Farba pera
        lineWidth: 5,  // Hrúbka čiary
        ctx: null,
        recorder: null,
        stream: null,
        videoUrl: null,
        mediaChunks: [],
      };
    },
  
    methods: {
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
          console.log("Test ID:", this.testId);
          this.router.push(`/tests/${this.testId}/public`)
      },
  
      // Spustenie nahrávania obrazovky
      startRecording() {
        navigator.mediaDevices.getDisplayMedia({ video: true })
          .then(stream => {
            this.mediaRecorder = new MediaRecorder(stream);
            this.chunks = [];
  
            this.mediaRecorder.ondataavailable = event => {
              if (event.data.size > 0) {
                this.chunks.push(event.data);
              }
            };
  
            this.mediaRecorder.onstop = this.saveRecording;
  
            this.mediaRecorder.start();
          })
          .catch(err => {
            console.error("Error accessing display media:", err);
          });
      },
  
      // Zastavenie nahrávania
      stopRecording() {
        if (this.mediaRecorder) {
          this.mediaRecorder.stop();
        }
      },
  
      // Uloženie videa
      saveRecording() {
        const blob = new Blob(this.chunks, { type: 'video/webm' });
        const formData = new FormData();
        formData.append('video', blob);
        formData.append('question_id', this.questionId);
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
    },
  };
  </script>
  
  <style scoped>
  .toolbar {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
  }
  
  .toolbar label {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  
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
  