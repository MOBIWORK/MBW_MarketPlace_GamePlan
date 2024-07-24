<template>
  <div v-if="visible" ref="target" class="absolute z-20 h-screen bg-white transition-all duration-300 ease-in-out"
    :style="{
      'box-shadow': '8px 0px 8px rgba(0, 0, 0, 0.1)',
      'max-width': '450px',
      'min-width': '430px',
      left: 'calc(100% + 1px)',
    }">
    <NotificationsList :parent_panel="'sidebar'" @eventReadNotification="onReadNotification()"></NotificationsList>
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
  setup(props, { emit }) {
    const target = ref(null)
    const closePanel = () => {
      emit('changeVisible', false)
    }
    onClickOutside(target, closePanel, { ignore: ['#notifications-btn'] })
    return { target }
  },
  methods: {
    onReadNotification(){
      this.$emit('changeVisible', false)
    }
  }
}
</script>

<style scoped>
</style>