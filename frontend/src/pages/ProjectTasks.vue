<template>
  <div class="py-6" v-if="typeView == 'list'">
    <TaskList :listOptions="listOptions" :groupByStatus="true" />
  </div>
  <div class="pt-6" style="height: calc(100% - 49px);" v-if="typeView == 'kanban'">
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
import { computed, ref } from 'vue'
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
  Avatar
} from 'frappe-ui'
import router from '@/router'
import { getUser } from '@/data/users'

const props = defineProps({
  project: {
    type: Object,
    required: true,
  },
  typeView: {
    type: String
  },
  paramKanbanDefault: {
    type: Object
  }
})

let dataByKanban = createResource({
  url: "gameplan.api.get_data_kanban",
  method: 'GET',
  params: props.paramKanbanDefault,
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
}))

let newTaskDialog = ref(null)
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
    objSubmit[props.paramKanbanDefault.column_field] = data.to
    tasksListResource.setValue.submit(objSubmit)
  }
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

</script>
