<script setup>
defineProps({
    crawlerRunning: Boolean,
    prefectures: Array,
    // v-model props
    forceMode: Boolean,
    selectedPrefecture: String, // 追加
    indeedKeyword: String,
    indeedLocation: String,
    indeedPages: Number
})

defineEmits([
    'update:forceMode',
    'update:selectedPrefecture', // 追加
    'update:indeedKeyword',
    'update:indeedLocation',
    'update:indeedPages',
    'runHellowork',
    'runIndeed'
])
</script>

<template>
    <div class="crawler-container">
        <!-- HelloWork クローラー -->
        <div class="crawler-panel">
            <h3>🤖 HelloWork クローラー</h3>
            <p class="description">ハローワークの最新求人を収集します。定期実行されていますが、手動で即時実行も可能です。</p>
            <div class="crawler-controls">
                <select :value="selectedPrefecture" @change="$emit('update:selectedPrefecture', $event.target.value)">
                    <option v-for="pref in prefectures" :key="pref" :value="pref">{{ pref }}</option>
                </select>

                <label class="force-label">
                    <input type="checkbox" :checked="forceMode"
                        @change="$emit('update:forceMode', $event.target.checked)" />
                    強制収集（既存データを無視）
                </label>
                <button @click="$emit('runHellowork')" :disabled="crawlerRunning" class="btn-primary">
                    {{ crawlerRunning ? '実行中...' : '収集開始' }}
                </button>
            </div>
        </div>

        <!-- Indeed クローラー -->
        <div class="indeed-panel">
            <h3>🔍 Indeed クローラー</h3>
            <p class="description">Indeedから求人を検索して収集します。</p>
            <div class="indeed-controls">
                <input type="text" :value="indeedKeyword" @input="$emit('update:indeedKeyword', $event.target.value)"
                    placeholder="キーワード（例: エンジニア）" />

                <select :value="indeedLocation" @change="$emit('update:indeedLocation', $event.target.value)">
                    <option v-for="pref in prefectures" :key="pref" :value="pref">{{ pref }}</option>
                </select>

                <div class="page-input">
                    <input type="number" :value="indeedPages"
                        @input="$emit('update:indeedPages', Number($event.target.value))" min="1" max="10" /> ページ
                </div>

                <button @click="$emit('runIndeed')" :disabled="crawlerRunning" class="btn-indeed">
                    {{ crawlerRunning ? '検索中...' : 'Indeed検索' }}
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.crawler-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.crawler-panel,
.indeed-panel {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.indeed-panel {
    background: #f0f4ff;
    border: 1px solid #dbeafe;
}

h3 {
    margin-top: 0;
    margin-bottom: 10px;
    color: #2c3e50;
}

.description {
    color: #7f8c8d;
    margin-bottom: 20px;
    font-size: 0.95rem;
}

.crawler-controls {
    display: flex;
    align-items: center;
    gap: 20px;
}

.force-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-weight: 500;
}

.indeed-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    align-items: center;
}

.indeed-controls input[type="text"] {
    flex: 1;
    min-width: 200px;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
}

.crawler-controls select,
.indeed-controls select {
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    min-width: 100px;
}

.page-input {
    display: flex;
    align-items: center;
    gap: 5px;
}

.page-input input {
    width: 60px;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
}

.btn-primary {
    padding: 12px 24px;
    background: #42b883;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.3s;
}

.btn-primary:disabled {
    background: #a8d5c2;
    cursor: not-allowed;
}

.btn-indeed {
    padding: 12px 24px;
    background: #2557a7;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.3s;
}

.btn-indeed:hover {
    background: #1d4a8e;
}

.btn-indeed:disabled {
    background: #95a5a6;
    cursor: not-allowed;
}
</style>
