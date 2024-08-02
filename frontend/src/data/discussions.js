import { createListResource, createResource } from 'frappe-ui'
import { computed } from 'vue'

export let discussion_owner = createResource({
    url: "gameplan.command_palette.get_discussion_owner",
    method: "GET",
    auto: true
})

export let activeDiscussion = computed(
    () => discussion_owner.data
  )