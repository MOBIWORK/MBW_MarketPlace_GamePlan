<template>
  <div>
    <header
      class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5"
    >
      <Breadcrumbs
        class="h-7"
        :items="[{ label: __('My Tasks'), route: { name: 'MyTasks' } }]"
      />
      <Button variant="solid" @click="showNewTaskDialog" v-if="!readOnlyByRole()">
        <template #prefix>
          <LucidePlus class="h-4 w-4" />
        </template>
        {{ __('Add new') }}
      </Button>
    </header>

    <div class="mx-auto w-full px-5">
      <div class="py-6">
        <TaskList :listOptions="listOptions" :groupByStatus="true" />
        <NewTaskDialog ref="newTaskDialog" />
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import { getCachedListResource, usePageMeta, Breadcrumbs } from 'frappe-ui'
import { getUser } from '@/data/users'
import {getRoleByUser} from '@/utils'

let newTaskDialog = ref(null)

let listOptions = computed(() => ({
  filters: { assigned_or_owner: getUser('sessionUser').name },
}))

function showNewTaskDialog() {
  newTaskDialog.value.show({
    defaults: {
      assigned_to: getUser('sessionUser').name,
    },
    onSuccess: () => {
      let tasks = getCachedListResource(['Tasks', listOptions.value])
      if (tasks) {
        tasks.reload()
      }
    },
  })
}

function readOnlyByRole(){
  let role = getRoleByUser(null, null)
  if(role == "guest") return true
  return false
}

usePageMeta(() => {
  return {
    title: __('My Tasks'),
  }
})
</script>
