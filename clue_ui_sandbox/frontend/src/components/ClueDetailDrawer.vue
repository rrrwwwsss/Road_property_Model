<template>
  <el-drawer
    v-model="visibleProxy"
    size="60%"
    class="clue-drawer"
    custom-class="clue-drawer"
  >
    <template #header>
      <div class="drawer-header-wrap">
        <div class="drawer-title">线索详情</div>
        <el-button
          v-if="canEdit"
          type="primary"
          size="default"
          class="submit-btn"
          :loading="editing"
          @click="emit('edit', detail)"
        >
          提交
        </el-button>
      </div>
    </template>

    <div class="clue-drawer-content">
      <el-descriptions :column="1" border :label-width="160" class="detail-desc">
        <el-descriptions-item label="工单编号">
          {{ detail?.raw?.["工单编号"] || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="违法类型">
          {{ detail?.raw?.["违法类型"] || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="发生地点">
          {{ detail?.raw?.["发生地点"] || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="发生时间">
          {{ formatOccurTime(detail?.raw?.["发生时间"]) }}
        </el-descriptions-item>
        <el-descriptions-item label="所属支队">
          {{ detail?.raw?.["所属支队"] || detail?.raw?.["UNIT_CODE"] || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="图片">
          <el-image
            v-if="detail?.image_url"
            :src="detail.image_url"
            fit="contain"
            class="detail-image"
            :preview-src-list="[detail.image_url]"
          />
          <span v-else>无图片</span>
        </el-descriptions-item>
        <el-descriptions-item label="模型输出">
          <pre class="model-output">{{ detail?.model_output || "无" }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </el-drawer>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  visible: { type: Boolean, default: false },
  detail: { type: Object, default: null },
  canEdit: { type: Boolean, default: false },
  editing: { type: Boolean, default: false }
});
const emit = defineEmits(["update:visible", "edit"]);

const visibleProxy = computed({
  get: () => props.visible,
  set: (v) => emit("update:visible", v)
});

function formatOccurTime(val) {
  if (!val) return "-";
  const text = String(val).trim();

  const m = text.match(/^(\d{4})(\d{2})(\d{2})[_ ]?(\d{2})(\d{2})(\d{2})$/);
  if (m) {
    return `${Number(m[1])}/${Number(m[2])}/${Number(m[3])} ${m[4]}:${m[5]}:${m[6]}`;
  }

  const d = new Date(text);
  if (!Number.isNaN(d.getTime())) {
    const y = d.getFullYear();
    const mon = d.getMonth() + 1;
    const day = d.getDate();
    const hh = String(d.getHours()).padStart(2, "0");
    const mm = String(d.getMinutes()).padStart(2, "0");
    const ss = String(d.getSeconds()).padStart(2, "0");
    return `${y}/${mon}/${day} ${hh}:${mm}:${ss}`;
  }

  return text;
}
</script>

<style>
.clue-drawer .el-drawer__header {
  margin-bottom: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #d6e3f4;
  background: linear-gradient(90deg, #eaf2fb, #f3f7fd);
  color: #123f76;
  font-weight: 700;
}

.drawer-header-wrap {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drawer-title {
  font-size: 16px;
  font-weight: 700;
  color: #123f76;
}

.submit-btn {
  min-width: 96px;
  height: 38px;
  font-size: 15px;
  font-weight: 700;
  box-shadow: 0 6px 14px rgba(37, 99, 235, 0.24);
}

.clue-drawer .el-drawer__body {
  background: #ffffff;
}

.clue-drawer-content {
  background: #f6f9fe;
  border: 1px solid #d6e3f4;
  border-radius: 8px;
  padding: 12px;
}

.clue-drawer-content .detail-image {
  width: 100%;
  max-height: 360px;
  border: 1px solid #dbe5f1;
  border-radius: 4px;
}

.clue-drawer-content .model-output {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", "STSong", serif;
  font-size: 15px;
  line-height: 1.75;
  color: #243447;
}

.clue-drawer-content .detail-desc :deep(.el-descriptions__table) {
  border: 2px solid #b8cae3;
}

.clue-drawer-content .detail-desc :deep(.el-descriptions__cell) {
  border: 2px solid #b8cae3 !important;
}

.clue-drawer-content .detail-desc :deep(.el-descriptions__label) {
  width: 160px;
  white-space: nowrap;
  font-weight: 700;
  color: #183b67;
}
</style>
