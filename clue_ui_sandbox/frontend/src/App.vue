<template>
  <el-container class="layout-root">
    <el-header class="topbar">
      <div class="system-title">公路违法行为识别系统</div>
      <el-button class="collapse-btn" @click="toggleMenu">
        {{ isCollapsed ? "展开菜单" : "收起菜单" }}
      </el-button>
    </el-header>
    <el-container>
      <el-aside :width="isCollapsed ? '72px' : '220px'" class="sidebar">
        <el-menu
          :default-active="activePath"
          :collapse="isCollapsed"
          class="menu"
          @select="onSelect"
        >
          <el-menu-item index="/">
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/clues">
            <span>线索列表</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="main-panel">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const activePath = computed(() => route.path);
const isCollapsed = ref(false);

function onSelect(path) {
  if (path !== route.path) router.push(path);
}

function toggleMenu() {
  isCollapsed.value = !isCollapsed.value;
}
</script>

