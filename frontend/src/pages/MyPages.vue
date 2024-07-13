<template>
  <header
    class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5"
  >
    <div class="flex items-center">
      <Breadcrumbs
        class="h-7 mr-4"
        :items="[{ label: __('My Pages'), route: { name: 'MyPages' } }]"
      />
      <TextInput class="border-none md:w-96" type="text" size="sm" :placeholder="__('Search title, team or project')" v-model="search" :debounce="800" @update:modelValue="onChangeSearch()">
        <template #suffix>
          <LucideSearch class="h-4 w-4" />
        </template>
      </TextInput>
    </div>
    <div class="flex items-center space-x-2">
      <Select
        :options="[
          {
            label: __('Sort by'),
            value: '',
            disabled: true,
          },
          // {
          //   label: __('Page Title'),
          //   value: 'title asc',
          // },
          {
            label: __('Date Updated'),
            value: 'modified desc',
          },
          {
            label: __('Date Created'),
            value: 'creation desc',
          },
        ]"
        v-model="orderBy"
        @update:modelValue="onChangeSortBy()"
      />

      <Button variant="solid" @click="$resources.newPage.submit()">
        <template #prefix>
          <LucidePlus class="h-4 w-4" />
        </template>
        {{__('Add new')}}
      </Button>
    </div>
  </header>
  <div class="mx-auto w-full px-5">
    <div class="py-6">
      <PageGrid
        :listOptions="listOptions"
      />
    </div>
  </div>
</template>
<script>
import { Dropdown, Select, Breadcrumbs, TextInput } from 'frappe-ui'
import ArrowDownUp from '~icons/lucide/arrow-up-down'
import PageGrid from './PageGrid.vue'

export default {
  name: 'MyPages',
  components: { Dropdown, Select, ArrowDownUp, PageGrid, Breadcrumbs, TextInput },
  data() {
    return {
      orderBy: 'modified desc',
      search: "",
      listOptions: {
        'orderBy': 'modified desc',
        'search': this.search
      }
    }
  },
  resources: {
    newPage() {
      return {
        url: 'frappe.client.insert',
        params: {
          doc: {
            doctype: 'GP Page',
            title: __('Untitled'),
            content: '',
          },
        },
        onSuccess(doc) {
          this.$router.push({
            name: 'Page',
            params: { pageId: doc.name },
          })
        },
      }
    },
  },
  methods: {
    onChangeSearch(){
      this.listOptions.search = this.search;
    },
    onChangeSortBy(){
      this.listOptions.orderBy = this.orderBy;
    }
  },
  pageMeta() {
    return {
      title: __('My Pages'),
    }
  },
}
</script>
<style scoped>
.sort-button:deep(.feather-minimize-2) {
  transform: rotate(15deg);
}
</style>
