<script setup>
defineProps({
    jobs: {
        type: Array,
        required: true
    },
    industries: {
        type: Array,
        default: () => []
    },
    // v-model props
    searchKeyword: String,
    wageMin: [String, Number],
    wageMax: [String, Number],
    filterIndustry: String,
    filterLocation: String
})

defineEmits([
    'update:searchKeyword',
    'update:wageMin',
    'update:wageMax',
    'update:filterIndustry',
    'update:filterLocation',
    'search'
])
</script>

<template>
    <div class="search-panel">
        <h3>🔍 詳細検索</h3>
        <div class="search-controls">
            <input type="text" :value="searchKeyword" @input="$emit('update:searchKeyword', $event.target.value)"
                placeholder="キーワード" />
            <input type="number" :value="wageMin" @input="$emit('update:wageMin', $event.target.value)"
                placeholder="最低給与" />
            <span>〜</span>
            <input type="number" :value="wageMax" @input="$emit('update:wageMax', $event.target.value)"
                placeholder="最高給与" />

            <select :value="filterIndustry" @change="$emit('update:filterIndustry', $event.target.value)">
                <option value="all">全業界</option>
                <option v-for="ind in industries" :key="ind" :value="ind">{{ ind }}</option>
            </select>

            <input type="text" :value="filterLocation" @input="$emit('update:filterLocation', $event.target.value)"
                placeholder="都道府県で絞込" />

            <button @click="$emit('search')" class="btn-primary">検索</button>
        </div>
    </div>

    <!-- 求人リスト -->
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th width="40">形態</th>
                    <th>職種</th>
                    <th>会社名</th>
                    <th>場所</th>
                    <th>給与</th>
                    <th>業界</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="job in jobs.slice(0, 50)" :key="job.id">
                    <td class="type-icon">
                        <span v-if="job.wage_type === 'hourly'" title="時給">🕒</span>
                        <span v-else-if="job.wage_type === 'monthly'" title="月給">📅</span>
                        <span v-else>❓</span>
                    </td>
                    <td class="job-title">{{ job.title?.substring(0, 30) }}...</td>
                    <td>{{ job.company || '-' }}</td>
                    <td>{{ job.location || '-' }}</td>
                    <td class="wage">{{ job.wage_min?.toLocaleString() }}円</td>
                    <td><span class="industry-tag">{{ job.industry || '-' }}</span></td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style scoped>
.search-panel {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}

.search-panel h3 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #34495e;
}

.search-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
}

.search-controls input,
.search-controls select {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
}

.btn-primary {
    padding: 10px 20px;
    background: #42b883;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.3s;
}

.btn-primary:hover {
    background: #3aa876;
}

.table-container {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 15px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th {
    background: #f8f9fa;
    font-weight: bold;
    color: #7f8c8d;
}

tr:hover {
    background: #fdfdfd;
}

.type-icon {
    font-size: 1.2rem;
    text-align: center;
}

.job-title {
    font-weight: bold;
    color: #2c3e50;
}

.wage {
    font-weight: bold;
    color: #e67e22;
}

.industry-tag {
    background: #e8f5e9;
    color: #2e7d32;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.85rem;
}
</style>
