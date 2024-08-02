import { createListResource, createResource } from 'frappe-ui'
import { computed } from 'vue'

export let page_owner = createResource({
    url: "gameplan.command_palette.get_page_owner",
    method: "GET",
    auto: true
})

export let activePage = computed(
    () => page_owner.data
  )