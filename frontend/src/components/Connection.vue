<template>
    <div class="w-full flex justify-between">
        <div class="flex items-center">
            <div class="text-1xl font-semibold mr-2">{{__('Connection')}}</div>
            <div class="w-6 h-6 rounded-full p-2 bg-gray-200 text-sm flex justify-center items-center text-gray-800">
                {{num_connection}}
            </div>
        </div>
        <div class="flex items-center" v-if="!readOnly">
            <Button class="mr-2" :variant="'outline'" theme="red" size="sm" :loading="false" @click="onDeleteAll()">{{__('Delete all')}}</Button>
            <Button :variant="'outline'" theme="gray" size="sm" :loading="false" @click="onAddConnection()">{{__('New connection')}}</Button>
        </div>
    </div>
    <div v-if="show_adding_connection">
        <div class="flex items-center mb-1 mt-3">
            <Select :options="[
                {
                    label: 'Task',
                    value: 'GP Task'
                },{
                    label: 'Discussion',
                    value: 'GP Discussion'
                },{
                    label: 'Page',
                    value: 'GP Page'
                }
            ]" variant="outline" v-model="reference_doctype_select" size="sm" class="mr-2" style="width: 8rem !important;">
            </Select>
            <div class="w-full">
                <Select :options="datas_reference_name" variant="outline" v-model="reference_name_select" size="sm"></Select>
            </div>
        </div>
        <div class="flex items-center justify-end">
            <Button :variant="'outline'" theme="gray" size="sm" class="mr-2" @click="onCancelAddingConnection()">{{__('Cancel')}}</Button>
            <Button :variant="'solid'" theme="gray" size="sm" @click="onSaveAddingConnection()">{{__('Save')}}</Button>
        </div>
    </div>
    <Dialog
        :options="{
            title: __('Delete all connection?'),
            message: __('This action can not be undone'),
            size: 'xl',
            actions: [
                {
                    label: __('Delete'),
                    variant: 'solid',
                    theme: 'red',
                    onClick: () => onConfirmDeleteConnections()
                }
            ],
        }"
        v-model="show_confirm_deleteing"
    />
    <div class="flex items-center mt-3" v-for="connection in connections">
        <TextInput :type="'text'" size="sm" variant="outline" :readonly="true" :value="onRenderValueDoctype(connection)" 
            class="mr-2" style="width: 8rem !important;color:rgb(37 99 235) !important;"/>
        <TextInput :type="'text'" size="sm" variant="outline" :readonly="true" :value="connection.title_destination" 
            class="w-full cursor-pointer hover:bg-gray-200" @click="onLinkConnection($event, connection)"/>
        <Button variant="outline" @click="onDeleteConnection(connection)" style="width: 2rem !important;" class="ml-2" v-if="!readOnly">
            <template #icon>
                <LucideTrash2 class="w-4" />
            </template>
        </Button>
    </div>
</template>
<script>
import { Button, TextInput, Tooltip, Select, Dialog } from 'frappe-ui'
import { createToast } from '@/utils'

