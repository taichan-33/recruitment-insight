import { ref } from "vue";

export const prefectures = [
  "北海道",
  "青森県",
  "岩手県",
  "宮城県",
  "秋田県",
  "山形県",
  "福島県",
  "茨城県",
  "栃木県",
  "群馬県",
  "埼玉県",
  "千葉県",
  "東京都",
  "神奈川県",
  "新潟県",
  "富山県",
  "石川県",
  "福井県",
  "山梨県",
  "長野県",
  "岐阜県",
  "静岡県",
  "愛知県",
  "三重県",
  "滋賀県",
  "京都府",
  "大阪府",
  "兵庫県",
  "奈良県",
  "和歌山県",
  "鳥取県",
  "島根県",
  "岡山県",
  "広島県",
  "山口県",
  "徳島県",
  "香川県",
  "愛媛県",
  "高知県",
  "福岡県",
  "佐賀県",
  "長崎県",
  "熊本県",
  "大分県",
  "宮崎県",
  "鹿児島県",
  "沖縄県",
];

export function useCrawler(onCrawlComplete) {
  const crawlerRunning = ref(false);
  const selectedPrefecture = ref("北海道");
  const maxPages = ref(10);
  const forceMode = ref(false);
  const crawlKeyword = ref("");

  // Indeed search params
  const indeedKeyword = ref("");
  const indeedLocation = ref("東京都");
  const indeedPages = ref(3);

  async function checkCrawlerStatus() {
    try {
      const res = await fetch("http://127.0.0.1:5000/api/crawl/status");
      const data = await res.json();
      if (data.is_running) {
        crawlerRunning.value = true;
        setTimeout(checkCrawlerStatus, 2000);
      } else {
        if (crawlerRunning.value) {
          // Only alert/callback if it WAS running
          if (data.last_result && data.last_result.success) {
            alert(
              `🎉 求人収集が完了しました！\n収集件数: ${data.last_result.count}件`
            );
          } else if (data.last_error) {
            alert(`⚠️ エラーが発生しました: ${data.last_error}`);
          } else {
            alert("通知: 求人収集が終了しました。");
          }
          if (onCrawlComplete) onCrawlComplete();
        }
        crawlerRunning.value = false;
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function runCrawler() {
    if (crawlerRunning.value) return;
    crawlerRunning.value = true;
    try {
      const res = await fetch("http://127.0.0.1:5000/api/crawl/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prefectures: [selectedPrefecture.value],
          max_pages: maxPages.value,
          force: forceMode.value,
          keyword: crawlKeyword.value,
        }),
      });
      const data = await res.json();
      alert(data.message);
      checkCrawlerStatus();
    } catch (e) {
      console.error("クローラー実行エラー:", e);
      crawlerRunning.value = false;
    }
  }

  async function runIndeedCrawler() {
    if (crawlerRunning.value) return;
    crawlerRunning.value = true;
    try {
      const res = await fetch("http://127.0.0.1:5000/api/crawl/indeed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          keyword: indeedKeyword.value,
          location: indeedLocation.value,
          max_pages: indeedPages.value,
        }),
      });
      const data = await res.json();
      alert(data.message);
      checkCrawlerStatus();
    } catch (e) {
      console.error("Indeed検索エラー:", e);
      crawlerRunning.value = false;
    }
  }

  return {
    crawlerRunning,
    selectedPrefecture,
    maxPages,
    forceMode,
    crawlKeyword,
    indeedKeyword,
    indeedLocation,
    indeedPages,
    prefectures,
    runCrawler,
    runIndeedCrawler,
    checkCrawlerStatus,
  };
}
