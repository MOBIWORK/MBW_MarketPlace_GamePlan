<template>
  <div v-if="visible" ref="target" class="absolute z-20 h-screen bg-white transition-all duration-300 ease-in-out"
    :style="{
      'box-shadow': '8px 0px 8px rgba(0, 0, 0, 0.1)',
      'max-width': '450px',
      'min-width': '430px',
      left: 'calc(100% + 1px)',
    }">
    <NotificationsList :parent_panel="'sidebar'"></NotificationsList>
  </div>
</template>

<script>
import { Tooltip, TabButtons } from 'frappe-ui'
import { onClickOutside } from '@vueuse/core'
import { ref } from 'vue'
import NotificationsList from '@/components/NotificationsList.vue'

export default {
  name: 'NotificationsSidebar',
  props: ["visible"],
  emits: ['changeVisible'],
  data() {
    return {
      activeTab: 'Unread'
    }
  },
  components: { TabButtons, Tooltip, NotificationsList },
  resources: {
    unreadNotifications() {
      if (this.activeTab !== 'Unread') return
      return {
        type: 'list',
        cache: 'Unread Notifications',
        doctype: 'GP Notification',
        filters: { to_user: this.$user().name, read: 0 },
        fields: [
          'name',
          'from_user',
          'message',
          'read',
          'type',
          'creation',
          'comment',
          'discussion',
          'task',
          'project',
          'team',
        ],
        orderBy: 'creation desc',
        auto: true,
      }
    },
    readNotifications() {
      if (this.activeTab !== 'Read') return
      return {
        type: 'list',
        cache: 'Read Notifications',
        doctype: 'GP Notification',
        filters: { to_user: this.$user().name, read: 1 },
        fields: [
          'name',
          'from_user',
          'message',
          'read',
          'type',
          'creation',
          'comment',
          'discussion',
          'task',
          'project',
          'team',
        ],
        orderBy: 'creation desc',
        auto: true,
      }
    },
    markAllAsRead() {
      return {
        url: 'gameplan.api.mark_all_notifications_as_read',
        onSuccess() {
          this.$getResource('Unread Notifications Count')?.reload()
          this.$resources.unreadNotifications.reload()
        },
      }
    },
  },
  computed: {
    notifications() {
      return this.activeTab === 'Unread'
        ? this.$resources.unreadNotifications.data
        : this.$resources.readNotifications.data
    },
  },
  methods: {
    markAsRead(name) {
      this.$resources.unreadNotifications.setValue.submit(
        {
          name,
          read: 1,
        },
        {
          onSuccess: () => {
            this.$getResource('Unread Notifications Count')?.reload()
          },
        }
      )
    },
    toggleNotificationPanel() {
      this.$emit('changeVisible', false)
    }
  },
  mounted() {
    this.$getResource('Unread Notifications Count')?.reload()
  },
  setup(props, { emit }) {
    const target = ref(null)
    const closePanel = () => {
      emit('changeVisible', false)
    }
    onClickOutside(target, closePanel, { ignore: ['#notifications-btn'] })
    return { target }
  }
}
</script>

<style scoped>
.btn-filter-notify {
  background-color: #f4f4f4 !important;
  color: #444 !important;
  border-color: #ddd !important;
  font-size: 13px;
  margin-left: 5px;
  border-radius: 15px;
  margin: 10px 5px;
  padding: 5px 10px;
  cursor: pointer;
}

.btn-filter-notify-active {
  background-color: #baebe1 !important;
  color: #1876f2 !important;
  border-color: #baebe1 !important;
  box-shadow: none !important;
  font-weight: 500;
  outline: none !important;
}
</style>