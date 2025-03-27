import { ref } from 'vue'
import { createResource } from 'frappe-ui'

export const defaultLanguage = ref()
createResource({
  url: 'gameplan.api_root.language.get_language',
  cache: 'Language',
  auto: true,
  onSuccess: (data) => {
    defaultLanguage.value = data
  },
})
export const showLanguage = ref(false)
