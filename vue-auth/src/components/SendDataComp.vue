<template>
    <div>
        <ButtonComp text="Zobraziť link na test" fontSize="1rem" @click="showModal = true" />
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
            <div class="modal">
                <button class="close-btn" @click="closeModal">×</button>
                <h2>Link na test</h2>
                <p><strong>Odkaz:</strong> <a :href="testLink" target="_blank">{{ testLink }}</a></p>
                <p><strong>Kód testu:</strong> {{ testCode }}</p>
                <ButtonComp text="Skopírovať link" @click="copyToClipboard" fontSize = "1rem" />  
            </div>
        </div>
    </div>
</template>
  
  <script>
import ButtonComp from './ButtonComp.vue';

  export default {
    components: {
        ButtonComp,
    },
    props: {
        testId: {
            type: Number,
            required: true
        },
        testCode: {
            type: String,
            required: true
        }
    },
    data() {
        return {
            showModal: false
        };
    },//zistit ci treeba computed
    computed: {
        testLink() {
            console.log(this.testId);
            console.log(this.testCode);
            return `http://localhost:8081/tests/${this.testId}/public`;
        }
    },
    methods: {
        closeModal() {
            this.showModal = false;
        },
        copyToClipboard() {
            navigator.clipboard.writeText(this.testLink)
        }
    }
  };
  </script>
  
<style scoped>
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .modal {
        background: white;
        width: 500px;  
        height: 300px; 
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center; 
        align-items: center; 
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
        position: relative;
    }

    .close-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        background: none;
        border: none;
        font-size: 24px;
        font-weight: bold;
        cursor: pointer;
        color: #555;
        outline: none;
    }

    .close-btn:hover {
        color: #000;
    }
</style>
  