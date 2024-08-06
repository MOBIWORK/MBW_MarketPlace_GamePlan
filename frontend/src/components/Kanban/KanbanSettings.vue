<template>
    <Button :label="__('Kanban Settings')" @click="showDialog = true" v-bind="$attrs">
        <template #prefix>
            <KanbanIcon class="h-4" />
        </template>
    </Button>
    <Dialog v-model="showDialog" :options="{ title: __('Kanban Settings') }">
        <template #body-content>
            <div>
                <div class="text-base text-gray-800 mb-2">{{ __('Column Field') }}</div>
                <Autocomplete value="" :options="props.columnFields" @change="(f) => onChangeColumnField(f)">
                    <template #target="{ togglePopover }">
                        <Button class="w-full !justify-start" variant="subtle" @click="togglePopover()"
                            :label="columnField != null ? columnField.label : __('Select Column Field')" />
                    </template>
                </Autocomplete>
                <div class="text-base text-gray-800 mb-2 mt-4">
                    {{ __('Title Field') }}
                </div>
                <Autocomplete value="" :options="props.titleFields" @change="(f) => onChangeTitleField(f)">
                    <template #target="{ togglePopover }">
                        <Button class="w-full !justify-start" variant="subtle" @click="togglePopover()"
                            :label="titleField != null ? titleField.label : __('Select Title Field')" />
                    </template>
                </Autocomplete>
            </div>
        </template>
        <template #actions>
            <Button class="w-full" variant="solid" @click="apply" :label="__('Apply')" />
        </template>
    </Dialog>
</template>
<script setup>
import DragVerticalIcon from '@/components/icons/DragVerticalIcon.vue'
import KanbanIcon from '@/components/icons/KanbanIcon.vue'
import Autocomplete from '@/components/frappe-ui/Autocomplete.vue'
import { Dialog, createResource } from 'frappe-ui'
import { ref, nextTick } from 'vue'

const props = defineProps({
    columnFields: {
        type: Array,
        required: true
    },
    titleFields: {
        type: Array,
        required: true
    },
    columnFieldDefault: {
        type: String
    },
    titleFieldDefault: {
        type: String
    }
})

const emit = defineEmits(['update'])

const showDialog = ref(false)
const columnField = ref(props.columnFieldDefault)
const titleField = ref(props.titleFieldDefault)

function onChangeColumnField(field){
    columnField.value = field
}
function onChangeTitleField(field){
    titleField.value = field
}

function apply() {
    nextTick(() => {
        showDialog.value = false
        emit('update', {
            column_field: columnField.value.fieldname,
            title_field: titleField.value.fieldname
        })
    })
}
</script>
