<template>
  <Dialog v-model="showLanguage" :options="{ size: 'lg', position: 'top' }" class="z-50">
    <template #body>
      <div>
        <div class="flex flex-col p-2 border-b relative">
          <h1 class="mb-3 px-2 pt-2 text-lg font-semibold text-ink-gray-9">
            {{ __('Select language') }}
          </h1>
          <Button
            class="absolute right-5 top-3.5"
            variant="ghost"
            icon="x"
            @click="showLanguage = false"
          />
        </div>
        <div class="flex flex-1 flex-col overflow-y-auto bg-surface-modal mb-4 px-4 pt-3">
          <Autocomplete
            :options="optionsLanguage"
            v-model="single"
            placeholder="Select language"
            :hideSearch="true"
          >
            <template #prefix>
              <img :src="single.image" class="mr-2 h-4.5 w-7" />
            </template>
            <template #item-prefix="{ option }">
              <img :src="option.image.toString()" class="h-4.5 w-7 mr-2" />
            </template>
          </Autocomplete>
        </div>
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import { showLanguage, defaultLanguage } from '@/composables/language.js'
import { Dialog, Button, createResource, Autocomplete } from 'frappe-ui'
import { ref, watch } from 'vue'

const optionsLanguage = [
  {
    label: __('Vietnamese'),
    value: 'vi',
    image: '/assets/gameplan/images/icon_flag_vi.svg',
  },
  {
    label: __('English'),
    value: 'en',
    image: '/assets/gameplan/images/icon_flag_en.svg',
  },
]
const single = ref()

const changeLanguage = createResource({
  url: 'gameplan.api_root.language.change_language',
  onError(err) {
    throw new Error(__('Language not found'))
  },
  onSuccess(data) {
    window.location.reload()
  },
})

watch(
  () => defaultLanguage.value,
  (val) => {
    single.value = optionsLanguage.find((item) => item.value === defaultLanguage.value)
  },
  {
    immediate: true,
  },
)

watch(single, (val) => {
  let v = val
  if (!val) {
    v = optionsLanguage.find((item) => item.value === defaultLanguage.value)
    single.value = v
  }
  if (v.value !== defaultLanguage.value) {
    changeLanguage.submit({ lang: v.value })
  }
})
</script>
