<template>
  <div class="flex h-full flex-1" v-if="$resources.task.doc">
    <div class="w-full flex-1">
      <div class="relative p-6">
        <div class="absolute right-0 top-0 p-6" v-show="$resources.task.setValueDebounced.loading">
          <LoadingText v-if="!$resources.task.setValueDebounced.error" :text="__('Saving...')" />
          <ErrorMessage :message="$resources.task.setValueDebounced.error" />
        </div>
        <div class="mb-4 flex items-center justify-between space-x-2">
          <input type="text" :placeholder="__('Title')"
            class="-ml-0.5 w-full rounded-sm border-none p-0.5 text-2xl font-semibold text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-400"
            @change="
              $resources.task.setValueDebounced.submit({
                title: $event.target.value,
              })
              " v-model="$resources.task.doc.title" v-focus :disabled="readOnlyControl" />
          <Dropdown :options="[
            {
              label: __('Delete'),
              onClick: () => {
                showDeleteTaskDialog = true;
              },
            },
          ]" v-if="!readOnlyControl">
            <Button variant="ghost">
              <template #icon>
                <LucideMoreHorizontal class="h-4 w-4" />
              </template>
            </Button>
          </Dropdown> 
        </div>
        <div class="w-full flex">
          <div class="text-1xl font-semibold mb-2">{{ __('Description') }}</div>
          <div class="ml-auto flex space-x-2" v-if="!readOnlyMode && !editingDescription && !readOnlyControl">
            <Button variant="ghost" @click="editingDescription = true" :label="__('Edit Description')">
              <template #icon>
                <LucideEdit class="w-4" />
              </template>
            </Button>
          </div>
        </div>
        <div class="w-full mb-6">
          <div :class="{
            'rounded-lg border p-4 focus-within:border-gray-400 w-full':
              editingDescription,
          }">
            <CommentEditor ref="description" class :value="$resources.task.doc.description"
              @change="$resources.task.doc.description = $event" @focus="editingDescription = true" :submitButtonProps="{
                variant: 'solid',
                onClick: () => {
                  $resources.task.setValue.submit({
                    description: $resources.task.doc.description,
                  })
                  editingDescription = false
                }
              }" :discardButtonProps="{
                onClick: () => {
                  editingDescription = false
                  $resources.task.reload()
                },
              }" :editable="editingDescription" />
          </div>
        </div>
        <div class="w-full mb-6 mt-1">
          <Connection :reference_doctype="'GP Task'" :reference_name="taskId" :project="projectTask"
            :readOnly="readOnlyControl">
          </Connection>
        </div>

        <div class="mt-8 flex flex-wrap items-center gap-2 sm:hidden">
          <ng-template v-if="!readOnlyControl">
            <Autocomplete :placeholder="__('Assign a user')" :options="assignableUsers"
              v-model="$resources.task.doc.assigned_to" @update:modelValue="changeUserAssign" />
            <TextInput type="date" :placeholder="__('Due date')" v-model="$resources.task.doc.due_date" @change="
              $resources.task.setValue.submit({
                due_date: $event.target.value,
              })
              " />
            <Dropdown :options="statusOptions">
              <Button>
                <template #prefix>
                  <TaskStatusIcon :status="$resources.task.doc.status" />
                </template>
                {{ $resources.task.doc.status || __('Set status') }}
              </Button>
            </Dropdown>
            <Dropdown :options="priorityOptions">
              <Button>
                <template v-if="$resources.task.doc.priority" #prefix>
                  <TaskPriorityIcon :priority="$resources.task.doc.priority" />
                </template>
                {{ $resources.task.doc.priority || __('Set priority') }}
              </Button>
            </Dropdown>
            <Autocomplete :placeholder="__('Select project')" :options="projectOptions"
              v-model="$resources.task.doc.project" @update:modelValue="changeProject" />
          </ng-template>
          <ng-teamplate v-else>
            <TextInput type="text" v-model="$resources.task.doc.assigned_to" :disabled="true" />
            <TextInput type="date" v-model="$resources.task.doc.due_date" :disabled="true" />
            <TextInput type="text" v-model="$resources.task.doc.status" :disabled="true" />
            <TextInput type="text" v-model="$resources.task.doc.priority" :disabled="true" />
            <TextInput type="text" v-model="$resources.task.doc.project" :disabled="true" />
          </ng-teamplate>

        </div>
        <div class="text-1xl font-semibold mb-2">Activity</div>
        <div class="flex items-center">
          <span class="text-sm">{{ __('Show') }}:</span>
          <div class="ml-4 mbw-bg-activity mbw-text-activity rounded px-2 py-1 cursor-pointer"
            :class="{ 'mbw-activity-active': activeActivity == 'all' }" @click="activeActivity = 'all'">All</div>
          <div class="ml-2 mbw-bg-activity mbw-text-activity rounded px-2 py-1 cursor-pointer"
            :class="{ 'mbw-activity-active': activeActivity == 'comment' }" @click="activeActivity = 'comment'">Comments</div>
          <div class="ml-2 mbw-bg-activity mbw-text-activity rounded px-2 py-1 cursor-pointer"
            :class="{ 'mbw-activity-active': activeActivity == 'history' }" @click="activeActivity = 'history'">History</div>
        </div>
        <template v-if="activeActivity == 'all'">
          <CommentsList class="mt-8" doctype="GP Task" :name="taskId" />
        </template>
        <template v-if="activeActivity == 'comment'">
          <div class="mt-5">
            <CommentsList class="mt-8" doctype="GP Task" :name="taskId" :typeFilter="'comment'" />
          </div>
        </template>
        <template v-if="activeActivity == 'history'">
          <CommentsList class="mt-8" doctype="GP Task" :name="taskId" :disableNewComment="true"
            :typeFilter="'history'" />
        </template>
      </div>
    </div>
    <div class="hidden w-[20rem] shrink-0 border-l sm:block">
      <div class="grid grid-cols-2 items-center gap-y-6 p-6 text-base text-gray-700" v-if="!readOnlyControl">
        <div>{{ __('Assignee') }}</div>
        <div>
          <Autocomplete :placeholder="__('Assign a user')" :options="assignableUsers"
            v-model="$resources.task.doc.assigned_to" @update:modelValue="changeUserAssign" />
        </div>
        <div>{{ __('Due Date') }}</div>
        <div>
          <DateTimePicker class="datepicker" icon-left="calendar" :value="$resources.task.doc.due_date" @change="(val) => ($resources.task.setValue.submit({
            due_date: val,
          }))" :placeholder="__('Due date')" input-class="border-none" />
        </div>
        <div>{{ __('Project') }}</div>
        <div>
          <Autocomplete :placeholder="__('Select project')" :options="projectOptions"
            v-model="$resources.task.doc.project" @update:modelValue="changeProject" />
        </div>
        <div>{{ __('Status') }}</div>
        <div>
          <Dropdown :options="statusOptions">
            <Button>
              <template #prefix>
                <TaskStatusIcon :status="$resources.task.doc.status" />
              </template>
              {{ $resources.task.doc.status || __('Set status') }}
            </Button>
          </Dropdown>
        </div>
        <div>{{ __('Priority') }}</div>
        <div>
          <Dropdown :options="priorityOptions">
            <Button>
              <template v-if="$resources.task.doc.priority" #prefix>
                <TaskPriorityIcon :priority="$resources.task.doc.priority" />
              </template>
              {{ $resources.task.doc.priority || __('Set priority') }}
            </Button>
          </Dropdown>
        </div>
      </div>
      <div class="grid grid-cols-2 items-center gap-y-6 p-6 text-base text-gray-700" v-else>
        <div>{{ __('Assignee') }}</div>
        <div>
          <TextInput type="text" v-model="$resources.task.doc.assigned_to" :disabled="true" />
        </div>
        <div>{{ __('Due Date') }}</div>
        <div>
          <TextInput type="text" v-model="$resources.task.doc.due_date" :disabled="true" />
        </div>
        <div>{{ __('Project') }}</div>
        <div>
          <TextInput type="text" v-model="$resources.task.doc.project" :disabled="true" />
        </div>
        <div>{{ __('Status') }}</div>
        <div>
          <TextInput type="text" v-model="$resources.task.doc.status" :disabled="true" />
        </div>
        <div>{{ __('Priority') }}</div>
        <div>
          <TextInput type="text" v-model="$resources.task.doc.priority" :disabled="true" />
        </div>
      </div>
    </div>
  </div>
  <Dialog :options="{
    title: __('Delete task'),
    message: __('Are you sure you want to delete this task?'),
    actions: [
      {
        label: __('Delete'),
        theme: 'red',
        variant: 'solid',
        onClick({ close }) {
          return $resources.task.delete.submit(null, {
            onSuccess() {
              showDeleteTaskDialog = false;
              $router.back();
            },
          })
        },
      },
    ],
  }" v-model="showDeleteTaskDialog" />
