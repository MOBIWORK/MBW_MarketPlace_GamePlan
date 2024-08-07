<template>
  <div class="@container" v-if="tasks.data?.length">
    <div v-for="group in groupedTasks" :key="group.title">
      <button
        class="group flex w-full items-baseline rounded-sm bg-gray-50 px-2.5 py-2 text-base transition hover:bg-gray-100"
        v-if="group.title && group.tasks.length"
        @click="isOpen[group.title] = !isOpen[group.title]"
      >
        <span class="font-medium text-gray-900">
          {{ group.title }}
        </span>
        <span class="ml-2 text-sm text-gray-600">{{ group.tasks.length }}</span>
        <span class="ml-auto hidden text-sm text-gray-600 group-hover:inline">
          {{ isOpen[group.title] ? __('Collapse') : __('Expand') }}
        </span>
      </button>
      <div :class="{ hidden: !(isOpen[group.title] ?? true) }">
        <div v-for="(d, index) in group.tasks" :key="d.name">
          <router-link
            :to="{
              name: d.project ? 'ProjectTaskDetail' : 'Task',
              params: { teamId: d.team, projectId: d.project, taskId: d.name },
            }"
            class="flex h-15 w-full items-center rounded p-2.5 transition hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
            :class="{
              'pointer-events-none':
                tasks.delete.loading && tasks.delete.params.name === d.name,
            }"
          >
            <div class="w-full">
              <div class="flex min-w-0 items-start">
                <LoadingIndicator
                  class="h-4 w-4 text-gray-600"
                  v-if="
                    tasks.delete.loading && tasks.delete.params.name === d.name
                  "
                />
                <Tooltip text="Change status" v-else>
                  <Dropdown
                    :options="
                      statusOptions({
                        onClick: (status) =>
                          tasks.setValue.submit({
                            status,
                            name: d.name,
                          }),
                      })
                    "
                  >
                    <button
                      class="flex rounded-full focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
                    >
                      <TaskStatusIcon :status="d.status" />
                    </button>
                  </Dropdown>
                </Tooltip>
                <div
                  class="ml-2.5 overflow-hidden text-ellipsis whitespace-nowrap text-base font-medium leading-4 text-gray-900"
                >
                  {{ d.title }}
                </div>
                <div
                  class="ml-auto shrink-0 whitespace-nowrap text-sm text-gray-600"
                >
                  {{ $dayjs(d.modified).fromNow() }}
                </div>
              </div>

              <div class="ml-6.5 mt-1.5 flex items-center">
                <div class="text-base text-gray-600">#{{ d.name }}</div>
                <div
                  v-if="$route.name != 'ProjectOverview' && d.project"
                  class="flex min-w-0 items-center text-base leading-none text-gray-600"
                >
                  <div class="px-2 leading-none text-gray-600">&middot;</div>
                  <div>{{ d.team_title }}</div>
                  <LucideChevronRight class="h-3 w-3 shrink-0 text-gray-600" />
                  <div class="overflow-hidden text-ellipsis whitespace-nowrap">
                    {{ d.project_title }}
                  </div>
                </div>
                <div class="hidden items-center @md:flex" v-if="d.assigned_to">
                  <div class="px-2 leading-none text-gray-600">&middot;</div>
                  <span class="whitespace-nowrap text-base text-gray-600">
                    {{ $user(d.assigned_to).full_name }}
                  </span>
                </div>

                <template v-if="d.due_date">
                  <div class="px-2 leading-none text-gray-600">&middot;</div>
                  <div class="flex items-center">
                    <LucideCalendar class="h-3 w-3 text-gray-600" />
                    <span
                      class="ml-2 whitespace-nowrap text-base text-gray-600"
                    >
                      {{ $dayjs(d.due_date).format('D MMM') }}</span
                    >
                  </div>
                </template>
                <template v-if="d.priority">
                  <div class="px-2 leading-none text-gray-600">&middot;</div>
                  <div class="flex items-center">
                    <div
                      class="h-2 w-2 rounded-full"
                      :class="{
                        'bg-red-400': d.priority === 'High',
                        'bg-yellow-500': d.priority === 'Medium',
                        'bg-gray-300': d.priority === 'Low',
                      }"
                    ></div>
                    <span class="ml-2 text-base text-gray-600">
                      {{ d.priority }}
                    </span>
                  </div>
                </template>
                <div
                  class="ml-auto inline-grid h-4 w-4 shrink-0 place-items-center rounded-full bg-gray-200 text-xs"
                  :class="[
                    d.unread ? 'text-gray-900' : 'text-gray-600',
                    d.comments_count ? '' : 'invisible',
                  ]"
                >
                  {{ d.comments_count || 0 }}
                </div>
              </div>
            </div>
          </router-link>
          <div
            class="mx-2.5 border-b"
            v-if="index < group.tasks.length - 1"
          ></div>
        </div>
      </div>
    </div>
  </div>
  <div
    class="flex flex-col items-center rounded-lg border-2 border-dashed py-8"
    v-else
  >
    <div class="text-base text-gray-600">{{__('No tasks')}}</div>
    <Button v-if="showAddTask && !readOnlyByRole()" class="mt-1" :variant="'solid'" theme="gray" @click="() => onAddTask()" >{{ __('Add task') }}</Button>
  </div>
  <NewTaskDialog ref="newTaskDialog" />
