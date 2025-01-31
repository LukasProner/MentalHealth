<template>
    <div>
        <ButtonComp text="Stiahnúť otázky" fontSize="1rem" @click="exportData" />
    </div>
</template>

<script>
import { ref } from "vue";
import ButtonComp from "./ButtonComp.vue";
export default {
    name: "ExportData",
    props: {
        testId: {
            type: Number,
            required: true,
        },
    },
    components: {
        ButtonComp
    },
    setup(props) {
        const questions = ref([]);
        const scales = ref([]);

        const generateCSV = (data, headers) => {
            const csvRows = [];
            csvRows.push(headers.join(";")); // Pridať hlavičky
            data.forEach((row) => {
                const values = headers.map((header) => row[header] || ""); // Extrahuj hodnoty
                csvRows.push(values.join(";"));
            });
            const csvContent = csvRows.join("\n");
            const bom = "\uFEFF"; // Pridať UTF-8 BOM
            return bom + csvContent;
        };

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

        const exportData = async () => {
            try {
                // Načítať otázky
                const questionsResponse = await fetch(`http://localhost:8000/api/tests/${props.testId}`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: "include",
                });

                if (!questionsResponse.ok) {
                    throw new Error("Chyba pri načítavaní otázok");
                }

                const test = await questionsResponse.json();
                questions.value = test.questions.map((q) => ({
                    type: "question",
                    text: q.text,
                    question_type: q.question_type,
                    options: q.options.map((o) => `${o.text}-${o.value}`).join(","),
                    category: q.category,
                    min_points: "",
                    max_points: "",
                    response: "",
                }));

                // Načítať škály
                const scalesResponse = await fetch(`http://localhost:8000/api/tests/${props.testId}/scales/`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: "include",
                });

                if (!scalesResponse.ok) {
                    throw new Error("Chyba pri načítavaní škál");
                }

                scales.value = (await scalesResponse.json()).map((s) => ({
                    type: "scale",
                    text: "",
                    question_type: "",
                    options: "",
                    category: s.category,
                    min_points: s.min_points,
                    max_points: s.max_points,
                    response: s.response,
                }));

                // Skombinovať otázky a škály
                const combinedData = [...questions.value, ...scales.value];
                const headers = [
                    "type",
                    "text",
                    "question_type",
                    "options",
                    "category",
                    "min_points",
                    "max_points",
                    "response",
                ];

                // Generovať a stiahnuť CSV
                const csvContent = generateCSV(combinedData, headers);
                downloadCSV(csvContent, "exported_data.csv");

                alert("Dáta boli úspešne exportované!");
            } catch (error) {
                console.error("Chyba pri exporte dát:", error);
            }
        };

        return {
            exportData,
        };
    },
};
</script>

