<template>
  <div class="page-card">
    <div class="dashboard-title">首页概览</div>

    <el-row :gutter="12" class="cards">
      <el-col :span="6"><el-card><div class="k">线索总数</div><div class="v">{{ summary.total }}</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="k">未提交数量</div><div class="v warn">{{ summary.uncommitted }}</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="k">已提交数量</div><div class="v ok">{{ summary.committed }}</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="k">已提交率</div><div class="v">{{ summary.committed_rate }}%</div></el-card></el-col>
    </el-row>

    <el-card class="chart-card">
      <template #header><div class="section-title">违法类型趋势图</div></template>
      <div ref="chartRef" class="trend-chart"></div>
    </el-card>

    <el-tabs v-model="tab" class="table-tabs">
      <el-tab-pane label="按违法类型统计" name="violation" />
      <el-tab-pane label="按发生地点统计" name="location" />
    </el-tabs>

    <el-table :data="tableRows" border stripe table-layout="fixed">
      <el-table-column :label="tab === 'violation' ? '违法类型' : '发生地点'" prop="group_key" width="260" show-overflow-tooltip />
      <el-table-column label="总数" width="140">
        <template #default="{ row }"><span class="c-total">{{ row.total }}</span></template>
      </el-table-column>
      <el-table-column label="未提交数" width="140">
        <template #default="{ row }"><span class="c-uncommit">{{ row.uncommitted }}</span></template>
      </el-table-column>
      <el-table-column label="已提交数" width="140">
        <template #default="{ row }"><span class="c-commit">{{ row.committed }}</span></template>
      </el-table-column>
      <el-table-column label="已提交率(%)" width="140">
        <template #default="{ row }"><span class="c-rate">{{ row.committed_rate }}</span></template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as echarts from "echarts";
import {
  fetchStatsByMeasure,
  fetchStatsByUnit,
  fetchStatsSummary,
  fetchTrendByViolation
} from "../api/clues";

const tab = ref("violation");
const summary = ref({ total: 0, uncommitted: 0, committed: 0, committed_rate: 0.0 });
const byViolation = ref([]);
const byLocation = ref([]);
const trend = ref({ dates: [], series: [] });
const tableRows = computed(() => (tab.value === "violation" ? byViolation.value : byLocation.value));

const chartRef = ref(null);
let chart = null;

function renderChart() {
  if (!chartRef.value) return;
  if (!chart) chart = echarts.init(chartRef.value);
  const palette = ["#1d4ed8", "#0ea5e9", "#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#6366f1"];
  chart.setOption({
    color: palette,
    tooltip: { trigger: "axis" },
    legend: { top: 0 },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: { type: "category", data: trend.value.dates, boundaryGap: false },
    yAxis: { type: "value", name: "行为数" },
    series: trend.value.series.map((s) => ({
      name: s.name,
      type: "line",
      smooth: true,
      symbol: "circle",
      symbolSize: 6,
      lineStyle: { width: 2.5 },
      areaStyle: { opacity: 0.08 },
      data: s.data
    }))
  });
}

async function loadSummary() {
  summary.value = await fetchStatsSummary();
}

async function loadTables() {
  byViolation.value = await fetchStatsByUnit();
  byLocation.value = await fetchStatsByMeasure();
}

async function loadTrend() {
  trend.value = await fetchTrendByViolation();
  await nextTick();
  renderChart();
}

watch(tab, loadTables);
onMounted(async () => {
  await loadSummary();
  await loadTables();
  await loadTrend();
  window.addEventListener("resize", renderChart);
});
onBeforeUnmount(() => {
  window.removeEventListener("resize", renderChart);
  if (chart) chart.dispose();
});
</script>

<style scoped>
.dashboard-title { font-size: 22px; font-weight: 700; color: #0b3a73; margin-bottom: 10px; }
.cards { margin-bottom: 12px; }
.k { color: #64748b; font-size: 13px; }
.v { margin-top: 6px; font-size: 30px; font-weight: 700; color: #1e3a8a; }
.v.warn { color: #d97706; }
.v.ok { color: #059669; }
.chart-card { margin-bottom: 12px; }
.section-title { font-weight: 600; color: #0f2f56; }
.trend-chart { width: 100%; height: 340px; }
.table-tabs { margin-bottom: 8px; }
.c-total { color: #1d4ed8; font-weight: 600; }
.c-uncommit { color: #d97706; font-weight: 600; }
.c-commit { color: #059669; font-weight: 600; }
.c-rate { color: #475569; font-weight: 600; }
</style>

