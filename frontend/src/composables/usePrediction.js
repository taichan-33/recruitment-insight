import { ref } from "vue";

export function usePrediction() {
  const mlIndustry = ref("IT・エンジニア");
  const mlLocation = ref("東京都");
  const mlWageType = ref("monthly");
  const mlPrediction = ref(null);
  const mlTraining = ref(false);

  async function trainModel() {
    mlTraining.value = true;
    try {
      const res = await fetch("http://127.0.0.1:5000/api/ml/train", {
        method: "POST",
      });
      const data = await res.json();
      alert(data.message);
    } catch (e) {
      alert("学習エラー: " + e);
    } finally {
      mlTraining.value = false;
    }
  }

  async function predictSalary() {
    try {
      const res = await fetch("http://127.0.0.1:5000/api/ml/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          industry: mlIndustry.value,
          location: mlLocation.value,
          wage_type: mlWageType.value,
        }),
      });
      mlPrediction.value = await res.json();
    } catch (e) {
      console.error("予測エラー:", e);
    }
  }

  return {
    mlIndustry,
    mlLocation,
    mlWageType,
    mlPrediction,
    mlTraining,
    trainModel,
    predictSalary,
  };
}
