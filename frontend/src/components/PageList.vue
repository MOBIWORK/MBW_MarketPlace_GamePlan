<template>
  <div v-if="pages.data?.length">
    <div v-for="(page, index) in pages.data" :key="page.name">
      <router-link
        :to="{
          name: 'ProjectPage',
          params: {
            teamId: page.team,
            projectId: page.project,
            pageId: page.name,
          },
        }"
        class="flex h-15 items-start rounded-md p-2.5 hover:bg-gray-100"
      >
        <div class="min-w-0">
          <div class="text-base font-medium leading-4 truncate">
            {{ page.title }}
          </div>
          <div class="mt-1.5 flex items-center">
            <div class="flex items-center space-x-1.5">
              <UserAvatar :user="page.owner" size="xs" />
              <span class="text-base">{{ $user(page.owner).full_name }}</span>
            </div>
            <span class="px-2 text-gray-600">&middot;</span>
            <span class="text-base text-gray-600">
              {{__('Updated')}} {{ $dayjs(page.modified).fromNow() }}
            </span>
          </div>
        </div>
      </router-link>
      <div class="mx-2.5 border-b" v-if="index < pages.data.length - 1"></div>
    </div>
  </div>
  <div
    class="flex flex-col items-center rounded-lg border-2 border-dashed py-8"
    v-else
  >
    <div class="text-base text-gray-600">{{__('No pages')}}</div>
    <Button v-if="!readOnlyByRole()" class="mt-1" :variant="'solid'" :loading="isloadingAddPage" theme="gray" @click="() => onAddPage()">{{ __('Add page') }}</Button>
  </div>
</template>
<script setup>
import { createListResource, createResource } from 'frappe-ui'
import {getRoleByUser} from '@/utils'
import router from '@/router'
import { watch } from 'vue';

let props = defineProps({
  listOptions: {
    type: Object,
    default: () => ({}),
  },
})
let emits = defineEmits(['load_data'])

let isloadingAddPage = false

function onAddPage(){
  let me = this;
  isloadingAddPage.value = true
  let newPage = createResource({
    url: 'frappe.client.insert',
    params: {
      doc: {
        doctype: 'GP Page',
        project: props.listOptions.filters.project,
        title: __('Untitled'),
        content: '',
      },
    },
    onSuccess(doc) {
      router.push({
        name: 'ProjectPage',
        params: { pageId: doc.name },
      })
      isloadingAddPage.value = false
    }
  })
  newPage.submit();
}

function readOnlyByRole(){
  let role = getRoleByUser(null, null)
  if(role == "guest") return true
  return false
}

let pages = createListResource({
  type: 'list',
  doctype: 'GP Page',
  cache: ['Pages', props.listOptions],
  fields: ['name', 'title', 'slug', 'modified', 'owner', 'project', 'team'],
  filters: props.listOptions.filters,
  pageLength: props.listOptions.pageLength || 20,
  auto: true,
  realtime: true,
  orderBy: props.listOptions.orderBy || 'modified desc'
})
watch(pages, (newData) => {
  emits('load_data', newData.data);
}, { deep: true });
</script>
