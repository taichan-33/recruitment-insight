import { ref, watch } from "vue";

export const industries = [
  "IT・エンジニア",
  "医療・介護",
  "営業・事務",
  "サービス・販売",
  "製造・建設",
  "その他",
];

export function useJobs() {
  const jobs = ref([]);
  const filterType = ref("all");
  const filterIndustry = ref("all");
  const filterLocation = ref("");
  const searchKeyword = ref("");
  const wageMin = ref("");
  const wageMax = ref("");

  async function fetchJobs() {
    try {
      let url = "http://127.0.0.1:5000/api/jobs";
      const params = new URLSearchParams();
      if (filterType.value !== "all")
        params.append("wage_type", filterType.value);
      if (params.toString()) url += `?${params.toString()}`;

      const res = await fetch(url);
      jobs.value = await res.json();
    } catch (e) {
      console.error("求人取得エラー:", e);
      jobs.value = [];
    }
  }

  async function searchJobs() {
    try {
      const params = new URLSearchParams();
      if (searchKeyword.value) params.append("keyword", searchKeyword.value);
      if (wageMin.value) params.append("wage_min", wageMin.value);
      if (wageMax.value) params.append("wage_max", wageMax.value);
      if (filterIndustry.value !== "all")
        params.append("industry", filterIndustry.value);
      if (filterLocation.value) params.append("location", filterLocation.value);

      const res = await fetch(
        `http://127.0.0.1:5000/api/search?${params.toString()}`
      );
      jobs.value = await res.json();
    } catch (e) {
      console.error("検索エラー:", e);
    }
  }

  // Watch for filter changes to trigger search or fetch
  watch([filterType, filterIndustry, filterLocation], () => {
    if (
      searchKeyword.value ||
      wageMin.value ||
      wageMax.value ||
      filterIndustry.value !== "all" ||
      filterLocation.value
    ) {
      searchJobs();
    } else {
      fetchJobs();
    }
  });

  return {
    jobs,
    filterType,
    filterIndustry,
    filterLocation,
    searchKeyword,
    wageMin,
    wageMax,
    industries,
    fetchJobs,
    searchJobs,
  };
}