export default {
    name: 'Connection',
    props: {
        reference_doctype: {
            type: String
        },
        reference_name: {
            type: String
        },
        project: {
            type: String
        },
        readOnly: {
            type: Boolean
        }
    },
    data() {
        return {
            num_connection: 0,
            connections: [],
            show_adding_connection: false,
            reference_doctype_select: "GP Task",
            reference_name_select: "",
            datas_reference_name: [],
            show_confirm_deleteing: false
        }
    },
    components: {
        Button,
        TextInput,
        Tooltip,
        Select,
        Dialog
    },
    resources: {
        connections() {
            return {
                type: 'list',
                doctype: 'GP Connection',
                fields: ['name','reference_type_source','reference_name_source','reference_type_destination','reference_name_destination'],
                auto: false,
                delete: {
                    onSuccess(){
                        this.$resources.lst_connection.fetch()
                    }
                },
                insert: {
                    onSuccess(){
                        this.$resources.lst_connection.fetch()
                    }
                }
            }
        },
        lst_connection(){
            return {
                url: 'gameplan.api.get_connections',
                method: 'GET',
                params: {
                    reference_doctype: this.reference_doctype,
                    reference_name: this.reference_name
                },
                auto: true,
                onSuccess(data){
                    this.num_connection = data.length
                    this.connections = data
                }
            }
        },
        values_by_reference(){
            return {
                url: 'gameplan.api.get_value_by_reference_doctype',
                method: 'GET',
                params: {
                    reference_doctype: this.reference_doctype_select,
                    project: this.project != null && this.project != ""? this.project : ""
                },
                auto: true,
                onSuccess(data){
                    this.datas_reference_name = data
                }
            }
        },
        delete_connections(){
            return {
                url: 'gameplan.api.delete_connections',
                method: 'GET',
                params: {
                    reference_doctype: this.reference_doctype,
                    reference_name: this.reference_name
                },
                auto: false,
                onSuccess(data){
                    if(data == "ok"){
                        createToast({
                            title: __('Delete successfully link'),
                            icon: 'check',
                            iconClasses: 'text-green-600'
                        })
                        this.num_connection = 0
                        this.connections = []
                    }else{
                        createToast({
                            title: __('Delete failed link'),
                            icon: 'x',
                            iconClasses: 'text-red-600',
                        })
                    }
                }
            }
        }
    },
    methods: {
        onDeleteAll(){
            this.show_confirm_deleteing = true
        },
        onAddConnection(){
            this.show_adding_connection = true
        },
        onDeleteConnection(connection){
            this.$resources.connections.delete.submit(connection.name)
        },
        onLinkConnection(event, connection){
            event.stopPropagation()
            if(connection.doctype_destination == "GP Discussion"){
                this.$router.push({
                    name: 'ProjectDiscussion',
                    params: {
                        teamId: connection.team_destination,
                        projectId: connection.project_destination,
                        postId: connection.name_destination,
                    }
                })
            }else if(connection.doctype_destination == "GP Page"){
                if(connection.project_destination != null && connection.project_destination != ""){
                    this.$router.push({
                        name: 'ProjectPage',
                        params: {
                            teamId: connection.team_destination,
                            projectId: connection.project_destination,
                            pageId: connection.name_destination
                        }
                    })
                }else{
                    this.$router.push({
                        name: 'Page',
                        params: {
                            pageId: connection.name_destination
                        }
                    })
                }
            }else if(connection.doctype_destination == "GP Task"){
                if(connection.project_destination != null && connection.project_destination != ""){
                    this.$router.push({
                        name: 'ProjectTaskDetail',
                        params: {
                            teamId: connection.team_destination,
                            projectId: connection.project_destination,
                            taskId: connection.name_destination
                        }
                    })
                }else{
                    this.$router.push({
                        name: 'Task',
                        params: {
                            taskId: connection.name_destination
                        }
                    })
                }
            }
        },
        onRenderValueDoctype(connection){
            if(connection.doctype_destination == "GP Task") return "Task"
            else if(connection.doctype_destination == "GP Discussion") return "Discussion"
            else if(connection.doctype_destination == "GP Page") return "Page"
            return ""
        },
        onCancelAddingConnection(){
            this.show_adding_connection = false
            this.reference_doctype_select = "GP Task"
            this.reference_name_select = ""
        },
        onSaveAddingConnection(){
            this.$resources.connections.insert.submit({
                reference_type_source: this.reference_doctype,
                reference_name_source: this.reference_name,
                reference_type_destination: this.reference_doctype_select,
                reference_name_destination: this.reference_name_select
            })
            this.reference_doctype_select = "GP Task"
            this.show_adding_connection = false
        },
        onConfirmDeleteConnections(){
            this.$resources.delete_connections.fetch()
            this.show_confirm_deleteing = false
        }
    },
    watch: {
        reference_doctype_select(newVal, oldVal){
            this.reference_name_select = ""
            this.$resources.values_by_reference.fetch()
        }
    },
    mounted() {
    },
}
</script>