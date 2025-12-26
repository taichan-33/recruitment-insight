<script setup>
defineProps({
    prediction: Object,
    training: Boolean,
    industries: Array,
    prefectures: Array,
    // v-model props
    mlIndustry: String,
    mlLocation: String,
    mlWageType: String
})

defineEmits([
    'update:mlIndustry',
    'update:mlLocation',
    'update:mlWageType',
    'train',
    'predict'
])
</script>

<template>
    <div class="predict-panel">
        <div class="train-section">
            <h3>🧠 AIモデルの再学習</h3>
            <p>最新の求人データを学習して予測モデルを更新します。</p>
            <button @click="$emit('train')" :disabled="training" class="btn-secondary">
                {{ training ? '学習中...' : 'モデル再学習' }}
            </button>
        </div>

        <div class="predict-form">
            <h3>💰 給与予測</h3>
            <div class="form-row">
                <label>業界:</label>
                <select :value="mlIndustry" @change="$emit('update:mlIndustry', $event.target.value)">
                    <option v-for="ind in industries" :key="ind" :value="ind">{{ ind }}</option>
                </select>
            </div>
            <div class="form-row">
                <label>勤務地:</label>
                <select :value="mlLocation" @change="$emit('update:mlLocation', $event.target.value)">
                    <option v-for="pref in prefectures" :key="pref" :value="pref">{{ pref }}</option>
                </select>
            </div>
            <div class="form-row">
                <label>給与形態:</label>
                <select :value="mlWageType" @change="$emit('update:mlWageType', $event.target.value)">
                    <option value="monthly">月給</option>
                    <option value="hourly">時給</option>
                </select>
            </div>
            <button @click="$emit('predict')" class="btn-primary btn-predict">予測実行</button>
        </div>

        <!-- 予測結果 -->
        <div v-if="prediction" class="prediction-result" :class="{
            'result-success': prediction.status === 'success',
            'result-error': prediction.status === 'error'
        }">
            <div v-if="prediction.status === 'success'">
                <div class="result-label">予測給与</div>
                <div class="result-value">
                    {{ Math.round(prediction.predicted_wage).toLocaleString() }}円
                    <span class="wage-type">
                        ({{ prediction.wage_type === 'monthly' ? '月給' : '時給' }})
                    </span>
                </div>
                <div class="result-details">
                    信頼区間: {{ Math.round(prediction.confidence_interval[0]).toLocaleString() }}円 〜
                    {{ Math.round(prediction.confidence_interval[1]).toLocaleString() }}円
                </div>
            </div>
            <div v-else>
                予測エラー: {{ prediction.message }}
            </div>
        </div>
    </div>
</template>

<style scoped>
.predict-panel {
    display: grid;
    gap: 30px;
}

.train-section {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    border-left: 5px solid #3498db;
}

.predict-form {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

h3 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #2c3e50;
}

.form-row {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
}

.form-row label {
    min-width: 80px;
    font-weight: bold;
    color: #34495e;
}

.form-row select {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
}

.btn-primary,
.btn-secondary {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.3s;
    color: white;
}

.btn-primary {
    background: #42b883;
    width: 100%;
}

.btn-primary:hover {
    background: #3aa876;
}

.btn-secondary {
    background: #3498db;
}

.btn-secondary:disabled {
    background: #95a5a6;
}

.prediction-result {
    margin-top: 20px;
    padding: 25px;
    border-radius: 12px;
    animation: fadeIn 0.5s;
}

.result-success {
    background: linear-gradient(135deg, #42b883, #2d9f6e);
    color: white;
    text-align: center;
    box-shadow: 0 4px 15px rgba(66, 184, 131, 0.4);
}

.result-error {
    background: #fee;
    color: #c00;
    border: 1px solid #ffcdd2;
}

.result-value {
    font-size: 2.5rem;
    font-weight: bold;
    margin: 10px 0;
}

.wage-type {
    font-size: 1rem;
    opacity: 0.9;
    font-weight: normal;
}

.result-details {
    background: rgba(255, 255, 255, 0.2);
    padding: 8px 15px;
    border-radius: 20px;
    display: inline-block;
    font-size: 0.9rem;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
