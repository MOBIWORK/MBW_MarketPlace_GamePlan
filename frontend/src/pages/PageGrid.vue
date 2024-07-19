<template>
  <div class="grid grid-cols-1 gap-5 md:grid-cols-3 lg:grid-cols-4">
    <div class="text-base text-gray-600" v-if="!$resources.pages.data?.length">
      {{ __('No pages') }}
    </div>
    <div class="relative" v-for="d in $resources.pages.data" :key="d.name">
      <div class="absolute right-0 top-0 p-3" v-if="onShowAction(d)">
        <Dropdown
          :button="{
            icon: 'more-horizontal',
            label: __('Page Options'),
            variant: 'ghost',
          }"
          :options="[
            {
              label: __('Delete'),
              icon: 'trash',
              onClick: () => {
                pageSource = d;
                showDeleteDialog = true;
              },
            },
          ]"
          placement="right"
        />
      </div>
      <router-link
        :to="{
          name: d.project ? 'ProjectPage' : 'Page',
          params: {
            pageId: d.name,
            slug: d.slug,
            projectId: d.project,
            teamId: d.team,
          },
        }"
      >
        <section
          class="aspect-[37/50] cursor-pointer overflow-hidden rounded-md border border-gray-50 p-3 shadow-lg transition-shadow hover:shadow-2xl"
        >
          <div class="overflow-hidden text-ellipsis whitespace-nowrap">
            <h1 class="text-lg font-semibold leading-none pr-12 truncate">
              {{ d.title }}
            </h1>
            <div
              class="mt-1.5 flex items-center text-sm leading-none text-gray-700"
            >
              <!-- <div v-if="d.project">
                {{ projectTitle(d.project).value }} &middot;&nbsp;
              </div> -->
              <div>Updated {{ $dayjs(d.modified).fromNow() }}</div>
            </div>
            <hr class="my-2 border-gray-100" />
            <div
              class="prose prose-sm pointer-events-none w-[200%] origin-top-left scale-[.55] prose-p:my-1 md:w-[250%] md:scale-[.39]" style="font-size: 2rem !important;"
              v-html="d.content"
            />
          </div>
        </section>
      </router-link>
    </div>
  </div>
  <Dialog
        :options="{
          title: __('Delete Page'),
          message: __('Are you sure you want to delete this page?'),
          actions: [
            {
              label: __('Delete'),
              onClick: ({ close }) => {
                showDeleteDialog = false
                return $resources.pages_source.delete.submit(pageSource.name)
              },
              variant: 'solid',
              theme: 'red',
            },
            {
              label: __('Cancel'),
            },
          ],
        }"
        v-model="showDeleteDialog"
      />
</template>
<script>
import { projectTitle } from '@/utils/formatters'
import { Dropdown } from 'frappe-ui'
import { getUser } from '@/data/users'

export default {
  name: 'PageGrid',
  props: ['listOptions'],
  data(){
    return{
      showDeleteDialog: false,
      pageSource: {}
    }
  },
  resources: {
    pages() {
      return {
        url: "gameplan.api.get_mypages_by_filter",
        method: "GET",
        params: {
          order_by: this.listOptions.orderBy,
          search: this.listOptions.search != undefined && this.listOptions.search != null? this.listOptions.search : "",
          project: this.listOptions.project != undefined && this.listOptions.project != null? this.listOptions.project: "" 
        },
        auto: true
      }
    },
    pages_source(){
      return {
        type: 'list',
        cache: ['Pages', this.listOptions],
        doctype: 'GP Page',
        fields: [
          'name',
          'creation',
          'title',
          'content',
          'slug',
          'project',
          'team',
          'modified',
        ],
        delete:{
          onSuccess(){
            this.$resources.pages.fetch()
          }
        }
      }
    }
  },
  methods: {
    projectTitle,
    onShowAction(page){
      if(page.owner == getUser('sessionUser').name) return true;
      return false;
    }
  },
  components: { Dropdown },
}
</script>
