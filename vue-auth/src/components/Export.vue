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
        const answers = ref([]);

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

        const fetchAnswers = async () => {
            try {
                const answersResponse = await fetch(`http://localhost:8000/api/tests/${props.testId}/responses/`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: "include",
                });

                if (!answersResponse.ok) {
                    throw new Error("Chyba pri načítavaní odpovedí");
                }

                answers.value = await answersResponse.json();
            } catch (error) {
                console.error("Chyba pri načítavaní odpovedí:", error);
            }
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
                    id: q.id, // ID pre spárovanie odpovedí
                    type: "question",
                    text: q.text,
                    question_type: q.question_type,
                    options: q.options.map((o) => `${o.text}-${o.value}`).join(","),
                    category: q.category,
                    min_points: "",
                    max_points: "",
                    response: "", // Pre škály
                    answer: "", // Nový stĺpec pre odpoveď účastníka
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
                    response: s.response, // Ponechať odpoveď v škále
                    answer: "", // Neaplikuje sa pre škály
                }));

                // Načítať odpovede účastníkov
                await fetchAnswers();
                console.log("answers: " + JSON.stringify(answers.value));

                // Skombinovať otázky a škály + pridať odpovede účastníkov
                const combinedData = [
                    ...questions.value.map((q) => {
                        console.log("Spracovávam otázku ID:", q.id);

                        // Overíme, či máme odpovede a rozbalíme ich
                        if (!answers.value || answers.value.length === 0) {
                            console.warn("answers.value je prázdne alebo nenačítané!");
                            return { ...q, answer: "" };
                        }

                        // Extrahujeme odpovede z `answers.value`
                        const allAnswers = answers.value.flatMap(a => a.answers);
                        console.log("Všetky odpovede:", JSON.stringify(allAnswers));

                        // Nájdeme odpoveď k otázke
                        const userAnswer = allAnswers.find(a => a.question_id === q.id);

                        let parsedAnswer = "";
                        if (userAnswer) {
                            try {
                                // Pokúsime sa odpoveď analyzovať ako JSON
                                const jsonAnswer = JSON.parse(userAnswer.answer.replace(/'/g, '"'));
                                parsedAnswer = jsonAnswer.text || userAnswer.answer;
                            } catch (error) {
                                parsedAnswer = userAnswer.answer; // Ak nejde o JSON, necháme pôvodnú hodnotu
                            }
                        }

                        console.log(`Nájdená odpoveď pre otázku ${q.id}:`, parsedAnswer);
                        return {
                            ...q,
                            answer: parsedAnswer,
                        };
                    }),
                    ...scales.value
                ];


        const headers = [
            "type",
            "text",
            "question_type",
            "options",
            "category",
            "min_points",
            "max_points",
            "response", // Odpoveď pre škály
            "answer", // Nový stĺpec pre odpovede účastníkov
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

