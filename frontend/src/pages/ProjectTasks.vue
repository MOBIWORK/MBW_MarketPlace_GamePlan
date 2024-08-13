<template>
  <div class="w-full pt-3 px-4 flex items-center justify-between">
        <div class="w-1/2">
          <TextInput type="text" class="w-full" :placeholder="__('Search task')" :debounce="600" v-model="txtSearch">
            <template #suffix>
              <FeatherIcon
                class="w-4"
                name="search"
              />
            </template>
          </TextInput>
        </div>
        <div class="flex items-center">
          <Dropdown :options="[
            {
              label: 'List View',
              onClick: () => onChangeTypeView('list'),
              icon: 'list'
            },
            {
              label: 'Kanban by Status',
              onClick: () => onChangeTypeView('kanban_by_status'),
              icon: 'trello'
            },
            {
              label: 'Kanban by Priority',
              onClick: () => onChangeTypeView('kanban_by_priority'),
              icon: 'trello'
            }
          ]" class="mr-3" style="font-size: 14px;">
            <Button class="px-2.5 w-full" style="justify-content: flex-start !important;">
              <template #icon>
                <FeatherIcon v-if="typeView=='list'"
                  name="list"
                  class="h-4 w-4"
                />
                <FeatherIcon v-if="typeView=='kanban_by_status' || typeView=='kanban_by_priority'"
                  name="trello"
                  class="h-4 w-4 justify-start"
                />
                <span v-if="typeView=='list'">List View</span>
                <span v-if="typeView=='kanban_by_status'">Kanban by Status</span>
                <span v-if="typeView=='kanban_by_priority'">Kanban by Priority</span>
              </template>
            </Button>
          </Dropdown>
          <SortBy :fields="[
            { value: 'due_date', label: __('Due Date') },
            { value: 'modified', label: __('Modified') },
            { value: 'creation', label: __('Creation') },
            { value: 'priority', label: __('Priority') }
          ]" @update="(data) => onUpdateSort(data)"></SortBy>
        </div>
      </div>
  <div class="pt-3 px-4" v-if="typeView == 'list'">
    <TaskList :listOptions="listOptions" :groupByStatus="true" ref="lstTask"/>
  </div>
  <div class="pt-3 pl-2" style="height: calc(100% - 90px);" v-if="typeView == 'kanban_by_status' || typeView == 'kanban_by_priority'">
    <KanbanView :kanban="dataByKanban" :options="{
      onNewClick: (column) => createTask(column),
    }" @update="(data) => updateKanban(data)" @update_assign_task="(data) => onUpdateAssign(data)">
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
    <NewTaskDialog ref="newTaskDialog" />
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
import { computed, ref, watch } from 'vue'
import KanbanView from '@/components/Kanban/KanbanView.vue'
import TaskStatusIcon from '@/components/icons/TaskStatusIcon.vue'
import TaskPriorityIcon from '@/components/icons/TaskPriorityIcon.vue'
import ArrowUpRightIcon from '@/components/icons/ArrowUpRightIcon.vue'
import { dateFormat, dateTooltipFormat, timeAgo, createToast } from '@/utils'
import {
  Dialog,
  createResource,
  createListResource,
  Dropdown,
  Avatar,
  TextInput,
  FeatherIcon,
  Button
} from 'frappe-ui'
import router from '@/router'
import { getUser } from '@/data/users'
import SortBy from '@/components/SortBy.vue'

const props = defineProps({
  project: {
    type: Object,
    required: true,
  }
})

let paramKanbanDefault = ref({
  doctype: 'GP Task',
  filters: JSON.stringify({}),
  order_by: 'modified desc',
  column_field: "status",
  title_field: "title",
  rows: JSON.stringify(["name", "title", "description", "assigned_to", "status", "priority", "project", "team"]),
  kanban_columns: JSON.stringify([{'name': "Backlog"},{'name': "Todo"},{'name': "In Progress"},{'name': "Done"},{'name': "Canceled"}]),
  kanban_fields: JSON.stringify(["description", "priority", "due_date", "comments_count", "assigned_to"]),
  text_search: "",
  is_my_task: "false"
})

let dataByKanban = createResource({
  url: "gameplan.api.get_data_kanban",
  method: 'GET',
  params: paramKanbanDefault.value,
  auto: true
})

let deleteTaskResource = createResource({
  url: "gameplan.api.delete_task_by_id",
  method: "DELETE",
  onSuccess(data) {
    if (data.status == "ok") {
      createToast({
        title: __('Delete successfully task'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      dataByKanban.fetch()
    } else {
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


let listOptions = computed(() => ({
  filters: {
    project: props.project.name,
  },
  orderBy: "creation desc"
}))

let newTaskDialog = ref(null)
let showDialogDelete = ref(false)
let nameTaskDelete = ref("")
let txtSearch = ref("")
let lstTask = ref(null)
let typeView = ref("list")

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
function getRow(name, field) {
  function getValue(value) {
    if (value && typeof value === 'object') {
      return value
    }
    return { label: value }
  }
  return getValue(rows.value?.find((row) => row.name == name)[field])
}

function onShowTaskDetail(itemName, titleField){
  let itemFilter = rows.value?.find((row) => row.name == itemName)
  if(itemFilter != null){
    let taskInfo = itemFilter
    router.push({
      name: 'ProjectTaskDetail',
      params: { teamId: taskInfo.team, projectId: taskInfo.project, taskId: taskInfo.name }
    })
  }
}

function createTask(column) {
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

function onUpdateAssign(data){
  let objSubmit = { name: data.id_task, assigned_to: data.user_id }
  tasksListResource.setValue.submit(objSubmit)
}

function updateKanban(data) {
  if (data.item != null && data.item != "" && data.to != null && data.to != "") {
    let objSubmit = { name: data.item }
    objSubmit[paramKanbanDefault.value.column_field] = data.to
    tasksListResource.setValue.submit(objSubmit)
  }
}

function onReloadData(){
  if(typeView.value == "list"){
    lstTask.value.onReloadTasks()
  } 
  else dataByKanban.fetch()
}

function onChangeTypeView(view){
  if(view == "kanban_by_status"){
    paramKanbanDefault.value.column_field = "status"
    dataByKanban.fetch()
  }else if(view == "kanban_by_priority"){
    paramKanbanDefault.value.column_field = "priority"
    dataByKanban.fetch()
  }
  typeView.value = view
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

function onConfirmDeleteTask() {
  deleteTaskResource.submit({ name: nameTaskDelete.value })
  showDialogDelete.value = false
}

function onUpdateSort(querySort){
  paramKanbanDefault.value.order_by = querySort != null && querySort != ""? querySort : "creation desc"
  listOptions.value['orderBy'] = querySort != null && querySort != ""? querySort : "creation desc"
  if(typeView.value == "list"){
    lstTask.value.onReloadTasks()
  } 
  else dataByKanban.fetch()
}

watch(txtSearch, async(newSearch, oldSearch) => {
  paramKanbanDefault.value.text_search = txtSearch.value
  listOptions.value.filters['title'] = ['like', `%${txtSearch.value}%`]
  if(typeView.value == "list"){
    lstTask.value.onReloadTasks()
  } 
  else dataByKanban.fetch()
})

defineExpose({ onReloadData })

</script>
