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
            <!-- <ButtonComp @click="downloadImage" fontSize = "1rem" text="Stiahnuť obrázok"/> -->
            <div v-if="videoUrl" class="video-container">
                <h2>Video:</h2>
                <video :src="videoUrl" controls></video>
            </div>
            <ButtonComp v-if="videoUrl" @click="downloadVideo" fontSize = "1rem" text="Stiahnuť video"/>
            
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
        const base64Image=ref('');
        const videoUrl=ref('');
        const loading=ref(true);
        const error = ref('');
        const route = useRoute();

        const fetchData=async()=>{
            try{
                const response=await fetch(`http://localhost:8000/api/save_drawing/${route.params.id}/`);
                if(!response.ok){
                    throw new Error('obrazok sa nepodarilo nacitat');
                }
                const data = await response.json();

                base64Image.value = data.image_url; 
            }catch(err){
                error.value='Chyba pri načítaní obrázka: '+ err.message;
            }

            try{
                const videoResponse=await fetch(`http://localhost:8000/api/save_video/${route.params.id}/`);
                if(!videoResponse.ok){
                    throw new Error('Video sa nepodarilo načítať.');
                }
                const videoData = await videoResponse.json();
                videoUrl.value = `http://localhost:8000${videoData.video_url}`;
            }catch(err){
                // console.warn('Chyba pri načítaní videa:', err.message);
            }finally{
                loading.value = false;
            }
        };
        const downloadVideo=async()=>{
            try{
                const response = await fetch(videoUrl.value,{ //načíta video z danej URL
                    mode: 'cors',
                });
                if (!response.ok) {
                    throw new Error('Chyba pri sťahovaní videa.');
                }

                const blob = await response.blob(); //vytvori blob
                const url = URL.createObjectURL(blob); 

                const link = document.createElement('a');
                link.href = url;
                link.download = 'moje_video.mp4';  
                document.body.appendChild(link);
                link.click(); // programovo simuluje kliknutie, čím sa video stiahne
                document.body.removeChild(link); //– odstráni link z DOMu.
                URL.revokeObjectURL(url); // zruší dočasnú URL, aby sa uvoľnila pamäť.
            } catch (err) {
                console.error('chyba pri stiahnuti videa:', err);
            }
        };

        onMounted(fetchData);

        return {
            base64Image,
            videoUrl,
            loading,
            error,
            downloadVideo
            // downloadImage
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