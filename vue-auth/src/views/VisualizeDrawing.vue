<template>
    <div class="visualise-drawing">
        <div v-if="loading" class="loading">
            <p>Načítavam dáta...</p>
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <div v-else>
            <div class="image-container">
                <h2>Obrázok:</h2>
                <img :src="base64Image" alt="Obrázok" />
            </div>
            <ButtonComp @click="downloadImage" fontSize = "1rem" text="Stiahnuť obrázok"/>
            <div v-if="videoUrl" class="video-container">
                <h2>Video:</h2>
                <video :src="videoUrl" controls></video>
            </div>
            <ButtonComp @click="downloadVideo" fontSize = "1rem" text="Stiahnuť video"/>
            
        </div>
    </div>
</template>

<script>
import ButtonComp from '@/components/ButtonComp.vue';
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

export default {
    components: {
        ButtonComp,
    },
    setup() {
        const base64Image = ref('');
        const videoUrl = ref('');
        const loading = ref(true);
        const error = ref('');
        const route = useRoute();

        const fetchData = async () => {
            try {
                // Fetch obrázok
                const imageResponse = await fetch(`http://localhost:8000/api/save_drawing/${route.params.id}/`);
                if (!imageResponse.ok) {
                    throw new Error('Obrázok sa nepodarilo načítať.');
                }
                const imageData = await imageResponse.json();
                base64Image.value = imageData.drawing;
            } catch (err) {
                error.value = 'Chyba pri načítaní obrázka: ' + err.message;
            }

            try {
                // Fetch video (nezastaví načítanie obrázka pri chybe)
                const videoResponse = await fetch(`http://localhost:8000/api/save_video/${route.params.id}/`);
                if (!videoResponse.ok) {
                    throw new Error('Video sa nepodarilo načítať.');
                }
                const videoData = await videoResponse.json();
                videoUrl.value = `http://localhost:8000${videoData.video_url}`;
            } catch (err) {
                console.warn('Chyba pri načítaní videa:', err.message);
            } finally {
                loading.value = false;
            }
        };

        // Funkcia pre stiahnutie videa
        const downloadVideo = () => {
            if (videoUrl.value) {
                const a = document.createElement('a');
                a.href = videoUrl.value;
                a.download = videoUrl.value.split('/').pop();
                a.click();
            }
        };
        const downloadImage = () => {
            if (base64Image.value) {
                const a = document.createElement('a');
                a.href = base64Image.value;
                a.download = 'drawing.png';
                a.click();
            }
        };

        onMounted(fetchData);

        return {
            base64Image,
            videoUrl,
            loading,
            error,
            downloadVideo,
            downloadImage
        };
    }
};
</script>

<style scoped>
.visualise-drawing {
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
}
.image-container, .video-container {
    margin-top: 20px;
}
img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
video {
    width: 100%;
    max-width: 600px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-top: 10px;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #e0f2fe;
  color: #0284c7;
  padding: 20px;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  font-weight: bold;
  font-size: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.error {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fee2e2;
  color: #b91c1c;
  padding: 20px;
  border: 1px solid #fecaca;
  border-radius: 8px;
  font-weight: bold;
  font-size: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.error p{
  margin: 0;
}

</style>