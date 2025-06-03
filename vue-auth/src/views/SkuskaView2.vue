<template>
    <button @click="clearCanvas">
        vymazat
    </button>
    <button @click="downloadImage">
        stiahnut
    </button>
    <button @click="saveDrawing">Dokončiť</button>
    <button @click="startRecorting">Natocit</button>
    <canvas 
        ref="canvas"
        :width="canvasWidth"
        :height="canvasHeight"
        @mousedown="startDrawing"
        @mousemove="draw"
        @mouseup="stopDrawing"
        @mouseleave="stopDrawing"
    ></canvas>
</template>

<script>
import {  useRoute } from 'vue-router';
import { onMounted } from 'vue';

export default{
    setup(){
        const route = useRoute();
        const questionId = Number(route.query.question_id);
        const testId = Number(route.query.testId);
        console.log("Query ID:", questionId, " test Id ", testId);
        return{testId, questionId}
    },

    data(){
        return{
            canvasWidth: window.innerWidth*0.9,
            canvasHeight: window.innerHeight * 0.9,

            ctx:null,
            isDrawing:false,
            question:{},
            stream: null,

        };
    },
    methods:{
        startDrawing(event){
            this.isDrawing = true;
            this.ctx = this.$refs.canvas.getContext('2d');
            this.ctx.beginPath();
            this.ctx.moveTo(event.offsetX, event.offsetY)
        },

        draw(event){
            if(!this.isDrawing) return;
            this.ctx.lineTo(event.offsetX, event.offsetY);
            this.ctx.stroke();
        },

        stopDrawing(event){
            if(!this.isDrawing) return;
            this.isDrawing = false;
            this.ctx.closePath();
        },

        clearCanvas(){
            const canvas = this.$refs.canvas;
            this.ctx = this.$refs.canvas.getContext('2d');
            this.ctx.clearRect(0,0,canvas.width, canvas.height);
        },

        async fetchQuestions(){
            try{
                console.log("question Id = ",this.questionId)
                const response = await fetch(`http://localhost:8000/api/questions/${this.questionId}/`);
                this.question = await response.json();
                console.log("tu vse ok");
                if(this.hasBackground()){
                    this.loadBackground();
                }
                console.log("tu vse ok tez");

            }catch(error){
                console.error("chyba pri nacitani otazky:", error);
            }
        },

        hasBackground(){
            return this.question.image_url!=null;
        },

        loadBackground(){
            const canvas = this.$refs.canvas;
            this.ctx = this.$refs.canvas.getContext('2d');

            const img = new Image();
            img.crossOrigin="anonymous";
            img.src = this.question.image_url;

            img.onload =()=>{
                const imgWidth = img.width;
                const imgHeight = img.height;
                const variable = (this.canvasWidth*0.9)/imgWidth;
                canvas.height = imgHeight * variable ;
                canvas.width = imgWidth * variable ;
                this.ctx.clearRect(0, 0, canvas.width, canvas.height);
                this.ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            }
        },

        downloadImage(){
            const canvas=this.$refs.canvas;
            const dataUrl = canvas.toDataURL('image/png');
            const a= document.createElement('a')
            a.href = dataUrl;
            a.download='skica.png';
            a.click();
        },

        async saveDrawing(){
            const canvas= this.$refs.canvas;
            canvas.toBlob(async(blob)=>{
                const formData = new FormData();
                formData.append('image', blob, 'drawing.png');
                formData.append('question_id',this.questionId);

            try{
                const response = await fetch('http://localhost:8000/api/save_drawing/',{
                    method: 'POST',
                    headers:{
                        Authorization:`Bearer ${localStorage.getItem('token')}`,
                    },
                    body:formData,
                });
                if(!response.ok){
                    const errorDetail = await response.test();
                    throw new Error(`chyba pri ukladani obrazka: ${errorDetail}`);
                }

                const data = await response.json();
                this.$router.push(`/tests/${this.testId}/public`);
            }catch(error){
                console.error('Chyba pri ukladani:', error);
            }
            },'image/png');
        },

        async startRecorting(){
            try{
                const stream = await navigator.mediaDevices.getDisplayMedia({
                    video:true
                })
                this.mediaRecorder = new MediaRecorder(stream);
                this.chunks=[];

                this.mediaRecorder.ondataavailable=event=>{
                    if(event.data.size > 0){
                        this.chunks.push(event.data);
                    }
                };

                this.mediaRecorder.onstop= this.saveRecorting;
                this.mediaRecorder.start();
            }catch(error){
                //
            }
        },
        
        async saveRecorting(){
            const blob = new Blob(this.chunks,{type: 'video/webm'});
            const formData = new FormData();
            formData.append('video', blob);
            formData.append('question_id', this.questionId);
        
            try{
                const response = await fetch('http://localhost:8000/api/save_video/', {
                    method: 'POST',
                    body : formData,
                });
            }catch(error){
                //nic
            }
        },

    },
    mounted() {
        this.fetchQuestions();
        // console.log("prebieha")
        if (this.hasBackground) {
        // console.log("prebieha2")
            this.loadBackground();   
        }
    },
}
</script>

<style scoped>
    canvas{
        border: 2px solid;
    }
</style>