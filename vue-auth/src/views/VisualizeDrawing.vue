<template>
    <div>
        <h1>Obrázok</h1>
        <div v-if="loading">
            <p>Načítavam obrázok...</p>
        </div>
        <div v-if="error">{{ error }}</div>
        <div v-else>
            <img :src="base64Image" alt="Obrázok" />
        </div>
    </div>
</template>
<script>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

export default {
    setup() {
        const base64Image = ref('');
        const loading = ref(true);
        const error = ref('');
        const route = useRoute();

        const fetchImage = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/save_drawing/${route.params.id}/`);
            if (!response.ok) {
                throw new Error('Obrázok sa nepodarilo načítať.');
            }
            const data = await response.json();
            base64Image.value = data.drawing;
            console.log(data.drawing);
        } catch (err) {
            error.value = err.message;
        } finally {
            loading.value = false;
        }
        };
        onMounted(fetchImage);

        return {
        base64Image,
        loading,
        error,
        };
    }
}
</script>