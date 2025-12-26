<script setup>
defineProps({
    activeTab: {
        type: String,
        required: true
    }
})

defineEmits(['update:activeTab'])
</script>

<template>
    <div class="header-container">
        <h1>📊 HelloWork Insight <span class="subtitle">分析ダッシュボード</span></h1>

        <!-- タブナビゲーション -->
        <div class="tab-nav">
            <button :class="{ active: activeTab === 'dashboard' }" @click="$emit('update:activeTab', 'dashboard')">
                📈 ダッシュボード
            </button>
            <button :class="{ active: activeTab === 'crawler' }" @click="$emit('update:activeTab', 'crawler')">
                🤖 データ収集
            </button>
            <button :class="{ active: activeTab === 'search' }" @click="$emit('update:activeTab', 'search')">
                🔍 検索
            </button>
            <button :class="{ active: activeTab === 'predict' }" @click="$emit('update:activeTab', 'predict')">
                🤖 AI給与予測
            </button>
        </div>
    </div>
</template>

<style scoped>
h1 {
    border-bottom: 3px solid #42b883;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

.subtitle {
    font-size: 0.6em;
    color: #7f8c8d;
    font-weight: normal;
}

.tab-nav {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.tab-nav button {
    padding: 12px 24px;
    border: none;
    background: white;
    border-radius: 8px 8px 0 0;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.3s;
}

.tab-nav button.active {
    background: #42b883;
    color: white;
}

.tab-nav button:hover:not(.active) {
    background: #f0f0f0;
}
</style>
