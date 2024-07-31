<template>
  <div class="pt-6">
    <div class="space-y-5 pb-40">
      <ProjectOverviewReadme :project="project" />
      <div class="sm:rounded sm:border sm:px-4 sm:py-3">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-xl font-semibold">{{ __('Discussions') }}</h2>
          <div class="flex items-center" v-if="displayControlDiscussion">
            <Button :variant="'outline'" theme="gray" :route="{ name: 'ProjectDiscussionNew' }" v-if="!readOnlyByRole()">{{ __('Add discussion') }}</Button>
            <Button class="ml-3" :variant="'solid'" theme="gray" :route="{ name: 'ProjectDiscussions' }">{{ __('View all') }}</Button>
          </div>
        </div>
        <DiscussionList
          :listOptions="{
            filters: { project: project.doc.name },
            pageLength: 4,
          }"
          :hideLoadMore="true"
          :showDiscussion="true"
          @load_data="onLoadDataDiscussion"
        />
      </div>
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div class="sm:rounded sm:border sm:px-4 sm:py-3">
          <div class="mb-3 flex items-center justify-between">
            <h2 class="text-xl font-semibold">{{ __('Tasks') }}</h2>
            <div class="flex items-center" v-if="displayControlTask">
              <Button :variant="'outline'" theme="gray" @click="() => onAddTask()" v-if="!readOnlyByRole()">{{ __('Add task') }}</Button>
              <Button class="ml-3" :variant="'solid'" theme="gray" :route="{ name: 'ProjectTasks' }">{{ __('View all') }}</Button>
            </div>
          </div>
          <TaskList
            :listOptions="optionTask"
            :showAddTask="true"
            @load_data="onLoadDataTask"
          />
          <NewTaskDialog ref="newTaskDialog" />
        </div>
        <div class="sm:rounded sm:border sm:px-4 sm:py-3">
          <div class="mb-3 flex items-center justify-between">
            <h2 class="text-xl font-semibold">{{ __('Pages') }}</h2>
            <div class="flex items-center" v-if="displayControlPage">
              <Button :variant="'outline'" theme="gray" @click="() => onAddPage()" v-if="!readOnlyByRole()">{{ __('Add page') }}</Button>
              <Button class="ml-3" :variant="'solid'" theme="gray" :route="{ name: 'ProjectPages' }">{{ __('View all') }}</Button>
            </div>
          </div>
          <PageList
            :listOptions="{
              filters: {
                project: project.doc.name,
              },
              pageLength: 4,
            }"
            @load_data="onLoadPage"
          />
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import ProjectOverviewReadme from './ProjectOverviewReadme.vue'
import { createResource, getCachedListResource } from 'frappe-ui'
import { getUser } from '@/data/users'

export default {
  name: 'ProjectOverview',  
  props: ['project'],
  components: {
    ProjectOverviewReadme,
  },
  data() {
    return {
      newTaskDialog: null,
      optionTask: {
        filters: {
          project: this.project.doc.name,
          status: ['in', ['Backlog', 'Todo', 'In Progress']],
        },
        pageLength: 4,
      },
      displayControlDiscussion: false,
      displayControlTask: false,
      displayControlPage: false
    }
  },
  methods:{
    onAddTask(){
      let me = this;
      this.$refs.newTaskDialog.show({
        defaults: {
          project: this.project.doc.name,
          assigned_to: getUser('sessionUser').name,
        },
        onSuccess: () => {
          let tasks = getCachedListResource(['Tasks', me.optionTask])
          if (tasks) {
            tasks.reload()
          }
        },
      })
    },
    onAddPage(){
      let me = this;
      let newPage = createResource({
        url: 'frappe.client.insert',
        params: {
          doc: {
            doctype: 'GP Page',
            project: me.project.doc.name,
            title: __('Untitled'),
            content: '',
          },
        },
        onSuccess(doc) {
          me.$router.push({
            name: 'ProjectPage',
            params: { pageId: doc.name },
          })
        }
      })
      newPage.submit();
    },
    onLoadDataDiscussion(data){
      if(data.length > 0) this.displayControlDiscussion = true;
    },
    onLoadDataTask(data){
      if(data.length > 0) this.displayControlTask = true;
    },
    onLoadPage(data){
      if(data.length > 0) this.displayControlPage = true;
    },
    readOnlyByRole(){
      let role = this.$getRoleByUser(null, this.project.doc)
      if(role == "guest") return true
      return false
    }

  }
}
</script>
