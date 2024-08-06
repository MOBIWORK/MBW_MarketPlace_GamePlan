<template>
  <div class="h-full">
    <header
      class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5"
    >
      <Breadcrumbs
        class="h-7"
        :items="[{ label: __('My Tasks'), route: { name: 'MyTasks' } }]"
      />
      <div class="flex items-center">
        <Dropdown :options="[
          {
            label: 'List View',
            onClick: () => onChangeTypeView('list'),
            icon: 'list'
          },
          {
            label: 'Kanban',
            onClick: () => onChangeTypeView('kanban'),
            icon: 'trello'
          }
        ]" class="mr-3">
          <Button class="pl-2.5" style="width: 7rem !important;justify-content: flex-start !important;">
            <template #icon>
              <FeatherIcon v-if="viewTask=='list'"
                name="list"
                class="h-4 w-4"
              />
              <FeatherIcon v-if="viewTask=='kanban'"
                name="trello"
                class="h-4 w-4 justify-start"
              />
              <span v-if="viewTask=='list'">List View</span>
              <span v-if="viewTask=='kanban'">Kanban</span>
            </template>
          </Button>
        </Dropdown>
        <KanbanSettings v-if="viewTask=='kanban'" @update="updateKanbanSettings"
          :columnFields="[
            {'fieldname': 'status', 'fieldtype': 'Select', 'label': 'Status'},
            {'fieldname': 'priority', 'fieldtype': 'Select', 'label': 'Priority'}
          ]"
          :titleFields="[
            {'fieldname': 'title', 'fieldtype': 'Data', 'label': 'Title'},
            {'fieldname': 'due_date', 'fieldtype': 'Datetime', 'label': 'Due Date'},
            {'fieldname': 'status', 'fieldtype': 'Select', 'label': 'Status'},
            {'fieldname': 'priority', 'fieldtype': 'Select', 'label': 'Priority'},
            {'fieldname': 'assigned_to', 'fieldtype': 'Link', 'label': 'Assigned To'}
          ]"
          :columnFieldDefault="{'fieldname': 'status', 'fieldtype': 'Select', 'label': 'Status'}"
          :titleFieldDefault="{'fieldname': 'title', 'fieldtype': 'Data', 'label': 'Title'}"
          ></KanbanSettings>
        <Button variant="solid" @click="showNewTaskDialog" v-if="!readOnlyByRole() && viewTask=='list'">
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
          {{ __('Add new') }}
        </Button>
      </div>
    </header>

    <div class="mx-auto w-full px-5" style="height: calc(100% - 49px);">
      <div class="pt-6 h-full">
        <KanbanView
          v-if="viewTask=='kanban'"
          :kanban="dataByKanban"
          :options="{
            onNewClick: (column) => createTask(column),
          }"
          @update="(data) => updateKanban(data)"
          @update_assign_task="(data) => onUpdateAssign(data)"
        >
          <template #title="{ titleField, itemName }">
            <div class="flex items-center justify-between w-full">
              <div class="truncate cursor-pointer" style="width: calc(100% - 28px);" @click="onShowTaskDetail(itemName, titleField)">
                <div v-if="titleField === 'status'">
                  <TaskStatusIcon :status="getRow(itemName, titleField).label" />
                </div>
                <div v-else-if="titleField === 'priority'">
                  <TaskPriorityIcon :priority="getRow(itemName, titleField).label" />
                </div>
                <div v-else-if="titleField === 'assigned_to'">
                  <Avatar
                    v-if="getRow(itemName, titleField).full_name"
                    class="flex items-center"
                    :image="getRow(itemName, titleField).user_image"
                    :label="getRow(itemName, titleField).full_name"
                    size="sm"
                  />
                </div>
                <div
                  v-if="['modified', 'creation'].includes(titleField)"
                  class="truncate text-base"
                >
                  <Tooltip :text="getRow(itemName, titleField).label">
                    <div>{{ getRow(itemName, titleField).timeAgo }}</div>
                  </Tooltip>
                </div>
                <div
                  v-else-if="getRow(itemName, titleField).label"
                  class="truncate text-base"
                >
                  {{ getRow(itemName, titleField).label }}
                </div>
                <div class="text-gray-500" v-else>{{ __('No Title') }}</div>
              </div>
              <div class="w-7">
                <Dropdown
                class="flex items-center gap-2"
                :options="actions(itemName)"
                variant="ghost"
                @click.stop.prevent
              >
                <Button icon="more-vertical" variant="ghost" />
              </Dropdown>
              </div>
            </div>
          </template>
        </KanbanView>
        <TaskList v-if="viewTask=='list'" :listOptions="listOptions" :groupByStatus="true" />
        <NewTaskDialog ref="newTaskDialog" />
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
        onClick: () => onConfirmDeleteTask()
      },
    ],
  }" v-model="showDialogDelete" />
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import { 
  getCachedListResource,
  usePageMeta, 
  Breadcrumbs, 
  Dropdown, 
  FeatherIcon, 
  Avatar, 
  Tooltip, 
  TextEditor, 
  Button,
  createResource,
  Dialog,
  createListResource
} from 'frappe-ui'
import { getUser } from '@/data/users'
import {getRoleByUser} from '@/utils'
import KanbanSettings from '@/components/Kanban/KanbanSettings.vue'
import KanbanView from '@/components/Kanban/KanbanView.vue'
import TaskStatusIcon from '@/components/icons/TaskStatusIcon.vue'
import TaskPriorityIcon from '@/components/icons/TaskPriorityIcon.vue'
import { dateFormat, dateTooltipFormat, timeAgo, createToast } from '@/utils'
import router from '@/router'

