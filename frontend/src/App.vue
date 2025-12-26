<script setup>
import { onMounted, ref } from 'vue'

// Components
import TheHeader from './components/TheHeader.vue'
import Dashboard from './components/Dashboard.vue'
import JobSearch from './components/JobSearch.vue'
import CrawlerControl from './components/CrawlerControl.vue'
import SalaryPredictor from './components/SalaryPredictor.vue'

// Composables
import { useJobs, industries } from './composables/useJobs'
import { useStats } from './composables/useStats'
import { useCrawler, prefectures } from './composables/useCrawler'
import { usePrediction } from './composables/usePrediction'

// State
const activeTab = ref('dashboard')

// Instantiate Composables
const {
    jobs,
    filterType,
    filterIndustry,
    filterLocation,
    searchKeyword,
    wageMin,
    wageMax,
    fetchJobs,
    searchJobs
} = useJobs()

const {
    stats,
    industryStats,
    hotIndustries,
    industryRanking,
    locationStats,
    salaryTrend,
    industryComparison,
    heatmapData,
    loading,
    fetchAllStats
} = useStats()

// Refresh function for crawler callback
async function refreshAllData() {
    await Promise.all([
        fetchJobs(),
        fetchAllStats()
    ])
}

const {
    crawlerRunning,
    selectedPrefecture,
    maxPages,
    forceMode,
    crawlKeyword,
    indeedKeyword,
    indeedLocation,
    indeedPages,
    runCrawler,
    runIndeedCrawler
} = useCrawler(refreshAllData)

const {
    mlIndustry,
    mlLocation,
    mlWageType,
    mlPrediction,
    mlTraining,
    trainModel,
    predictSalary
} = usePrediction()

// Lifecycle
onMounted(async () => {
    await refreshAllData()
})
</script>

<template>
    <div class="container">
        <TheHeader :activeTab="activeTab" @update:activeTab="activeTab = $event" />

        <!-- ダッシュボードタブ -->
        <div v-if="activeTab === 'dashboard'" class="tab-content">
            <Dashboard :loading="loading" :stats="stats" :hotIndustries="hotIndustries" :industryStats="industryStats"
                :industryRanking="industryRanking" :salaryTrend="salaryTrend" :industryComparison="industryComparison"
                :heatmapData="heatmapData" :locationStats="locationStats" :industries="industries" />
        </div>

        <!-- クローラータブ -->
        <div v-if="activeTab === 'crawler'" class="tab-content">
            <CrawlerControl :crawlerRunning="crawlerRunning" :prefectures="prefectures" :forceMode="forceMode"
                @update:forceMode="forceMode = $event" :selectedPrefecture="selectedPrefecture"
                @update:selectedPrefecture="selectedPrefecture = $event" :indeedKeyword="indeedKeyword"
                @update:indeedKeyword="indeedKeyword = $event" :indeedLocation="indeedLocation"
                @update:indeedLocation="indeedLocation = $event" :indeedPages="indeedPages"
                @update:indeedPages="indeedPages = $event" @runHellowork="runCrawler" @runIndeed="runIndeedCrawler" />
        </div>

        <!-- 検索タブ -->
        <div v-if="activeTab === 'search'" class="tab-content">
            <JobSearch :jobs="jobs" :industries="industries" :searchKeyword="searchKeyword"
                @update:searchKeyword="searchKeyword = $event" :wageMin="wageMin" @update:wageMin="wageMin = $event"
                :wageMax="wageMax" @update:wageMax="wageMax = $event" :filterIndustry="filterIndustry"
                @update:filterIndustry="filterIndustry = $event" :filterLocation="filterLocation"
                @update:filterLocation="filterLocation = $event" @search="searchJobs" />
        </div>

        <!-- ML予測タブ -->
        <div v-if="activeTab === 'predict'" class="tab-content">
            <SalaryPredictor :prediction="mlPrediction" :training="mlTraining" :industries="industries"
                :prefectures="prefectures" :mlIndustry="mlIndustry" @update:mlIndustry="mlIndustry = $event"
                :mlLocation="mlLocation" @update:mlLocation="mlLocation = $event" :mlWageType="mlWageType"
                @update:mlWageType="mlWageType = $event" @train="trainModel" @predict="predictSalary" />
        </div>
    </div>
</template>

<style scoped>
* {
    box-sizing: border-box;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    color: #2c3e50;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    min-height: 100vh;
}

.tab-content {
    background: white;
    border-radius: 0 12px 12px 12px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
</style>