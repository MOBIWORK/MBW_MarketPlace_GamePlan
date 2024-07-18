<template>
  <NotificationsList style="height: 99%;"></NotificationsList>
</template>
<script>

import NotificationsList from '@/components/NotificationsList.vue'

export default {
  name: 'Notifications',
  pageMeta() {
    return {
      title: 'Notifications',
      emoji: '🔔',
    }
  }
}
</script>
