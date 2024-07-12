<template>
  <div class="py-6">
    <TaskList :listOptions="listOptions" :groupByStatus="true" />
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { computed } from 'vue'

const props = defineProps({
  project: {
    type: Object,
    required: true,
  },
})

let listOptions = computed(() => ({
  filters: {
    project: props.project.name,
  },
}))
</script>
