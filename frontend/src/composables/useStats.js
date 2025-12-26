import { ref } from "vue";

export function useStats() {
  const stats = ref({});
  const industryStats = ref([]);
  const hotIndustries = ref([]);
  const industryRanking = ref([]);
  const locationStats = ref([]);
  const salaryTrend = ref([]);
  const industryComparison = ref([]);
  const heatmapData = ref({ prefectures: [], industries: [], data: [] });
  const loading = ref(true);

  async function fetchStats() {
    try {
      const res = await fetch("http://127.0.0.1:5000/api/stats");
      stats.value = await res.json();
    } catch (e) {
      console.error("統計取得エラー:", e);
    }
  }

  async function fetchIndustryStats() {
    try {
      const res = await fetch("http://127.0.0.1:5000/api/analysis/industry");
      industryStats.value = await res.json();
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchHotIndustries() {
    try {
      const res = await fetch("http://127.0.0.1:5000/api/analysis/hot");
      hotIndustries.value = await res.json();
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchIndustryRanking() {
    try {
      const res = await fetch("http://127.0.0.1:5000/api/analysis/ranking");
      industryRanking.value = await res.json();
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchLocationStats() {
    try {
      const res = await fetch("http://127.0.0.1:5000/api/analysis/location");
      locationStats.value = await res.json();
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchSalaryTrend() {
    try {
      const res = await fetch(
        "http://127.0.0.1:5000/api/analysis/salary-trend"
      );
      salaryTrend.value = await res.json();
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchIndustryComparison() {
    try {
      const res = await fetch(
        "http://127.0.0.1:5000/api/analysis/industry-comparison"
      );
      industryComparison.value = await res.json();
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchHeatmapData() {
    try {
      const res = await fetch("http://127.0.0.1:5000/api/analysis/heatmap");
      heatmapData.value = await res.json();
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchAllStats() {
    loading.value = true;
    await Promise.all([
      fetchStats(),
      fetchIndustryStats(),
      fetchHotIndustries(),
      fetchIndustryRanking(),
      fetchLocationStats(),
      fetchSalaryTrend(),
      fetchIndustryComparison(),
      fetchHeatmapData(),
    ]);
    loading.value = false;
  }

  return {
    stats,
    industryStats,
    hotIndustries,
    industryRanking,
    locationStats,
    salaryTrend,
    industryComparison,
    heatmapData,
    loading,
    fetchAllStats,
  };
}
