const yearPicker = document.getElementById("yearPicker");
const monthPicker = document.getElementById("monthPicker");
const queryBtn = document.getElementById("queryBtn");
const exportBtn = document.getElementById("exportBtn");
const reportTable = document.getElementById("reportTable");
const message = document.getElementById("message");

const toggleConfigBtn = document.getElementById("toggleConfigBtn");
const configPanel = document.getElementById("configPanel");
const configText = document.getElementById("configText");
const reloadConfigBtn = document.getElementById("reloadConfigBtn");
const saveConfigBtn = document.getElementById("saveConfigBtn");

function setMessage(text, isError = true) {
  message.style.color = isError ? "#9a2c2c" : "#145a32";
  message.textContent = text;
}

function getCurrentYearMonth() {
  const now = new Date();
  const year = Number(yearPicker.value || now.getFullYear());
  const month = Number(monthPicker.value || now.getMonth() + 1);
  return { year, month };
}

function renderTable(data) {
  const headers = ["站名", ...data.day_headers, "应到报", "实到报", "到报率(%)"];

  let html = "<thead><tr>";
  headers.forEach((head) => {
    html += `<th>${head}</th>`;
  });
  html += "</tr></thead><tbody>";

  data.rows.forEach((row) => {
    html += "<tr>";
    html += `<td>${row.station_name}</td>`;
    row.daily_actual.forEach((value) => {
      html += `<td>${value}</td>`;
    });
    html += `<td>${row.expected_total}</td>`;
    html += `<td>${row.actual_total}</td>`;
    html += `<td>${row.rate}</td>`;
    html += "</tr>";
  });

  html += "</tbody>";
  reportTable.innerHTML = html;
}

async function fetchReport() {
  const { year, month } = getCurrentYearMonth();
  setMessage("正在加载...", false);
  try {
    const response = await fetch(`/api/report/monthly?year=${year}&month=${month}`);
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "查询失败");
    }
    const data = await response.json();
    renderTable(data);
    setMessage(`加载完成：${year}年${month}月`, false);
  } catch (error) {
    setMessage(error.message || "查询失败");
  }
}

function exportReport() {
  const { year, month } = getCurrentYearMonth();
  window.location.href = `/api/report/monthly/export?year=${year}&month=${month}`;
}

async function loadConfig() {
  try {
    const response = await fetch("/api/config");
    if (!response.ok) {
      throw new Error("加载配置失败");
    }
    const config = await response.json();
    configText.value = JSON.stringify(config, null, 2);
  } catch (error) {
    setMessage(error.message || "加载配置失败");
  }
}

async function saveConfig() {
  let payload;
  try {
    payload = JSON.parse(configText.value);
  } catch (error) {
    setMessage("JSON 格式错误，请修正后再保存");
    return;
  }

  try {
    const response = await fetch("/api/config", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "保存失败");
    }
    const saved = await response.json();
    configText.value = JSON.stringify(saved, null, 2);
    setMessage("配置已保存", false);
  } catch (error) {
    setMessage(error.message || "保存失败");
  }
}

function initYearMonthPickers() {
  const now = new Date();
  const currentYear = now.getFullYear();
  const startYear = currentYear - 15;
  const endYear = currentYear + 5;

  let yearOptions = "";
  for (let year = startYear; year <= endYear; year += 1) {
    yearOptions += `<option value="${year}">${year}</option>`;
  }
  yearPicker.innerHTML = yearOptions;

  let monthOptions = "";
  for (let month = 1; month <= 12; month += 1) {
    monthOptions += `<option value="${month}">${month}</option>`;
  }
  monthPicker.innerHTML = monthOptions;

  yearPicker.value = String(currentYear);
  monthPicker.value = String(now.getMonth() + 1);
}

queryBtn.addEventListener("click", fetchReport);
exportBtn.addEventListener("click", exportReport);

reloadConfigBtn.addEventListener("click", loadConfig);
saveConfigBtn.addEventListener("click", saveConfig);

toggleConfigBtn.addEventListener("click", async () => {
  configPanel.classList.toggle("hidden");
  if (!configPanel.classList.contains("hidden")) {
    await loadConfig();
  }
});

initYearMonthPickers();
fetchReport();
