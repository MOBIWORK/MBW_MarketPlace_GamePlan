<template>
    <NestedPopover>
        <template #target>
            <Button :label="__('Sort')" ref="sortButtonRef">
                <template #prefix>
                    <SortIcon class="h-4" />
                </template>
                <template v-if="sortValues?.length" #suffix>
                    <div
                        class="flex h-5 w-5 items-center justify-center rounded bg-gray-900 pt-[1px] text-2xs font-medium text-white">
                        {{ sortValues.length }}
                    </div>
                </template>
            </Button>
        </template>
        <template #body="{ close }">
            <div class="my-2 rounded-lg border border-gray-100 bg-white shadow-xl">
                <div class="min-w-[352px] p-2">
                    <div v-if="sortValues?.length" id="sort-list" class="mb-3 flex flex-col gap-2">
                        <div v-for="(sort, i) in sortValues" :key="sort.fieldname" class="flex items-center gap-2">
                            <div class="handle flex h-7 w-7 items-center justify-center">
                                <DragIcon class="h-4 w-4 cursor-grab text-gray-600" />
                            </div>
                            <Select class="!w-32" :options="fields" v-model="sort.fieldname" @change="(e) => {
                                        sort.fieldname = e.target.value
                                        apply()
                                    }"/>
                            <FormControl class="!w-32" type="select" v-model="sort.direction" :options="[
                                { label: __('Ascending'), value: 'asc' },
                                { label: __('Descending'), value: 'desc' },
                            ]" @change="(e) => {
                                        sort.direction = e.target.value
                                        apply()
                                    }
                                    " :placeholder="__('Ascending')" />
                            <Button variant="ghost" icon="x" @click="removeSort(i)" />
                        </div>
                    </div>
                    <div v-else class="mb-3 flex h-7 items-center px-3 text-sm text-gray-600">
                        {{ __('Empty - Choose a field to sort by') }}
                    </div>
                    <div class="flex items-center justify-between gap-2">
                        <Autocomplete :options="fields" v-model="fieldSelect">
                            <template #target="{ togglePopover }">
                                <Button class="!text-gray-600" variant="ghost" @click="togglePopover()"
                                    :label="__('Add Sort')">
                                    <template #prefix>
                                        <FeatherIcon name="plus" class="h-4" />
                                    </template>
                                </Button>
                            </template>
                        </Autocomplete>
                        <Button v-if="sortValues?.length" class="!text-gray-600" variant="ghost"
                            :label="__('Clear Sort')" @click="clearSort(close)" />
                    </div>
                </div>
            </div>
        </template>
    </NestedPopover>
</template>

<script setup>
import NestedPopover from '@/components/NestedPopover.vue'
import SortIcon from '@/components/icons/SortIcon.vue'
import DragIcon from '@/components/icons/DragIcon.vue'
import { useSortable } from '@vueuse/integrations/useSortable'
import { computed, ref, nextTick, onMounted, watch } from 'vue'
import {
    Select,
    FormControl,
    Button,
    FeatherIcon,
    Autocomplete
} from 'frappe-ui'

const props = defineProps({
    fields: {
        type: Array
    }
})

const emit = defineEmits(['update'])

const sortButtonRef = ref(null)
let sortValues = ref([])
let fieldSelect = ref("")

const sortSortable = useSortable('#sort-list', sortValues, {
  handle: '.handle',
  animation: 200,
  onEnd: () => apply(),
})

function addSort(item) {
    sortValues.value.push({ fieldname: item.value, direction: 'asc' })
    restartSort()
    apply()
}

function clearSort(close) {
    sortValues.value = []
    apply()
    close()
}

function removeSort(index) {
    sortValues.value.splice(index, 1)
    apply()
}

function apply() {
    nextTick(() => {
        emit('update', convertToString(sortValues.value))
    })
}

function convertToString(values) {
    let _sortValues = ''
    values.forEach((f) => {
        _sortValues += `${f.fieldname} ${f.direction}, `
    })
    _sortValues = _sortValues.slice(0, -2)
    return _sortValues
}

function restartSort() {
  sortSortable.stop()
  sortSortable.start()
}

watch(fieldSelect, async (newFieldSelect, oldFieldSelect) => {
    if(newFieldSelect != null) addSort(newFieldSelect)
})

</script>