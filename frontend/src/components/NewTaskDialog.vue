<template>
  <Dialog
    :options="{
      title: __('New Task'),
      actions: [
        {
          label: __('Create'),
          variant: 'solid',
          onClick: onCreateClick,
        },
      ],
    }"
    v-model="showDialog"
    @after-leave="newTask = initialData"
  >
    <template #body-content>
      <div class="space-y-4">
        <FormControl :label="__('Title')" v-model="newTask.title" autocomplete="off" />
        <FormControl
          :label="__('Description')"
          type="textarea"
          v-model="newTask.description"
        />
        <div class="flex space-x-2">
          <div>
            <div class="mb-1.5 text-sm text-gray-600">{{ __('Status') }}</div>
            <Dropdown
            :options="
              statusOptions({
                onClick: (status) => (newTask.status = status),
              })
            "
          >
            <Button class="w-32" style="justify-content: start !important;"> 
              <template #prefix>
                <TaskStatusIcon :status="newTask.status" />
              </template>
              {{ newTask.status }}
            </Button>
          </Dropdown>
          </div>
          <div>
            <div class="mb-1.5 text-sm text-gray-600">{{ __('Due date') }}</div>
            <DateTimePicker class="datepicker"
                icon-left="calendar"
                :value="newTask.due_date"
                @change="(val) => (newTask.due_date = val)"
                :placeholder="__('Set due date')"
                input-class="border-none" />
          </div>
          <div>
            <div class="mb-1.5 text-sm text-gray-600">{{ __('Assign to') }}</div>
            <Autocomplete
              :placeholder="__('Assign a user')"
              :options="assignableUsers"
              v-model="newTask.assigned_to"
              @update:modelValue="onChangeUserAssign"

            />
          </div>
        </div>
        <div class="flex items-end">
          <div class="mr-3 w-1/3">
            <div class="mb-1.5 text-sm text-gray-600">{{ __('Reminder') }}</div>
            <TextInput
              :type="'number'"
              size="sm"
              variant="subtle"
              placeholder="Nhập thời gian nhắc nhở"
              v-model="newTask.remind_times"
            />
          </div>
          <div class="mr-3 w-1/3">
            <Select
              :placeholder="'Chọn đơn vị'"
              :options="[
                {
                  label: 'minutes',
                  value: 'minute',
                },
                {
                  label: 'hours',
                  value: 'hour',
                },
                {
                  label: 'days',
                  value: 'day',
                }
              ]"
              v-model="newTask.remind_unit"
            />
          </div>
          <div class="mr-3">
            <Checkbox
              size="sm"
              :value="false"
              v-model="newTask.notify_browser"
              label="Browser"
            />
          </div>
          <div>
            <Checkbox
              size="sm"
              :value="false"
              v-model="newTask.notify_email"
              label="Email"
            />
          </div>
        </div>
        <ErrorMessage class="mt-2" :message="createTask.error" />
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import { ref, computed, h } from 'vue'
import {
  Dialog,
  FormControl,
  Autocomplete,
  Dropdown,
  TextInput,
  createResource,
  DatePicker,
  Select,
  Checkbox
} from 'frappe-ui'
import TaskStatusIcon from './icons/TaskStatusIcon.vue'
import { activeUsers } from '@/data/users'
import DateTimePicker from '@/components/Controls/DateTimePicker.vue'

const props = defineProps(['modelValue', 'defaults'])
const emit = defineEmits(['update:modelValue'])
const showDialog = ref(false)
const createTask = createResource({
  url: 'frappe.client.insert',
  makeParams(values) {
    return {
      doc: {
        doctype: 'GP Task',
        ...values,
      },
    }
  },
})
const initialData = {
  title: '',
  description: '',
  status: 'Backlog',
  assigned_to: null,
  project: null,
  remind_times: '30',
  remind_unit: 'minute'
}

const newTask = ref(initialData)

function statusOptions({ onClick }) {
  return ['Backlog', 'Todo', 'In Progress', 'Done', 'Canceled'].map(
    (status) => {
      return {
        icon: () => h(TaskStatusIcon, { status }),
        label: status,
        onClick: () => onClick(status),
      }
    }
  )
}

function onChangeUserAssign(option){
  newTask.value.assigned_to = option?.value || '';
}

const assignableUsers = computed(() => {
  return activeUsers.value
    //.filter((user) => user.name != newTask.value.assigned_to)
    .map((user) => ({
      label: user.full_name,
      value: user.name,
    }))
})

let _onSuccess
function show({ defaults, onSuccess } = {}) {
  newTask.value = { ...initialData, ...(defaults || {}) }
  showDialog.value = true
  _onSuccess = onSuccess
}

function onCreateClick(close) {
  createTask
    .submit(newTask.value, {
      validate() {
        if (!newTask.value.title) {
          return __('Task title is required')
        }
      },
      onSuccess: _onSuccess,
    })
    .then(close)
}

defineExpose({ show })
</script>
