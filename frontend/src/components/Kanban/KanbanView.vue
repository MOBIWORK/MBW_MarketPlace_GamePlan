<template>
    <div class="flex overflow-x-auto" style="height:100%;">
        <Draggable v-if="columns" :list="columns" item-key="column" @end="updateColumn"
            :delay="isTouchScreenDevice() ? 200 : 0" class="flex sm:mx-2.5 mx-2 pb-3.5">
            <template #item="{ element: column }">
                <div v-if="!column.column.delete"
                    class="flex flex-col gap-2.5 min-w-72 w-72 bg-gray-100 rounded-lg p-2.5 mr-4">
                    <div class="flex gap-2 items-center group justify-between">
                        <div class="flex items-center text-base">
                            <NestedPopover>
                                <template #target>
                                    <Button variant="ghost" size="sm" class="hover:!bg-gray-100">
                                        <IndicatorIcon :class="colorClasses(column.column.color, true)" />
                                    </Button>
                                </template>
                                <template #body="{ close }">
                                    <div
                                        class="flex flex-col gap-3 px-3 py-2.5 rounded-lg border border-gray-100 bg-white shadow-xl">
                                        <div class="flex gap-1">
                                            <Button :class="colorClasses(color)" variant="ghost" v-for="color in colors"
                                                :key="color" @click="() => (column.column.color = color)">
                                                <IndicatorIcon />
                                            </Button>
                                        </div>
                                        <div class="flex flex-row-reverse">
                                            <Button variant="solid" :label="__('Apply')" @click="updateColumn" />
                                        </div>
                                    </div>
                                </template>
                            </NestedPopover>
                            <div>{{ column.column.name }}</div>
                            <div class="ml-1 text-sm">({{column.column.count}})</div>
                        </div>
                        <div class="flex">
                            <Dropdown :options="actions(column)">
                                <template #default>
                                    <Button class="hidden group-hover:flex" icon="more-horizontal" variant="ghost" />
                                </template>
                            </Dropdown>
                            <Button icon="plus" variant="ghost" @click="options.onNewClick(column)" />
                        </div>
                    </div>
                    <div class="overflow-y-auto flex flex-col gap-2 h-full overflow-customize">
                        <Draggable :list="column.data" group="fields" item-key="name"
                            class="flex flex-col gap-3.5 flex-1" @end="updateColumn"
                            :delay="isTouchScreenDevice() ? 200 : 0" :data-column="column.column.name">
                            <template #item="{ element: fields }">
                                <component :is="options.getRoute ? 'router-link' : 'div'"
                                    class="pt-3 px-3.5 pb-2.5 rounded-lg border bg-white text-base flex flex-col"
                                    :data-name="fields.name" v-bind="{
                                        to: options.getRoute ? options.getRoute(fields) : undefined
                                    }">
                                    <slot name="title" v-bind="{ fields, titleField, itemName: fields.name }">
                                        <div class="h-5 flex items-center">
                                            <div v-if="fields[titleField]">
                                                {{ fields[titleField] }}
                                            </div>
                                            <div class="text-gray-500" v-else>
                                                {{ __('No Title') }}
                                            </div>
                                        </div>
                                    </slot>
                                    <div class="border-b h-px my-2.5" />

                                    <div class="flex flex-col gap-3.5">
                                        <div class="truncate text-base max-h-44" v-if="fields['description'] != null && fields['description'] != ''">
                                            <TextEditor
                                                :content="fields['description']"
                                                :editable="false"
                                                editor-class="!prose-sm max-w-none focus:outline-none"
                                                class="flex-1 overflow-hidden"
                                            />
                                        </div>
                                        <div class="flex justify-start" v-if="fields['priority'] != null && fields['priority'] != ''">
                                            <Popover>
                                                <template #target="{ togglePopover }">
                                                    <div
                                                        class="rounded-full py-1 px-2 text-sm cursor-pointer"
                                                        :class="{
                                                            'bg-red-500 text-white': fields['priority'] === 'High',
                                                            'bg-yellow-500 text-black': fields['priority'] === 'Medium',
                                                            'bg-gray-300 text-black': fields['priority'] === 'Low',
                                                        }"
                                                        @click="togglePopover()"
                                                    >{{fields['priority']}}</div>
                                                </template>
                                                <template #body-main="{ togglePopover }">
                                                    <div class="p-2">
                                                        <div class="text-gray-800 group flex h-7 w-full items-center rounded px-2 text-base hover:bg-gray-100" 
                                                            @click="() => {fields['priority']='Low'; onChangePriority(fields.name, 'Low'); togglePopover();}">
                                                            <div class="grid place-items-center mr-2 h-4 w-4 flex-shrink-0 text-gray-700">
                                                                <div class="h-3 w-3 rounded-full bg-gray-300"></div>
                                                            </div>
                                                            <span class="whitespace-nowrap">{{__('Low')}}</span>
                                                        </div>
                                                        <div class="text-gray-800 group flex h-7 w-full items-center rounded px-2 text-base hover:bg-gray-100" 
                                                            @click="() => {fields['priority']='Medium'; onChangePriority(fields.name, 'Medium'); togglePopover();}">
                                                            <div class="grid place-items-center mr-2 h-4 w-4 flex-shrink-0 text-gray-700">
                                                                <div class="h-3 w-3 rounded-full bg-yellow-500"></div>
                                                            </div>
                                                            <span class="whitespace-nowrap">{{__('Medium')}}</span>
                                                        </div>
                                                        <div class="text-gray-800 group flex h-7 w-full items-center rounded px-2 text-base hover:bg-gray-100" 
                                                            @click="() => {fields['priority']='High'; onChangePriority(fields.name, 'High'); togglePopover();}">
                                                            <div class="grid place-items-center mr-2 h-4 w-4 flex-shrink-0 text-gray-700">
                                                                <div class="h-3 w-3 rounded-full bg-red-500"></div>
                                                            </div>
                                                            <span class="whitespace-nowrap">{{__('High')}}</span>
                                                        </div>
                                                    </div>
                                                </template>
                                            </Popover>
                                        </div>
                                        <div class="flex items-center justify-between">
                                            <div class="flex items-center" :class="{'text-red-600': checkDeadLine(fields['due_date'], fields['status']) == true}">
                                                <FeatherIcon name="briefcase" class="w-4 mr-1" v-if="fields['due_date'] != null && fields['due_date'] != ''" />
                                                <div class="text-sm" v-if="fields['due_date'] != null && fields['due_date'] != ''">{{renderDateText(fields['due_date'])}}</div>
                                            </div>
                                            <div class="flex items-center">
                                                <FeatherIcon name="message-circle" class="w-4 mr-1 text-gray-700 cursor-pointer" v-if="fields['comments_count'] > 0" @click="onEnteringComment(fields)"/>
                                                <div class="mr-2 text-gray-700 text-sm cursor-pointer" v-if="fields['comments_count'] > 0" @click="onEnteringComment(fields)">{{fields['comments_count']}}</div>
                                                <!-- <UserAvatar :user="fields['assigned_to']" size="md" v-if="fields['assigned_to'] != null && fields['assigned_to'] != ''" /> -->
                                                <Dropdown class="cursor-pointer"
                                                    :options="
                                                        assignOptions({
                                                            onClick: (assign) => {fields['assigned_to'] = assign; emit('update_assign_task', {'id_task': fields['name'], 'user_id': assign})}
                                                        })
                                                    "
                                                >
                                                    <UserAvatar :user="fields['assigned_to']" size="md" v-if="fields['assigned_to'] != null && fields['assigned_to'] != ''" />
                                                </Dropdown>
                                            </div>
                                        </div>
                                    </div>
                                </component>
                            </template>
                        </Draggable>
                        <!-- <div v-if="column.column.count < column.column.all_count"
                            class="flex items-center justify-center">
                            <Button :label="__('Load More')" @click="emit('loadMore', column.column.name)" />
                        </div> -->
                    </div>
                </div>
            </template>
        </Draggable>
        <div v-if="deletedColumns.length" class="shrink-0 min-w-64">
            <Autocomplete value="" :options="deletedColumns" @change="(e) => addColumn(e)">
                <template #target="{ togglePopover }">
                    <Button class="w-full mt-2.5 mb-1 mr-5" @click="togglePopover()" :label="__('Add Column')">
                        <template #prefix>
                            <FeatherIcon name="plus" class="h-4" />
                        </template>
                    </Button>
                </template>
            </Autocomplete>
        </div>
    </div>
