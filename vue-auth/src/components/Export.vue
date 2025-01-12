<template>
    <div>
        <button @click="exportQuestions">Exportovať dáta</button>
    </div>
</template>
<script>
import { ref } from "vue";
export default{
    name : "ExportData",
    props: {
        testId: {
            type: Number,
            required: true,
        },
    },
    setup(props){
        const questions = ref([]);
        const scales = ref([]);
        
        const generateCSV = (data, headers) => {
            const csvRows = [];
            csvRows.push(headers.join(";")); 
            data.forEach((row) => {
                const values = headers.map((i) => row[i] || ""); // Extrahuj hodnoty
                csvRows.push(values.join(";"));
            });
            const csvContent = csvRows.join("\n");
            const bom = "\uFEFF"; // Pridanie UTF-8 BOM
            return bom + csvContent;
        };

        // Funkcia na stiahnutie súboru
        const downloadCSV = (csvContent, filename) => {
            const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
            const link = document.createElement("a");
            const url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", filename);
            link.style.visibility = "hidden";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        };

        // Export otázok
        const exportQuestions = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/tests/${props.testId}`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: "include",
                });

                if (!response.ok) {
                    throw new Error("Chyba pri načítavaní otázok");
                }

                const test = await response.json();
                questions.value = test.questions;
                const headers = ["text", "question_type", "options", "category"];
                const csvContent = generateCSV(
                    questions.value.map((q) => ({
                        text: q.text,
                        question_type: q.question_type,
                        options: q.options.map((o) => `${o.text}-${o.value}`).join(","),
                        category: q.category,
                    })),
                    headers
                );

                downloadCSV(csvContent, "questions.csv");
                alert("Otázky boli úspešne exportované!");
            } catch (error) {
                console.error("Chyba pri exporte otázok:", error);
            }
            exportScales();
        };

        // Export škál
        const exportScales = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/tests/${props.testId}/scales/`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: "include",
                });

                if (!response.ok) {
                    throw new Error("Chyba pri načítavaní škál");
                }

                scales.value = await response.json();
                const headers = ["min_points", "max_points", "response", "category"];
                const csvContent = generateCSV(scales.value, headers);

                downloadCSV(csvContent, "scales.csv");
                alert("Škály boli úspešne exportované!");
            } catch (error) {
                console.error("Chyba pri exporte škál:", error);
            }
        };

        return {
            exportQuestions,
            exportScales,
        };
    },
};
</script>
   