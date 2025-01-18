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
    </div>
  </div>
</template>

<script>
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
      ctx: null
    };
  },
  methods: {
    saveDrawing() {
      const canvas = this.$refs.canvas;
      const dataURL = canvas.toDataURL(); // Konverzia kresby na Base64 obrázok
      console.log("data URL",dataURL);
      console.log("ID",this.questionId);
      fetch('http://localhost:8000/api/save_drawing/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`, // Ak používaš JWT
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

    
    // Začiatok kreslenia
    startDrawing(event) {
      this.drawing = true;
      this.ctx = this.$refs.canvas.getContext('2d'); // Získanie kontextu pre kreslenie
      this.ctx.beginPath(); // Začiatok novej čiare
      this.ctx.moveTo(event.offsetX, event.offsetY); // Nastavenie počiatočného bodu
    },
    // Kreslenie na plátne
    draw(event) {
      if (!this.drawing) return;

      this.ctx.lineCap = 'round'; // Zaoblené konce čiar
      this.ctx.lineJoin = 'round'; // Zaoblené spojenie čiar
      this.ctx.strokeStyle = this.lineColor;
      this.ctx.lineWidth = this.lineWidth;

      this.ctx.lineTo(event.offsetX, event.offsetY); // Kreslenie čiary
      this.ctx.stroke(); // Vyplnenie a vykreslenie
    },
    // Zastavenie kreslenia
    stopDrawing() {
      if (!this.drawing) return;
      this.drawing = false;
      this.ctx.closePath(); // Uzavretie cesty po nakreslení čiary
    },
    // Vymazanie plátna
    clearCanvas() {
      const canvas = this.$refs.canvas;
      this.ctx = canvas.getContext('2d');
      this.ctx.clearRect(0, 0, canvas.width, canvas.height); // Vymaže celý obsah
    },
    // Stiahnutie obrázka
    downloadImage() {
      const canvas = this.$refs.canvas;
      const dataUrl = canvas.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = dataUrl;
      a.download = 'skica.png';
      a.click();
    }
  }
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