</template>
<script setup>
import Autocomplete from '@/components/frappe-ui/Autocomplete.vue'
import NestedPopover from '@/components/NestedPopover.vue'
import IndicatorIcon from '@/components/icons/IndicatorIcon.vue'
import { isTouchScreenDevice } from '@/utils'
import Draggable from 'vuedraggable'
import { Dropdown, FeatherIcon, Avatar, Popover } from 'frappe-ui'
import { computed, ref } from 'vue'
import router from '@/router'
import { activeUsers } from '@/data/users'

const props = defineProps({
    options: {
        type: Object,
        default: () => ({
            getRoute: null,
            onNewClick: null,
        }),
    },
    kanban: {
        type: Object
    }
})

const emit = defineEmits(['update', 'loadMore', 'update_assign_task', 'update_property'])

const titleField = computed(() => {
    return props.kanban.data?.title_field
})

const columns = computed(() => {
    let _columns = props.kanban.data? props.kanban.data.data : []

    let has_color = _columns.some((column) => column.column?.color)
    if (!has_color) {
        _columns.forEach((column, i) => {
            column.column['color'] = colors[i % colors.length]
        })
    }
    return _columns
})



const assignableUsers = computed(() => {
  return activeUsers.value
    .map((user) => ({
      label: user.full_name,
      value: user.name
    }))
})