let defaultParamsKanban = ref({
  doctype: 'GP Task',
  filters: JSON.stringify({}),
  order_by: 'modified desc',
  column_field: "status",
  title_field: "title",
  rows: JSON.stringify(["name", "title", "description", "assigned_to", "status", "priority", "project", "team", "due_date", "comments_count"]),
  kanban_columns: JSON.stringify([{'name': "Backlog"},{'name': "Todo"},{'name': "In Progress"},{'name': "Done"},{'name': "Canceled"}]),
  kanban_fields: JSON.stringify(["description", "priority", "due_date", "comments_count", "assigned_to"])
})

let dataByKanban = createResource({
  url: "gameplan.api.get_data_kanban",
  method: 'GET',
  params: defaultParamsKanban.value,
  auto: true
})

let deleteTaskResource = createResource({
  url: "gameplan.api.delete_task_by_id",
  method: "DELETE",
  onSuccess(data){
    if(data.status == "ok"){
      createToast({
        title: __('Delete successfully task'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      dataByKanban.fetch()
    }else{
      createToast({
        title: __('Delete failed task'),
        icon: 'x',
        iconClasses: 'text-red-600',
      })
    }
  }
})

let tasksListResource = createListResource({
  doctype: 'GP Task',
  auto: false
})

let newTaskDialog = ref(null)
let viewTask = ref("list")
let showDialogDelete = ref(false)
let nameTaskDelete = ref("")

const rows = computed(() => {
  if (!dataByKanban.data?.data) return []

  return getKanbanRows(dataByKanban.data.data)
})

function getKanbanRows(data) {
  let _rows = []
  data.forEach((column) => {
    column.data?.forEach((row) => {
      _rows.push(row)
    })
  })
  return parseRows(_rows)
}

function parseRows(rows) {
  return rows.map((task) => {
    let _rows = {}
    dataByKanban.data.rows.forEach((row) => {
      _rows[row] = task[row]

      if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: dateFormat(task[row], dateTooltipFormat),
          timeAgo: __(timeAgo(task[row])),
        }
      } else if (row == 'assigned_to') {
        _rows[row] = {
          label: task.assigned_to && getUser(task.assigned_to).full_name,
          ...(task.assigned_to && getUser(task.assigned_to)),
        }
      }
    })
    return _rows
  })
}

let listOptions = computed(() => ({
  filters: { assigned_or_owner: getUser('sessionUser').name },
}))

async function updateKanbanSettings(data){
  defaultParamsKanban.value.column_field = data.column_field
  defaultParamsKanban.value.title_field = data.title_field
  dataByKanban.params = defaultParamsKanban.value
  dataByKanban.fetch()
}

function showNewTaskDialog() {
  newTaskDialog.value.show({
    defaults: {
      assigned_to: getUser('sessionUser').name,
    },
    onSuccess: () => {
      let tasks = getCachedListResource(['Tasks', listOptions.value])
      if (tasks) {
        tasks.reload()
      }
    },
  })
}

function onShowTaskDetail(itemName, titleField){
  let itemFilter = rows.value?.find((row) => row.name == itemName)
  if(itemFilter != null){
    let taskInfo = itemFilter
    showTask(taskInfo)
  }
}

function getRow(name, field) {
  function getValue(value) {
    if (value && typeof value === 'object') {
      return value
    }
    return { label: value }
  }
  return getValue(rows.value?.find((row) => row.name == name)[field])
}

function onChangeTypeView(view){
  viewTask.value = view
}

function showTask(row){
  if(row.project != null && row.team != null){
    router.push({
      name: 'ProjectTaskDetail',
      params: { teamId: row.team, projectId: row.project, taskId: row.name }
    })
  }else{
    router.push({
      name: 'Task',
      params: { taskId: row.name }
    })
  }
}

function createTask(column){
  let objDefault = {
    assigned_to: getUser('sessionUser').name
  }
  objDefault[dataByKanban.data.column_field] = column.column.name
  newTaskDialog.value.show({
    defaults: objDefault,
    onSuccess: () => {
      createToast({
        title: __('Add successfully task'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      dataByKanban.fetch()
    },
  })
}

function updateKanban(data){
  if(data.item != null && data.item != "" && data.to != null && data.to != ""){
    let objSubmit = { name: data.item }
    objSubmit[defaultParamsKanban.value.column_field] = data.to
    tasksListResource.setValue.submit(objSubmit)
  }
}

function onUpdateAssign(data){
  let objSubmit = { name: data.id_task, assigned_to: data.user_id }
  tasksListResource.setValue.submit(objSubmit)
}



function actions(name) {
  return [
    {
      label: __('Delete'),
      icon: 'trash-2',
      onClick: () => {
        showDialogDelete.value = true
        nameTaskDelete.value = name
      },
    },
  ]
}

function onConfirmDeleteTask(){
  deleteTaskResource.submit({name: nameTaskDelete.value})
  showDialogDelete.value = false
}

function readOnlyByRole(){
  let role = getRoleByUser(null, null)
  if(role == "guest") return true
  return false
}

usePageMeta(() => {
  return {
    title: __('My Tasks'),
  }
})
</script>
