<template>
    <div>
        <h1>Obrázok</h1>
        <div v-if="loading">
            <p>Načítavam dáta...</p>
        </div>
        <div v-if="error">{{ error }}</div>
        <div v-else>
            <div>
                <h2>Obrázok:</h2>
                <img :src="base64Image" alt="Obrázok" />
            </div>
            <div v-if="videoUrl">
                <h2>Video:</h2>
                <!-- Tlačidlo pre stiahnutie videa -->
                <button @click="downloadVideo">Stiahnuť video</button>
                <video :src="videoUrl" controls></video>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

export default {
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

                // Fetch video
                const videoResponse = await fetch(`http://localhost:8000/api/save_video/${route.params.id}/`,
                    {method: 'GET',}
                );
                if (!videoResponse.ok) {
                    throw new Error('Video sa nepodarilo načítať.');
                }
                const videoData = await videoResponse.json();
                console.log(videoData);
                videoUrl.value = `http://localhost:8000${videoData.video_url}`;
            } catch (err) {
                error.value = err.message;
            } finally {
                loading.value = false;
            }
        };

        // Funkcia pre stiahnutie videa
        const downloadVideo = () => {
            const a = document.createElement('a');
            a.href = videoUrl.value;
            a.download = videoUrl.value.split('/').pop(); // Určí názov súboru na stiahnutie
            a.click();
        };

        onMounted(fetchData);

        return {
            base64Image,
            videoUrl,
            loading,
            error,
            downloadVideo, // Funkcia pre stiahnutie videa
        };
    }
};
</script>
