<script setup>
import { computed } from 'vue'
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale,
    ArcElement,
    LineElement,
    PointElement
} from 'chart.js'
import { Bar, Pie, Line } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, LineElement, PointElement, Title, Tooltip, Legend)

const props = defineProps({
    loading: Boolean,
    stats: Object,
    hotIndustries: Array,
    industryStats: Array,
    industryRanking: Array,
    salaryTrend: Array,
    industryComparison: Array,
    heatmapData: Object,
    locationStats: Array,
    industries: Array
})

// チャート設定
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: 'top' } },
    elements: {
        point: {
            radius: 6,
            hoverRadius: 8
        },
        line: {
            borderWidth: 3
        }
    }
}

const pieOptions = { responsive: true, maintainAspectRatio: false, plugins: { title: { display: true, text: '業界別求人数' } } }
const barOptions = { responsive: true, maintainAspectRatio: false, plugins: { title: { display: true, text: '業界別平均賃金' } } }

// データ加工 (Computed)
const industryPieData = computed(() => {
    if (!props.industryStats?.length) {
        return { labels: props.industries, datasets: [{ backgroundColor: ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#95a5a6'], data: [0, 0, 0, 0, 0, 0] }] }
    }
    return {
        labels: props.industryStats.map(s => s.industry || 'その他'),
        datasets: [{ backgroundColor: ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#95a5a6'], data: props.industryStats.map(s => s.count) }]
    }
})

const industryWageData = computed(() => {
    if (!props.industryRanking?.length) return { labels: [], datasets: [] }
    return {
        labels: props.industryRanking.map(r => r.industry),
        datasets: [
            { label: '平均月給(万円)', backgroundColor: '#42b883', data: props.industryRanking.map(r => r.avg_monthly ? Math.round(r.avg_monthly / 10000) : 0) },
            { label: '平均時給(円)', backgroundColor: '#3498db', data: props.industryRanking.map(r => r.avg_hourly || 0) }
        ]
    }
})

const salaryTrendChartData = computed(() => ({
    labels: props.salaryTrend.map(d => d.month).reverse(),
    datasets: [{
        label: '平均月給（円）',
        data: props.salaryTrend.map(d => d.avg_wage).reverse(),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        tension: 0.3,
        fill: true
    }]
}))

const industryComparisonChartData = computed(() => ({
    labels: props.industryComparison.map(d => d.industry),
    datasets: [
        {
            label: '平均月給（万円）',
            data: props.industryComparison.map(d => Math.round(d.avg_wage / 10000)),
            backgroundColor: '#3b82f6'
        },
        {
            label: '求人数（件）',
            data: props.industryComparison.map(d => d.job_count),
            backgroundColor: '#10b981'
        }
    ]
}))
</script>

<template>
    <div class="dashboard-content">
        <div v-if="loading" class="loading">データを分析中...</div>

        <div v-else>
            <!-- 統計サマリー -->
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-number">{{ stats.total_count || 0 }}</div>
                    <div class="stat-label">総求人数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ (stats.avg_monthly_wage || 0).toLocaleString() }}円</div>
                    <div class="stat-label">平均月給</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ (stats.avg_hourly_wage || 0).toLocaleString() }}円</div>
                    <div class="stat-label">平均時給</div>
                </div>
            </div>

            <!-- ホット業界ランキング -->
            <div class="section">
                <h2>🔥 ホット業界ランキング</h2>
                <div class="ranking-list">
                    <div v-for="(item, index) in hotIndustries" :key="index" class="ranking-item">
                        <span class="rank">{{ index + 1 }}</span>
                        <span class="industry-name">{{ item.industry }}</span>
                        <span class="job-count">{{ item.job_count }}件</span>
                        <span class="avg-wage">平均 {{ Math.round((item.estimated_monthly || 0) / 10000) }}万円</span>
                        <div class="score-bar"
                            :style="{ width: (item.hot_score / (hotIndustries[0]?.hot_score || 1) * 100) + '%' }">
                        </div>
                    </div>
                </div>
            </div>

            <!-- グラフエリア -->
            <div class="charts-row">
                <div class="chart-card">
                    <Pie :data="industryPieData" :options="pieOptions" />
                </div>
                <div class="chart-card">
                    <Bar :data="industryWageData" :options="barOptions" />
                </div>
            </div>

            <!-- 詳細分析グラフ（New） -->
            <div class="section">
                <h2>📈 給与トレンド（月別推移）</h2>
                <div class="chart-container-large">
                    <Line :data="salaryTrendChartData" :options="chartOptions" />
                </div>
            </div>

            <div class="section">
                <h2>📊 業界別 賃金・求人数比較</h2>
                <div class="chart-container-large">
                    <Bar :data="industryComparisonChartData" :options="chartOptions" />
                </div>
            </div>

            <div class="section">
                <h2>🌡 地域 × 業界 ヒートマップ</h2>
                <div class="heatmap-container">
                    <div class="heatmap-header">
                        <div class="heatmap-cell header-cell">地域 / 業界</div>
                        <div v-for="ind in heatmapData.industries" :key="ind" class="heatmap-cell header-cell">
                            {{ ind }}
                        </div>
                    </div>
                    <div v-for="(row, i) in heatmapData.data" :key="i" class="heatmap-row">
                        <div class="heatmap-cell row-header">{{ heatmapData.prefectures[i] }}</div>
                        <div v-for="(val, j) in row" :key="j" class="heatmap-cell"
                            :style="{ backgroundColor: `rgba(66, 184, 131, ${val / 100})` }">
                            {{ val }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- 地域別求人数 -->
            <div class="section">
                <h2>📍 地域別求人数 TOP10</h2>
                <div class="location-grid">
                    <div v-for="loc in locationStats.slice(0, 10)" :key="loc.location" class="location-card">
                        <div class="location-name">{{ loc.location }}</div>
                        <div class="location-count">{{ loc.count }}件</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.loading {
    text-align: center;
    padding: 3rem;
    font-size: 1.5rem;
}

/* 統計カード */
.stats-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: linear-gradient(135deg, #42b883, #2d9f6e);
    color: white;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
}

.stat-number {
    font-size: 2rem;
    font-weight: bold;
}

.stat-label {
    font-size: 0.9rem;
    opacity: 0.9;
    margin-top: 5px;
}

/* セクション */
.section {
    margin-bottom: 30px;
}

h2 {
    font-size: 1.2rem;
    margin-bottom: 15px;
    color: #34495e;
    border-left: 5px solid #42b883;
    padding-left: 10px;
}

/* ランキング */
.ranking-list {
    background: white;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.ranking-item {
    display: flex;
    align-items: center;
    padding: 12px;
    border-bottom: 1px solid #eee;
    position: relative;
    overflow: hidden;
}

.ranking-item:last-child {
    border-bottom: none;
}

.rank {
    width: 30px;
    font-weight: bold;
    color: #42b883;
}

.industry-name {
    flex: 1;
    font-weight: bold;
    z-index: 1;
}

.job-count {
    width: 80px;
    text-align: right;
    color: #7f8c8d;
    z-index: 1;
    font-size: 0.9rem;
}

.avg-wage {
    width: 120px;
    text-align: right;
    font-weight: bold;
    color: #e67e22;
    z-index: 1;
}

.score-bar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    background: rgba(66, 184, 131, 0.1);
    z-index: 0;
}

/* グラフエリア */
.charts-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 30px;
}

.chart-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    height: 300px;
}

/* 地域カード */
.location-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
}

.location-card {
    background: white;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s;
}

.location-card:hover {
    transform: translateY(-3px);
}

.location-name {
    font-weight: bold;
    margin-bottom: 5px;
}

.location-count {
    color: #42b883;
}

/* 詳細分析グラフ・ヒートマップ */
.chart-container-large {
    height: 400px;
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.heatmap-container {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    overflow-x: auto;
}

.heatmap-header {
    display: flex;
}

.heatmap-row {
    display: flex;
}

.heatmap-cell {
    width: 80px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #eee;
    font-size: 0.8rem;
    color: #444;
}

.header-cell {
    background: #f8f9fa;
    font-weight: bold;
    color: #666;
}

.row-header {
    background: #f8f9fa;
    font-weight: bold;
    min-width: 80px;
}
</style>
