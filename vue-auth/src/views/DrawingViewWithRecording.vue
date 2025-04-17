<template>
  <div>
    <h1>{{ question.text }}</h1>
    <div class="toolbar">
  <div class="tooltip-container">
    <label>
      Farba pera:
      <input type="color" v-model="lineColor" />
    </label>
    <span class="tooltip-text">Vyberte farbu pera</span>
  </div>

  <div class="tooltip-container">
    <label>
      Hrúbka pera:
      <input type="range" v-model="lineWidth" min="1" max="20" />
      <span>{{ lineWidth }} px</span>
    </label>
    <span class="tooltip-text">Vyberte hrúbku pera</span>
  </div>

  <div class="tooltip-container">
    <button @click="toggleEraser">
      <i :class="isErasing ? 'bi bi-eraser-fill' : 'bi bi-brush'"></i>
    </button>
    <span class="tooltip-text">Prepínať medzi guma a pero</span>
  </div>

  <div class="tooltip-container">
    <button @click="undo">
      <i class="bi bi-arrow-counterclockwise"></i>
    </button>
    <span class="tooltip-text">Krok späť</span>
  </div>

  <div class="tooltip-container">
    <button @click="clearCanvas">
      <i class="bi bi-trash3"></i>
    </button>
    <span class="tooltip-text">Vymazať co ste doposial nakreslili</span>
  </div>

  <div class="tooltip-container">
    <button @click="downloadImage">
      <i class="bi bi-download"></i>
    </button>
    <span class="tooltip-text">Stiahnuť obrázok</span>
  </div>

  <div class="tooltip-container">
    <button @click="saveDrawing">Dokončiť</button>
    <span class="tooltip-text">Uložiť kresbu</span>
  </div>

  <div class="tooltip-container">
    <button @click="toggleRecording">
      <i :class="isRecording ? 'bi bi-stop-circle' : 'bi bi-record-circle'"></i>
      {{ isRecording ? 'Ukončiť nahrávanie' : 'Začať nahrávanie' }}
    </button>
    <span class="tooltip-text">{{ isRecording ? 'Ukončiť nahrávanie' : 'Začať nahrávanie' }}</span>
  </div>
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
      canvasWidth: window.innerWidth * 0.9,
      canvasHeight: window.innerHeight * 0.9,
      drawing: false,
      lineColor: '#000000',  // Farba pera
      lineWidth: 5,  // Hrúbka čiary
      ctx: null,
      recorder: null,
      stream: null,
      videoUrl: null,
      mediaChunks: [],
      question: {},
      isErasing: false,
      history: [],
      maxHistory: 3,
      isRecording: false,
    };
  },
 
  methods: {
    toggleRecording() {
      if (this.isRecording) {
        this.stopRecording();
      } else {
        this.startRecording();
      }
      this.isRecording = !this.isRecording;  // Prepnutie tlačidla
    },
    saveState() {
      const canvas = this.$refs.canvas;
      this.history.push(canvas.toDataURL()); // Uloží aktuálny stav ako obrázok

      if (this.history.length > this.maxHistory) {
        this.history.shift(); // Odstráni najstarší záznam, ak prekročíme limit
      }
    },
    undo() {
      if (this.history.length === 0) return;
      
      const canvas = this.$refs.canvas;
      const ctx = canvas.getContext('2d');
      const previousState = this.history.pop(); // Vrátime posledný uložený stav

      const img = new Image();
      img.src = previousState;
      img.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0); // Obnovíme predchádzajúci stav
      };
    },
    toggleEraser() {
      this.isErasing = !this.isErasing; // Prepnutie medzi kreslením a gumovaním
    },
    hasBackgroundImage() {
      return this.question.image_url !== null;
    },
    // Začiatok kreslenia
    startDrawing(event) {
      this.saveState();
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
      this.ctx.strokeStyle = this.isErasing ? '#FFFFFF' :this.lineColor;
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
      if (this.hasBackgroundImage) {
        this.loadBackgroundImage();   
      }
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

    // // Uloženie kresby
    // saveDrawing() {
    //   const canvas = this.$refs.canvas;
    //   const dataURL = canvas.toDataURL();
    //   fetch('http://localhost:8000/api/save_drawing/', {
    //     method: 'POST',
    //     headers: {
    //       'Content-Type': 'application/json',
    //       Authorization: `Bearer ${localStorage.getItem('token')}`,
    //     },
    //     body: JSON.stringify({
    //       question_id: this.questionId,
    //       image: dataURL,
    //     }),
    //   })
    //     .then((response) => {
    //       if (!response.ok) {
    //         throw new Error('Network response was not ok');
    //       }
    //       return response.json();
    //     })
    //     .then((data) => {
    //       console.log('Image saved:', data);
    //     })
    //     .catch((error) => {
    //       console.error('Error:', error);
    //     });
    //     console.log("Test ID:", this.testId);
    //     this.router.push(`/tests/${this.testId}/public`)
    // },
    saveDrawing() {
      const canvas = this.$refs.canvas;
      canvas.toBlob((blob) => {
        const formData = new FormData();
        formData.append('image', blob, 'drawing.png');
        formData.append('question_id', this.questionId);

        fetch('http://localhost:8000/api/save_drawing/', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
          body: formData,
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then((data) => {
            console.log('Image saved:', data);
            this.router.push(`/tests/${this.testId}/public`);
          })
          .catch((error) => {
            console.error('Error:', error);
          });
      }, 'image/png');
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
    async fetchQuestion() {
      try {
        console.log("ide fetchQuestion");
        const response = await fetch(`http://localhost:8000/api/questions/${this.questionId}/`);
        if (!response.ok) {
          throw new Error('Chyba pri načítaní dát');
        }
        const data = await response.json();
        this.question = data;
        console.log("preslo v fetch");

        if (this.hasBackgroundImage) {
          this.loadBackgroundImage();
          console.log("preslo v fetch2");
        }
      } catch (error) {
        console.error('Chyba pri načítaní otázky:', error);
      }
    },

    
    loadBackgroundImage() {
      const canvas = this.$refs.canvas;
      if (!canvas) return;
      
      this.ctx = canvas.getContext('2d');
      const img = new Image();
      img.crossOrigin = "anonymous";  

      console.log("Obrázok URL:", this.question.image_url);
      
      img.src = this.question.image_url;
      
      img.onload = () => {
        const imgWidth = img.width;
        const imgHeight = img.height;
        const variable = (this.canvasWidth*0.9)/imgWidth;
        canvas.height = imgHeight * variable ;
        canvas.width = imgWidth * variable ;
    
        console.log("Obrázok načítaný a vykreslený");
        this.ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        this.ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      };
      
      img.onerror = () => {
        console.error("Chyba pri načítaní obrázka");
      };
    }
  },
  mounted() {
    this.fetchQuestion();
    console.log("prebieha")
    if (this.hasBackgroundImage) {
      console.log("prebieha2")
      this.loadBackgroundImage();   
    }
  },
};
</script>

<!-- <style scoped>
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
</style> -->
<style scoped>
.tooltip-container {
    position: relative;
    display: inline-block;
    text-align: center;
    justify-content: center;
}

.tooltip-container .tooltip-text {
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    background-color: white;
    color: var(--color-button-hover);
    font-weight: bold;
    padding: 6px 10px;
    border-radius: 5px;
    white-space: nowrap;
    font-size: 0.8rem;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease-in-out, visibility 0s linear 0.3s;
    border: 3px solid var(--color-lightblue);
}

.tooltip-container:hover .tooltip-text {
    opacity: 1;
    visibility: visible;
    transition-delay: 2s;  
}

.tooltip-container:not(:hover) .tooltip-text {
    transition-delay: 0s;
}

/* Celý kontajner */
div {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
  border-radius: 10px;
}

/* Nadpis */
h1 {
  color: #333;
  font-size: 24px;
  margin-bottom: 10px;
}

/* Toolbar */
.toolbar {
  display: flex;
  flex-direction: row;
  gap: 15px;
  align-items: center;
  background: #fff;
  padding: 10px 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
}

.toolbar label {
  font-size: 14px;
  color: #555;
  display: flex;
  align-items: center;
  gap: 5px;
}

input[type="color"],
input[type="range"] {
  cursor: pointer;
}

/* Tlačidlá */
button {
  background: #8c00ff;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

button:hover {
  background: #8c00ff;
}

button i {
  font-size: 18px;
}

/* Kresliace plátno */
canvas {
  border: 2px solid #ddd;
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
}

/* Ovládacie tlačidlá */
.controls {
  display: flex;
  flex-direction: row;
  gap: 10px;
}

.controls button {
  background: #28a745;
}

.controls button:hover {
  background: #218838;
}

/* Prehrávač videa */
video {
  margin-top: 10px;
  width: 100%;
  max-width: 600px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
</style>
