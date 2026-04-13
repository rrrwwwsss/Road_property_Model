<template>
  <div class="page-card">
    <div class="toolbar">
      <el-button :loading="loading" @click="loadClues">刷新</el-button>
      <el-switch v-model="onlyUncommitted" active-text="只看未提交" @change="onFilterChange" />
      <el-input
        v-model="keyword"
        placeholder="搜索工单编号/违法类型/发生地点"
        clearable
        style="width: 320px"
        @keyup.enter="onFilterChange"
      />
      <el-button @click="onFilterChange">搜索</el-button>
    </div>

    <el-table :data="rows" border stripe v-loading="loading">
      <el-table-column
        v-for="col in visibleColumns"
        :key="col"
        :prop="col"
        :label="colLabel(col)"
        :fixed="col === 'id' ? 'left' : false"
        :width="col === 'id' ? 80 : undefined"
        min-width="130"
        show-overflow-tooltip
      >
        <template v-if="col === 'is_committed'" #default="{ row }">
          <el-tag :type="Number(row.is_committed) === 1 ? 'success' : 'warning'">
            {{ Number(row.is_committed) === 1 ? "已提交" : "未提交" }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" fixed="right" width="110">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="loadClues"
        @size-change="onSizeChange"
      />
    </div>

    <ClueDetailDrawer
      v-model:visible="drawerVisible"
      :detail="detail"
      :can-edit="Number(detail?.raw?.is_committed || 0) !== 1"
      :editing="committingId === detail?.id"
      @edit="onDrawerEdit"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { commitClue, fetchClueDetail, fetchClues } from "../api/clues";
import ClueDetailDrawer from "../components/ClueDetailDrawer.vue";

const loading = ref(false);
const rows = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);
const keyword = ref("");
const onlyUncommitted = ref(false);
const drawerVisible = ref(false);
const detail = ref(null);
const committingId = ref(null);

const visibleColumns = computed(() =>
  rows.value[0] ? Object.keys(rows.value[0]).filter((x) => x !== "工单编号") : []
);

const labelMap = {
  id: "ID",
  UNIT_CODE: "辖区编码",
  MEASURE: "职能编码",
  is_committed: "是否提交"
};

function colLabel(col) {
  return labelMap[col] || col;
}

async function loadClues() {
  loading.value = true;
  try {
    const offset = (currentPage.value - 1) * pageSize.value;
    const data = await fetchClues({
      limit: pageSize.value,
      offset,
      only_uncommitted: onlyUncommitted.value,
      keyword: keyword.value
    });
    rows.value = data.items || [];
    total.value = Number(data.total || 0);
  } catch (err) {
    ElMessage.error(err?.response?.data?.detail || err.message || "加载失败");
  } finally {
    loading.value = false;
  }
}

async function onFilterChange() {
  currentPage.value = 1;
  await loadClues();
}

async function onSizeChange(size) {
  pageSize.value = size;
  currentPage.value = 1;
  await loadClues();
}

async function openDetail(row) {
  try {
    detail.value = await fetchClueDetail(row.id);
    drawerVisible.value = true;
  } catch (err) {
    ElMessage.error(err?.response?.data?.detail || err.message || "详情加载失败");
  }
}

async function doCommit(id, workOrderNo) {
  try {
    await ElMessageBox.confirm(
      `确认提交该线索吗？\n工单编号：${workOrderNo || id}`,
      "提交确认",
      {
        confirmButtonText: "确认提交",
        cancelButtonText: "取消",
        type: "warning"
      }
    );
  } catch (_) {
    return;
  }

  committingId.value = id;
  try {
    await commitClue(id);
    ElMessage.success("提交成功");
    await loadClues();
    if (drawerVisible.value) {
      detail.value = await fetchClueDetail(id);
    }
  } catch (err) {
    ElMessage.error(err?.response?.data?.detail || err.message || "提交失败");
  } finally {
    committingId.value = null;
  }
}

async function onDrawerEdit(payload) {
  const id = payload?.id;
  const workOrderNo = payload?.raw?.["工单编号"];
  if (!id) return;
  await doCommit(id, workOrderNo);
}

onMounted(loadClues);
</script>

<style scoped>
.toolbar { display: flex; gap: 12px; align-items: center; margin-bottom: 12px; }
.pager-wrap { margin-top: 12px; display: flex; justify-content: flex-end; }
</style>
