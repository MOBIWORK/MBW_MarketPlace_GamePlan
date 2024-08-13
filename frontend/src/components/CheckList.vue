<template>
    <div class="w-full flex justify-between">
        <div class="flex items-center">
            <div class="text-1xl font-semibold mr-2">{{__('Checklists')}}</div>
            <div class="w-6 h-6 rounded-full p-2 bg-gray-200 text-sm flex justify-center items-center text-gray-800">
                {{numCheckList}}
            </div>
        </div>
        <div class="flex items-center" v-if="!readOnly">
            <Button class="mr-2" :variant="'outline'" theme="red" size="sm" :loading="false" @click="onDeleteAll()" v-if="numCheckList > 0">{{__('Delete all')}}</Button>
            <Button :variant="'outline'" theme="gray" size="sm" :loading="false" @click="onAddChecklist()">{{__('Add checklist')}}</Button>
        </div>
    </div>
    <div v-if="showFrmAddingChecklist">
        <div class="w-full mt-3 mb-2">
            <TextInput
                :type="'text'"
                size="sm"
                variant="outline"
                :placeholder="__('Add new checklist')"
                v-model="txtNewChecklist"
            />
        </div>
        <div class="flex items-center justify-end">
            <Button :variant="'outline'" theme="gray" size="sm" class="mr-2" @click="onCancelAddingChecklist()">{{__('Cancel')}}</Button>
            <Button :variant="'solid'" theme="gray" size="sm" @click="onSaveAddingChecklist()">{{__('Save')}}</Button>
        </div>
    </div>
    <div class="w-full mt-3" v-if="numCheckList > 0">
        <Progress
            size="md"
            :value="valProgress"
        />
    </div>
    <div class="w-full mt-3" v-if="numCheckList > 0">
        <div class="flex items-start justify-between mb-3" v-for="checklist in arrCheckList">
            <div class="flex items-start w-full">
                <Checkbox :id="checklist.name" size="md" v-model="checklist.is_check" :disabled="checklist.is_check || readOnly"
                     class="mr-2" v-on:change="() => onClickBox(checklist)" />
                <div class="text-base">{{checklist.label}}</div>
            </div>
            <div style="width: 4.7rem;" class="flex items-start">
                <UserAvatar :user="checklist.owner" class="mx-3" />
                <Button variant="outline" @click="onDeleteChecklist(checklist)" style="width: 2rem !important;" v-if="!readOnly">
                    <template #icon>
                        <LucideTrash2 class="w-4" />
                    </template>
                </Button>
            </div>
        </div>
    </div>
    <Dialog
        :options="{
            title: __('Delete all checklists?'),
            message: __('This action can not be undone'),
            size: 'xl',
            actions: [
                {
                    label: __('Delete'),
                    variant: 'solid',
                    theme: 'red',
                    onClick: () => onConfirmDeleteChecklists()
                }
            ],
        }"
        v-model="showDialogDeletingChecklists"
    />
    <Dialog
        :options="{
            title: __('Delete checklist?'),
            message: __('This action can not be undone'),
            size: 'xl',
            actions: [
                {
                    label: __('Delete'),
                    variant: 'solid',
                    theme: 'red',
                    onClick: () => onConfirmDeleteChecklist()
                }
            ],
        }"
        v-model="showDialogFrmDeletingChecklist"
    />
</template>
<script>
import { Button, TextInput, Checkbox, Dialog } from 'frappe-ui'
import { createToast } from '@/utils'
import Progress from '@/components/frappe-ui/Progress.vue'

