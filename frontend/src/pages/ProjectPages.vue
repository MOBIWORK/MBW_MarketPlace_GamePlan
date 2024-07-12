<template>
  <div class="py-6">
    <PageGrid
      class="mt-4.5"
      :listOptions="listOptionsPage"
    />
  </div>
</template>
<script>
import PageGrid from './PageGrid.vue'

export default {
  name: 'ProjectPages',
  props: ['project', 'listOptionsPage'],
  components: { PageGrid }
}
</script>
<style scoped>
.sort-button:deep(.feather-minimize-2) {
  transform: rotate(15deg);
}
</style>
