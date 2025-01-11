<template>
    <div class="import">
        <h3>import otázok a odpovedí</h3>
        <div>
            <input type="file" @change="handleFileImport">
            <button @click="importData">Importovat</button>
        </div>
    </div>
</template>
<script>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';

export default {
    name: "QuestionImport",
    props: {
        testId: {
            type: Number,
            required: true,
        },
    },
    setup(props, { emit }){
        const file = ref(null);

        const handleFileImport = (event) =>{
            file.value = event.target.files[0];
        };

        const importData = async (testId) => {
            if (!file.value) {
                alert("Vyberte súbor na import!");
                return;
            }

            const fileContent = await file.value.text(); 
            const rows = fileContent.split("\n").map(row => row.split(","));

            const [header, ...dataRows] = rows;
            console.log('Test ID:',props.testId)
            for (const row of dataRows) {
                if (row.length < 2) continue; // Skontroluj, či riadok obsahuje dostatok údajov

                const newQuestion = {
                    text: row[0], // Prvý stĺpec je text otázky
                    question_type: row[1], // Druhý stĺpec je typ otázky
                    options: row[2] ? row[2].split(";") : [], // Tretí stĺpec obsahuje možnosti (oddelené bodkočiarkou)
                    category: row[3] || "Nezaradená", // Štvrtý stĺpec je kategória
                };

                try {
                    const response = await fetch(`http://localhost:8000/api/tests/${props.testId}/questions/`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify(newQuestion),
                        credentials: "include",
                    });

                    if (!response.ok) {
                        throw new Error(`Chyba pri ukladaní otázky: ${response.status}`);
                    }

                    const savedQuestion = await response.json();
                    console.log("Otázka uložená:", savedQuestion);
                } catch (error) {
                    console.error("Chyba pri spracovaní otázky:", error);
                }
            }


            alert("Import dokončený!");
            emit('import-complete', dataRows);
        };

        return{
            file,
            handleFileImport,
            importData,
        }
    }
    
}
</script>