</template>
<script>
import { h, watch } from 'vue'
import { LoadingIndicator, Dropdown, Tooltip, getCachedListResource } from 'frappe-ui'
import TaskStatusIcon from './icons/TaskStatusIcon.vue'
import { getUser } from '@/data/users'

export default {
  name: 'TaskList',
  props: {
    groupByStatus: {
      type: Boolean,
      default: false,
    },
    listOptions: {
      type: Object,
      default: () => ({}),
    },
    showAddTask: {
      type: Boolean,
      default: false
    }
  },
  emits: ['load_data'],
  data() {
    return {
      newTaskDialog: null,
      isOpen: {
        Backlog: true,
        Todo: true,
        'In Progress': true,
        Canceled: false,
        Done: false,
      },
    }
  },
  components: {
    LoadingIndicator,
    Dropdown,
    Tooltip,
    TaskStatusIcon,
  },
  resources: {
    tasks() {
      return {
        type: 'list',
        url: 'gameplan.gameplan.doctype.gp_task.gp_task.get_list',
        cache: ['Tasks', this.listOptions],
        doctype: 'GP Task',
        fields: [
          '*',
          'project.title as project_title',
          'team.title as team_title',
        ],
        filters: this.listOptions.filters,
        orderBy: this.listOptions.orderBy,
        pageLength: this.listOptions.pageLength || 20,
        auto: true,
        realtime: true,
        txt_search: "Thi",
        is_my_task: "true"
      }
    },
  },
  methods: {
    statusOptions({ onClick }) {
      return ['Backlog', 'Todo', 'In Progress', 'Done', 'Canceled'].map(
        (status) => {
          return {
            icon: () => h(TaskStatusIcon, { status }),
            label: status,
            onClick: () => onClick(status),
          }
        }
      )
    },
    onAddTask(){
      let me = this;
      this.$refs.newTaskDialog.show({
        defaults: {
          project: this.listOptions.filters.project,
          assigned_to: getUser('sessionUser').name,
        },
        onSuccess: () => {
          this.onReloadTasks()
        },
      })
    },
    readOnlyByRole(){
      let role = this.$getRoleByUser(null, null)
      if(role == "guest") return true
      return false
    },
    onReloadTasks(){
      this.$resources.tasks.update({
        filters: this.listOptions.filters,
        orderBy: this.listOptions.orderBy
      })
      this.$resources.tasks.fetch()
    }
  },
  computed: {
    tasks() {
      return this.$resources.tasks
    },
    groupedTasks() {
      if (!this.groupByStatus) {
        return [
          {
            id: 'all',
            title: '',
            tasks: this.tasks.data,
          },
        ]
      }
      return ['In Progress', 'Todo', 'Backlog', 'Done', 'Canceled'].map(
        (status) => {
          return {
            id: status,
            title: status,
            tasks: this.tasksByStatus[status] || [],
          }
        }
      )
    },
    tasksByStatus() {
      const tasksByStatus = {}
      this.tasks.data.forEach((task) => {
        if (!tasksByStatus[task.status]) {
          tasksByStatus[task.status] = []
        }
        tasksByStatus[task.status].push(task)
      })
      return tasksByStatus
    },
  },
  mounted() {
    watch(
      () => this.tasks.data,
      (newData) => {
        this.$emit('load_data', newData);
      },
      { deep: true }
    );
  },
}
</script>
