import { createListResource, createResource } from 'frappe-ui'
import { computed } from 'vue'

export let task_owner = createResource({
    url: "gameplan.command_palette.get_task_owner",
    method: "GET",
    auto: true
})

export let activeTask = computed(
    () => task_owner.data
  )