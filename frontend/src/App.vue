<template>
  <router-view v-if="['Onboarding', 'Login'].includes($route.name)" />
  <Layout v-else-if="$session.isLoggedIn">
    <router-view />
  </Layout>
  <Dialogs />
  <Toasts />
</template>

<script setup>
import { computed, defineAsyncComponent } from 'vue'
import { Dialogs } from '@/utils/dialogs'
import { Toasts } from 'frappe-ui'
import { users } from '@/data/users'
import { useScreenSize } from './utils/composables'
import { initMessageFireBase } from './utils/messaging_firebase'

const screenSize = useScreenSize()
initMessageFireBase()
const MobileLayout = defineAsyncComponent(() =>
  import('./components/MobileLayout.vue')
)
const DesktopLayout = defineAsyncComponent(() =>
  import('./components/DesktopLayout.vue')
)
const Layout = computed(() => {
  if (screenSize.width < 640) {
    return MobileLayout
  } else {
    return DesktopLayout
  }
})

users.fetch()
</script>