</template>
<script>
import { h } from 'vue'
import TextEditor from '@/components/TextEditor.vue'
import ReadmeEditor from '@/components/ReadmeEditor.vue'
import CommentsArea from '@/components/CommentsArea.vue'
import { focus } from '@/directives'
import { Autocomplete, Dropdown, LoadingText, TextInput, Dialog } from 'frappe-ui'
import CommentsList from '@/components/CommentsList.vue'
import TaskStatusIcon from '@/components/icons/TaskStatusIcon.vue'
import TaskPriorityIcon from '@/components/icons/TaskPriorityIcon.vue'
import Connection from '@/components/Connection.vue'
import { activeUsers } from '@/data/users'
import { activeTeams, getTeamInfo } from '@/data/teams'
import { getTeamProjects, getProject } from '@/data/projects'
import { getUser } from '@/data/users'
import DateTimePicker from '@/components/Controls/DateTimePicker.vue'

export default {
  name: 'TaskDetail',
  props: ['taskId'],
  directives: { focus },
  data() {
    return {
      showDeleteTaskDialog: false,
      editingDescription: false,
      activeActivity: 'comment',
      projectTask: null
    }
  },
  resources: {
    task() {
      return {
        type: 'document',
        doctype: 'GP Task',
        name: this.taskId,
        whitelistedMethods: {
          trackVisit: 'track_visit',
        },
        setValue: {
          onError(e) {
            let message = e.messages ? e.messages.join('\n') : e.message
            this.$toast({
              title: __('Task Update Error'),
              text: message,
              icon: 'alert-circle',
              iconClasses: 'text-red-600',
            })
          },
        },
        onSuccess(doc) {
          this.projectTask = doc.project
          if (
            ['ProjectTaskDetail', 'Task'].includes(this.$route.name) &&
            Number(this.$route.params.taskId) === doc.name
          ) {
            this.$resources.task.trackVisit.submit()
          }
        },
      }
    },
  },
  methods: {
    changeProject(option) {
      this.$resources.task.setValue.submit(
        {
          project: option?.value || '',
        },
        {
          onSuccess() {
            this.projectTask = option?.value || ''
            this.updateRoute()
          },
        }
      )
    },
    updateRoute() {
      let task = this.$resources.task.doc
      if (task) {
        this.$router.replace({
          name: task.project ? 'ProjectTaskDetail' : 'Task',
          params: {
            taskId: task.name,
            teamId: task.team,
            projectId: task.project,
          },
        })
      }
    },
    changeUserAssign(option) {
      this.$resources.task.setValue.submit(
        {
          assigned_to: option?.value || '',
        },
        {
          onSuccess() {
            this.updateRoute()
          },
        }
      )
    }
  },
  computed: {
    assignableUsers() {
      return activeUsers.value
        //.filter((user) => user.name != this.$resources.task.doc.assigned_to)
        .map((user) => ({
          label: user.full_name,
          value: user.name,
        }))
    },
    statusOptions() {
      return ['Backlog', 'Todo', 'In Progress', 'Done', 'Canceled'].map(
        (status) => {
          return {
            icon: () => h(TaskStatusIcon, { status }),
            label: status,
            onClick: () => this.$resources.task.setValue.submit({ status }),
          }
        }
      )
    },
    priorityOptions() {
      return ['Low', 'Medium', 'High'].map((priority) => {
        return {
          icon: () => h(TaskPriorityIcon, { priority }),
          label: priority,
          onClick: () => this.$resources.task.setValue.submit({ priority }),
        }
      })
    },
    projectOptions() {
      return activeTeams.value.map((team) => ({
        group: team.title,
        items: getTeamProjects(team.name).map((project) => ({
          label: project.title,
          value: project.name.toString(),
        })),
      }))
    },
    readOnlyControl(){
      if (this.$resources.task.doc.owner == getUser('sessionUser').name || this.$resources.task.doc.assigned_to == getUser('sessionUser').name) {
        return false;
      } else if (this.$resources.task.doc.team != null && this.$resources.task.doc.project != null) {
        let projectInfo = getProject(this.$resources.task.doc.project);
        let teamInfo = getTeamInfo(this.$resources.task.doc.team).data;
        let roleByProject = this.$getRoleByUser(null, projectInfo);

        if (roleByProject == "manager") {
          return false;
        } else {
          let roleByTeam = this.$getRoleByUser(teamInfo, null);
          if (roleByTeam != "guest" && roleByTeam != "member") {
            return false;
          }
        }
      }
      return true
    }
  },
  components: {
    ReadmeEditor,
    TextEditor,
    CommentsArea,
    Autocomplete,
    TextInput,
    Dropdown,
    CommentsList,
    TaskStatusIcon,
    LoadingText,
    TaskPriorityIcon,
    Connection
  }
}
</script>

<style scoped>
.mbw-bg-activity {
  background-color: #091E420F;
}

.mbw-bg-activity:hover {
  background-color: #67402a2c;
}

.mbw-activity-active {
  color: #0C66E4 !important;
  background-color: #E9F2FF !important;
}

.mbw-text-activity {
  font-weight: 500;
  font-size: 14px;
  font-style: normal;
  font-family: inherit;
  text-align: center;
  color: #172B4D;
}
</style>