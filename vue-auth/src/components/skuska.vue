<script>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export default {
  name: 'DrawingViewWithRecording',
  setup() {
    const route = useRoute();
    const questionId = Number(route.query.question_id);
    const testId = Number(route.query.testId);
    console.log("Query ID:", questionId);
    const router = useRouter();
    return { questionId, testId, router };
  },

  data() {
    return {
      canvasWidth: 500,
      canvasHeight: 500,
      drawing: false,
      lineColor: '#000000',
      lineWidth: 5,
      ctx: null,
      mediaRecorder: null,
      videoUrl: null,
      chunks: [],
      question: {},
    };
  },

  computed: {
    hasBackgroundImage() {
      return this.question && this.question.image_url;
    }
  },

  methods: {
    startDrawing(event) {
      this.drawing = true;
      this.ctx = this.$refs.canvas.getContext('2d');
      this.ctx.beginPath();
      this.ctx.moveTo(event.offsetX, event.offsetY);
    },

    draw(event) {
      if (!this.drawing) return;

      this.ctx.lineCap = 'round';
      this.ctx.lineJoin = 'round';
      this.ctx.strokeStyle = this.lineColor;
      this.ctx.lineWidth = this.lineWidth;

      this.ctx.lineTo(event.offsetX, event.offsetY);
      this.ctx.stroke();
    },

    stopDrawing() {
      if (!this.drawing) return;
      this.drawing = false;
      this.ctx.closePath();
    },

    clearCanvas() {
      const canvas = this.$refs.canvas;
      this.ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (this.hasBackgroundImage) {
        this.loadBackgroundImage();  // Znovu načítaj pozadie
      }
    },

    downloadImage() {
      const canvas = this.$refs.canvas;
      const dataUrl = canvas.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = dataUrl;
      a.download = 'skica.png';
      a.click();
    },

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
        .then(response => response.json())
        .then(data => {
          console.log('Image saved:', data);
          this.router.push(`/tests/${this.testId}/public`);
        })
        .catch(error => console.error('Error:', error));
    },

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

    stopRecording() {
      if (this.mediaRecorder) {
        this.mediaRecorder.stop();
      }
    },

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

    fetchQuestion() {
      fetch(`http://localhost:8000/api/questions/${this.questionId}/`)
        .then(response => response.json())
        .then(data => {
          this.question = data;
          this.$nextTick(() => {
            if (this.hasBackgroundImage) {
              this.loadBackgroundImage();
            }
          });
        })
        .catch(error => console.error('Chyba pri načítaní otázky:', error));
    },

    loadBackgroundImage() {
      const canvas = this.$refs.canvas;
      this.ctx = canvas.getContext('2d');

      const img = new Image();
      img.crossOrigin = "anonymous";
      img.src = this.question.image_url;

      img.onload = () => {
        this.ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      };
    },
  },

  mounted() {
    this.fetchQuestion();
  },
};
</script>
