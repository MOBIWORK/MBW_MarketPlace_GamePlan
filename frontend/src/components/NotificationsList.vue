<template>
    <div v-if="visible_panel" ref="target"
      class="absolute z-20 h-screen bg-white transition-all duration-300 ease-in-out" :style="{
        'box-shadow': '8px 0px 8px rgba(0, 0, 0, 0.1)',
        'max-width': '350px',
        'min-width': '350px',
        left: 'calc(100% + 1px)',
      }">
      <div class="flex h-screen flex-col">
        <div class="z-20 flex items-center justify-between border-b bg-white px-5 py-2.5">
          <div class="text-base font-medium">{{ __('Notifications') }}</div>
          <div class="flex gap-1">
            <div class="flex h-7 items-center space-x-2">
                <Button
                @click="$resources.markAllAsRead.submit"
                :loading="$resources.markAllAsRead.loading"
                v-if="
                    activeTab === 'Unread' &&
                    $resources.unreadNotifications.data?.length > 0
                "
                >
                {{__('Mark all as read')}}
                </Button>
                <TabButtons
                :buttons="[{ label: __('Unread'), active: true }, { label: __('Read') }]"
                v-model="activeTab"
                />
            </div>
            <Tooltip :text="__('Close')">
              <div>
                <Button variant="ghost" @click="toggleNotificationPanel">
                  <template #icon>
                    <LucideX class="h-4 w-4 text-gray-700" />
                  </template>
                </Button>
              </div>
            </Tooltip>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { notificationsStore } from '@/data/notifications'
  import { onClickOutside } from '@vueuse/core'
  import { Tooltip, TabButtons } from 'frappe-ui'



  export default {
    name: 'NotificationsList',
    data() {
      return {
        activeTab: 'Unread',
        target: null
      }
    },
    components: { TabButtons, Tooltip },
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
      visible_panel(){
        console.log("Dòng 126 ", notificationsStore.visible)
        return notificationsStore.visible;
      }
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
      toggleNotificationPanel(){
        notificationsStore.toggle()
      }
    },
    mounted() {
      onClickOutside(this.$refs.target, () => {
        if (visible) {
            console.log("Dòng 149")
          this.toggleNotificationPanel()
        }
      }, {
        ignore: ['#notifications-btn'],
      })
  
      this.$getResource('Unread Notifications Count')?.reload()
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
    