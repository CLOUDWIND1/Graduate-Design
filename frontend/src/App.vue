<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <!-- 导航栏 - 登录/注册页面不显示 -->
      <el-header v-if="showNav" class="app-header glass">
        <div class="header-inner">
          <div class="header-left">
            <router-link to="/" class="logo">
              <span class="logo-icon">✨</span>
              <span class="text-gradient">推荐系统</span>
            </router-link>
            
            <nav class="nav-links">
              <router-link to="/" class="nav-item" :class="{ active: route.path === '/' }">
                首页
              </router-link>
              <router-link to="/recommendations" class="nav-item" :class="{ active: route.path === '/recommendations' }">
                推荐
              </router-link>
              <router-link to="/rewards" class="nav-item" :class="{ active: route.path === '/rewards' }">
                我的奖励
              </router-link>
              
              <!-- Admin Menu Group -->
              <div v-if="isAdmin" class="nav-group">
                <span class="nav-group-label">管理中心</span>
                <router-link to="/admin" class="nav-item" :class="{ active: route.path === '/admin' }">
                  看板
                </router-link>
                <router-link to="/admin/activities" class="nav-item" :class="{ active: route.path === '/admin/activities' }">
                  活动
                </router-link>
                <router-link to="/admin/config" class="nav-item" :class="{ active: route.path === '/admin/config' }">
                  配置
                </router-link>
              </div>
            </nav>
          </div>
          
          <div class="header-right">
            <el-dropdown @command="handleCommand" trigger="click">
              <div class="user-profile">
                <el-avatar :size="36" class="user-avatar" :style="{ backgroundColor: 'var(--primary-color)' }">
                  {{ userInfo && userInfo.username ? userInfo.username.charAt(0).toUpperCase() : 'U' }}
                </el-avatar>
                <span class="username">{{ userInfo && userInfo.username ? userInfo.username : 'User' }}</span>
                <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu class="custom-dropdown">
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="rewards">
                    <el-icon><Trophy /></el-icon>我的奖励
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout" class="danger-item">
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="slide-up" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </el-main>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { ArrowDown, User, Trophy, SwitchButton } from '@element-plus/icons-vue'
import { useUserStore } from '@/store'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const showNav = computed(() => {
  return !['/login', '/register'].includes(route.path)
})

const userInfo = computed(() => userStore.userInfo)
const isAdmin = computed(() => userStore.isAdmin)

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'rewards':
      router.push('/rewards')
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = async () => {
  await userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-color);
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0;
  height: var(--header-height);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 48px;
}

.logo {
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 700;
}

.logo-icon {
  font-size: 24px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-item {
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-regular);
  position: relative;
  transition: color 0.2s;
  padding: 8px 0;
}

.nav-item:hover {
  color: var(--primary-color);
}

.nav-item.active {
  color: var(--primary-color);
  font-weight: 600;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--primary-color);
  border-radius: 1px;
}

.nav-group {
  display: flex;
  align-items: center;
  gap: 24px;
  padding-left: 24px;
  border-left: 1px solid #E5E7EB;
}

.nav-group-label {
  font-size: 12px;
  text-transform: uppercase;
  color: var(--text-secondary);
  font-weight: 600;
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 99px;
  transition: background-color 0.2s;
  border: 1px solid transparent;
}

.user-profile:hover {
  background-color: #F3F4F6;
  border-color: #E5E7EB;
}

.user-avatar {
  color: white;
  font-weight: 600;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.dropdown-icon {
  font-size: 12px;
  color: var(--text-secondary);
}

.app-main {
  flex: 1;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* Custom Dropdown Styles */
:global(.custom-dropdown) {
  border-radius: 12px !important;
  padding: 8px !important;
  box-shadow: var(--shadow-lg) !important;
  border: none !important;
}

:global(.el-dropdown-menu__item) {
  border-radius: 6px;
  margin: 2px 0;
}

:global(.danger-item) {
  color: var(--danger-color) !important;
}

:global(.danger-item:hover) {
  background-color: #FEF2F2 !important;
}

@media (max-width: 1024px) {
  .header-left {
    gap: 24px;
  }
  .nav-group {
    display: none;
  }
}
</style>