function assignOptions({ onClick }) {
  return activeUsers.value.map(
    (user) => {
      return {
        label: user.full_name,
        value: user.name,
        onClick: () => onClick(user.name),
      }
    }
  )
}

const deletedColumns = computed(() => {
    return columns.value
        .filter((col) => col.column['delete'])
        .map((col) => {
            return { label: col.column.name, value: col.column.name }
        })
})

function renderDateText(dateText){
    const date = new Date(dateText)
    const day = String(date.getDate()).padStart(2, '0')
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const year = date.getFullYear()
    return `${day}/${month}/${year}`
}

function checkDeadLine(dateText, status){
    const date = new Date(dateText)
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if(date <= today && status != 'Done') return true
    else return false
}

function onEnteringComment(taskInfo){
    if(taskInfo.project != null && taskInfo.team != null){
    router.push({
      name: 'ProjectTaskDetail',
      params: { teamId: taskInfo.team, projectId: taskInfo.project, taskId: taskInfo.name }
    })
  }else{
    router.push({
      name: 'Task',
      params: { taskId: taskInfo.name }
    })
  }
}

function actions(column) {
    return [
        {
            group: __('Options'),
            hideLabel: true,
            items: [
                {
                    label: __('Delete'),
                    icon: 'trash-2',
                    onClick: () => {
                        column.column['delete'] = true
                        updateColumn()
                    },
                },
            ],
        },
    ]
}

function addColumn(e) {
    let column = columns.value.find((col) => col.column.name == e.value)
    column.column['delete'] = false
    updateColumn()
}

function updateColumn(d) {
    let toColumn = d?.to?.dataset.column
    let fromColumn = d?.from?.dataset.column
    let itemName = d?.item?.dataset.name

    let _columns = []
    columns.value.forEach((col) => {
        col.column['order'] = col.data.map((d) => d.name)
        if (col.column.page_length) {
            delete col.column.page_length
        }
        _columns.push(col.column)
    })

    let data = { kanban_columns: _columns }

    if (toColumn != fromColumn) {
        data = { item: itemName, to: toColumn, kanban_columns: _columns }
    }
    if(d.type == "end"){
        for(let i = 0; i < columns.value.length; i++){
            if(columns.value[i].column.name == toColumn){
                for(let j = 0; j < columns.value[i].data.length; j++){
                    if(columns.value[i].data[j].name == itemName){
                        columns.value[i].data[j].status = toColumn
                        break
                    }
                }
            }
        }
    }
    emit('update', data)
}

function colorClasses(color, onlyIcon = false) {
    let textColor = `!text-${color}-600`
    if (color == 'black') {
        textColor = '!text-gray-900'
    } else if (['gray', 'green'].includes(color)) {
        textColor = `!text-${color}-700`
    }

    let bgColor = `!bg-${color}-200 active:!bg-${color}-300`

    return [textColor, onlyIcon ? '' : bgColor]
}

const colors = [
    'gray',
    'blue',
    'green',
    'red',
    'pink',
    'orange',
    'amber',
    'yellow',
    'cyan',
    'teal',
    'violet',
    'purple',
    'black',
]

function onChangePriority(name, priority){
    let property_update = {
        'name': name,
        'priority': priority
    }
    emit('update_property', property_update)
}

</script>
<style scoped>
    .overflow-customize{
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
    }
    .overflow-customize::-webkit-scrollbar{
        display: none !important;
    }
</style>