 
<template>
    <div class="import">
        <ButtonComp text="Import a Export otázok" @click="openModal" fontSize="1rem"/>

        <!-- Modálne okno -->
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
            <div class="modal-content">
                <h2>Importovanie otázok</h2>
                <div class="modal-section">
                    <input type="file" @change="handleFileImport">
                </div>
                <button class="close-button" @click="closeModal">✖</button>
                <ButtonComp text="Importovať" @click="importData" fontSize="1rem"/>

            </div>
        </div>
    </div>
</template>

<script>
import { ref } from 'vue';
import ButtonComp from './ButtonComp.vue';

export default {
    components: {
        ButtonComp,
    },
    name: "QuestionImport",
    props: {
        testId: {
            type: Number,
            required: true,
        },
    },
    setup(props, { emit }) {
        const file = ref(null);
        const scales = [];
        const openImport = ref(false);
        const showModal = ref(false);

        const openModal = () => {
            showModal.value = true;
        };

        const closeModal = () => {
            showModal.value = false;
        };

        const handleOpenImport = () => {
            openImport.value = !openImport.value; 
            console.log('openImport:', openImport.value);
        };

        const handleClickOutside = (event) => {
            if (!event.target.closest('.import')) {
                openImport.value = false;
            }
        };

        document.addEventListener("click", handleClickOutside);
        
        const handleFileImport = (event) => {
            file.value = event.target.files[0];
        };

        const importData = async () => {
            if (!file.value) {
                alert("Vyberte súbor na import!");
                return;
            }

            const fileContent = await file.value.text(); 
            const rows = fileContent.split("\n").map(row => row.split(";"));
            const [header, ...dataRows] = rows;
            console.log('Header:', header);

            const formattedData = [];
            for (const row of dataRows) {
                if (row.length < 2) continue;
                if (isNaN(row[0])) {
                    const rawOptions = row[2] ? row[2].split(",") : [];
                    const options = rawOptions.map(option => {
                        const [text, value] = option.split("-");
                        return {
                            text: text.trim(),
                            value: value ? parseInt(value.trim(),10) : null,
                            hasValue: !!value,
                        };
                    });

                    const newQuestion = {
                        text: row[0], 
                        question_type: row[1], 
                        options: options, 
                        category: row[3] && row[3].trim() ? row[3].trim() : "Nezaradená"
                    };

                    try {
                        console.log("Posielam otázku:", newQuestion);
                        const response = await fetch(`http://localhost:8000/api/tests/${props.testId}/questions/`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify(newQuestion),
                            credentials: "include",
                        });

                        if (!response.ok) {
                            throw new Error(`Chyba pri ukladaní otázky: ${response.status}`);
                        }

                        const savedQuestion = await response.json();
                        formattedData.push(savedQuestion);
                        console.log("Otázka uložená:", savedQuestion);
                    } catch (error) {
                        console.error("Chyba pri spracovaní otázky:", error);
                    }
                } else {
                    scales.push({
                        min_points: parseFloat(row[0]) || 0,
                        max_points: parseFloat(row[1]) || 0,
                        response: row[2],
                        category: row[3] || "Nezaradená",
                    });
                }
            }

            if (scales.length !== 0) {
                try {
                    await fetch(`http://localhost:8000/api/tests/${props.testId}/scales/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(scales),
                        credentials: 'include',
                    });
                } catch (error) {
                    console.error('Chyba pri ukladaní škál:', error);
                }
            }

            console.log("Scales", scales);

            alert("Import dokončený!");
            emit('import-complete', formattedData, scales);
            scales.length = 0;
        };

        return {
            file,
            openImport,
            handleFileImport,
            handleOpenImport,
            importData,
            openModal,
            showModal,
            closeModal
        };
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

.modal-content {
    background: white;
    width:500px;
    height: 300px;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center; 
    align-items: center; 
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    position: relative;
}

/* Nadpisy sekcií */
.modal-section h3 {
    margin-bottom: 10px;
}

/* Štýl zatváracieho tlačidla */
.close-button {
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