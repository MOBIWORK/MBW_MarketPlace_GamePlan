import { createResource } from 'frappe-ui'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export let unreadNotifications = createResource({
  cache: 'Unread Notifications Count',
  url: 'gameplan.api.unread_notifications',
  initialData: 0,
  auto: true,
})

export let configNotifications = createResource({
  url: 'gameplan.api.get_config_notifications',
  method: "GET"
})

export const notificationsStore = defineStore('gp-notifications', () => {
  let visible = ref(false)

  const notifications = []

  // const mark_as_read = createResource({
  //   url: 'crm.api.notifications.mark_as_read',
  //   auto: false,
  //   onSuccess: () => {
  //     mark_as_read.params = {}
  //     notifications.reload()
  //   },
  // })

  function toggle() {
    console.log("togle");
    visible.value = !visible.value
    console.log(visible)
  }

  const allNotifications = computed(() => notifications.data || [])
  const unreadNotificationsCount = computed(
    () => notifications.data?.filter((n) => !n.read).length || 0
  )

  function mark_doc_as_read(doc) {
    // mark_as_read.params = { doc: doc }
    // mark_as_read.reload()
    toggle()
  }

  return {
    notifications,
    visible,
    allNotifications,
    unreadNotificationsCount,
    //mark_as_read,
    mark_doc_as_read,
    toggle,
  }
})