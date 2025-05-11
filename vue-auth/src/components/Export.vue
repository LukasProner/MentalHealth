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
        const scales=ref([]);
        const answers= ref([]);

        const generateCSV = (data, headers) => {
            const csvRows = [];
            csvRows.push(headers.join(";"));  
            data.forEach((row) => {
                const values = headers.map((header) =>row[header]||""); 
                csvRows.push(values.join(";"));
            });
            const csvContent = csvRows.join("\n");
            const bom = "\uFEFF";  //BOM (Byte Order Mark) – špeciálny znak, ktorý sa pridáva na začiatok súboru, aby sa správne zobrazoval v Exceli a podporoval Unicode (UTF-8).
            return bom + csvContent;
        };

        const downloadCSV = (csvContent, filename) => {
            const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
            const link = document.createElement("a");
            const url=URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", filename);
            link.style.visibility = "hidden";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        };

        const fetchAnswers=async()=>{
            try {
                const answersResponse=await fetch(`http://localhost:8000/api/tests/${props.testId}/responses/`,{
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: "include",
                });

                if (!answersResponse.ok){
                    throw new Error("Chyba pri načítavaní odpovedí");
                }

                answers.value = await answersResponse.json();
            }catch(error){
                console.error("chyba pri nacitavani odpovedi:", error);
            }
        };

        const exportData=async()=>{
            try {
                const questionsResponse =await fetch(`http://localhost:8000/api/tests/${props.testId}`,{
                    method: "GET",
                    credentials: "include",
                });
                if(!questionsResponse.ok){
                    throw new Error("Chyba pri načítavaní otázok");
                }

                const test = await questionsResponse.json();
                questions.value = test.questions.map((q) => ({
                    id: q.id, 
                    type: "question",
                    text: q.text,
                    question_type: q.question_type,
                    options: q.options.map((o) => `${o.text}-${o.value}`).join(","),
                    category: q.category,
                    min_points: "",
                    max_points: "",
                    response: "",  
                    answer: "",  
                }));

                const scalesResponse = await fetch(`http://localhost:8000/api/tests/${props.testId}/scales/`, {
                    method: "GET",
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
                    answer: "",  
                }));

                await fetchAnswers();
                // console.log("answers: " + JSON.stringify(answers.value));

                const combinedData=[
                    ...questions.value.map((q)=>{
                        // console.log("spracovávam otázku ID:", q.id);

                        if (!answers.value || answers.value.length === 0) {
                            return { ...q, answer: "" };
                        }

                        const allAnswers=answers.value.flatMap(a => a.answers); //flatMap(): Dostaneš jedno ploché pole všetkých odpovedí, teda všetky odpovede sú "zmerané" do jedného poľa.
                        // console.log("Všetky odpovede:", JSON.stringify(allAnswers));

                        const userAnswer=allAnswers.find(a =>a.question_id ===q.id);

                        let parsedAnswer = "";
                        if (userAnswer) {
                            try {
                                const jsonAnswer = JSON.parse(userAnswer.answer.replace(/'/g, '"'));
                                parsedAnswer = jsonAnswer.text || userAnswer.answer;
                            } catch (error) {
                                parsedAnswer = userAnswer.answer; 
                            }
                        }

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
                    "response",  
                    "answer",  
                ];

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