export default{
    name: 'CheckList',
    props: {
        reference_name: {
            type: String
        },
        readOnly:{
            type: Boolean
        }
    },
    components: {
        Button,
        TextInput,
        Checkbox,
        Progress,
        Dialog
    },
    resources: {
        checklists(){
            return {
                type: 'list',
                doctype: 'GP CheckList',
                fields: ['name', 'label', 'is_check', 'owner'],
                orderBy: 'creation asc',
                auto: true,
                filters: {
                    'parent': this.reference_name
                },
                transform(data){
                    for(let d of data){
                        if(d.is_check == 0) d.is_check = false
                        else d.is_check = true
                    }
                    return data
                },
                onSuccess(data){
                    this.arrCheckList = data
                    this.numCheckList = data.length
                    let checks = data.filter(x => x.is_check == true)
                    if(data.length > 0){
                        this.valProgress = (checks.length/data.length)*100
                    }
                },
                insert: {
                    onSuccess(){
                        createToast({
                            title: __('Add successfully checklist'),
                            icon: 'check',
                            iconClasses: 'text-green-600'
                        })
                        this.txtNewChecklist = ""
                    },
                    onError(){
                        createToast({
                            title: __('Add failed checklist'),
                            icon: 'x',
                            iconClasses: 'text-red-600',
                        })
                    }
                },
                delete: {
                    onSuccess(){
                        createToast({
                            title: __('Delete successfully checklist'),
                            icon: 'check',
                            iconClasses: 'text-green-600'
                        })
                        this.showDialogFrmDeletingChecklist = false
                        this.nameDeletingChecklist = ""
                    },
                    onError(){
                        createToast({
                            title: __('Delete failed checklist'),
                            icon: 'x',
                            iconClasses: 'text-red-600',
                        })
                    }
                },
                setValue:{
                    onSuccess(){
                        this.$resources.checklists.fetch()
                    }
                },
                runDocMethod:{
                    onSuccess() {
                        this.$resources.checklists.fetch()
                    }
                }
            }
        },
        delete_all(){
            return {
                url: "gameplan.api.delete_all_checklist",
                method: "GET",
                params: {
                    task_id: this.reference_name
                },
                auto: false,
                onSuccess(data){
                    if(data == "ok"){
                        createToast({
                            title: __('Delete successfully checklist'),
                            icon: 'check',
                            iconClasses: 'text-green-600'
                        })
                        this.showDialogDeletingChecklists = false
                        this.$resources.checklists.fetch()
                    }else{
                        createToast({
                            title: __('Delete failed checklist'),
                            icon: 'x',
                            iconClasses: 'text-red-600',
                        })
                    }
                    
                }
            }
        }
    },
    data(){
        return {
            arrCheckList: [],
            numCheckList: 0,
            valProgress: 0,
            showFrmAddingChecklist: false,
            txtNewChecklist: "",
            nameUpdate: "",
            showDialogDeletingChecklists: false,
            showDialogFrmDeletingChecklist: false,
            nameDeletingChecklist: ""
        }
    },
    methods: {
        onDeleteAll(){
            this.showDialogDeletingChecklists = true
        },
        onAddChecklist(){
            this.showFrmAddingChecklist = true
        },
        onCancelAddingChecklist(){
            this.showFrmAddingChecklist = false
            this.txtNewChecklist = ""
        },
        onSaveAddingChecklist(){
            this.$resources.checklists.insert.submit({
                'parent': this.reference_name,
                'parentfield': "checklists",
                'parenttype': "GP Task",
                'label': this.txtNewChecklist,
                'is_check': false
            })
            this.showFrmAddingChecklist = false
        },
        onDeleteChecklist(checklist){
            this.showDialogFrmDeletingChecklist = true
            this.nameDeletingChecklist = checklist.name
        },
        onConfirmDeleteChecklist(){
            this.$resources.checklists.delete.submit(this.nameDeletingChecklist)
        },
        onClickBox(checklist){
            if(this.nameUpdate != checklist.name){
                this.$resources.checklists.setValue.submit({
                    'name': checklist.name,
                    'is_check': true
                })
                this.nameUpdate = checklist.name
            }
            
        },
        onConfirmDeleteChecklists(){
            this.$resources.delete_all.fetch()
        }
    }

}
</script>
<style scoped>
</style>