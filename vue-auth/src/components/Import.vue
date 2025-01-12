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
        const scales = [];

        const handleFileImport = (event) =>{
            file.value = event.target.files[0];
        };
        const isHeader = (row) => {
            return row[0] === "min_points";
        };

        const importData = async (testId) => {
            if (!file.value) {
                alert("Vyberte súbor na import!");
                return;
            }

            const fileContent = await file.value.text(); 
            const rows = fileContent.split("\n").map(row => row.split(","));

            const [header, ...dataRows] = rows;
            // console.log('Test ID:',props.testId)
            // console.log('Header:', header);
            // console.log('Data rows:', dataRows);
            const formattedData = [];
            for (const row of dataRows) {
                if (row.length < 2 || isHeader(row)) continue;
                if (isNaN(row[0])) {
                    const rawOptions = row[2] ? row[2].split(";") : [];
                    const options = rawOptions.map(option => {
                        const [text, value] = option.split("-");
                        // console.log('text:',text,'value:',value)
                        return {
                            text: text.trim(),
                            value: value ? value.trim() : null,
                            hasValue: !!value,
                        };
                    });

                    const newQuestion = {
                        text: row[0], 
                        question_type: row[1], 
                        options: options, 
                        category: row[3] || "Nezaradená",
                    };
                    try {
                        // console.log("Posielam otázku:", newQuestion);
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
                        formattedData.push(savedQuestion);
                        // console.log("Otázka uložená:", savedQuestion);
                    } catch (error) {
                        console.error("Chyba pri spracovaní otázky:", error);
                    }
                }else {
                    scales.push({
                        min_points: parseFloat(row[0]) || 0,
                        max_points: parseFloat(row[1]) || 0,
                        response: row[2],
                        category: row[3] || "Nezaradená",
                    });
                }
            }
            if(scales.length != 0){
                try {
                    fetch(`http://localhost:8000/api/tests/${props.testId}/scales/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(scales),
                        credentials: 'include',
                    });
                } catch (error) {
                    console.error('Chyba pri ukladaní škál:', error);
                }
            }
            console.log("Scales", scales);

            alert("Import dokončený!");
            // console.log("Škály:", scales);
            // console.log('Data rows:', dataRows);    
            emit('import-complete', formattedData,scales);
            scales.length = 0;
        
        };

        return{
            file,
            handleFileImport,
            importData,
        }
    }
    
}
</script>
