<template>
  <el-drawer
    v-model="visibleProxy"
    title="线索详情"
    size="60%"
    class="clue-drawer"
    custom-class="clue-drawer"
  >
    <div class="clue-drawer-content">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="工单编号">
          {{ detail?.raw?.["工单编号"] || "-" }}
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
  detail: { type: Object, default: null }
});
const emit = defineEmits(["update:visible"]);

const visibleProxy = computed({
  get: () => props.visible,
  set: (v) => emit("update:visible", v)
});
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
</style>
