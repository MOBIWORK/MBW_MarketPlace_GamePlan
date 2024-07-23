<template>
    <div v-if="typeParent == 'team'" class="text-lg font-bold">Team members</div>
    <div v-else class="text-lg front-bold">Project members</div>
    <div class="text-gray-600 text-sm mt-2 mb-1">Add members</div>
    <TextInput
        :type="'text'"
        size="sm"
        variant="subtle"
        placeholder="Enter name or email address"
        autocomplete="off"
        modelValue=""
        v-model="nameOrEmailMember" :debounce="debounceSearch" @focus="onFocusInputUser()"
    />
    <div ref="result_user" class="max-h-40 overflow-y-auto absolute z-50 mt-1 rounded-lg bg-white text-base shadow-2xl" style="width: 91%;" v-if="displayUserSystem">
        <ul role="list" class="mt-2 ml-2 divide-y overflow-y-auto max-h-80">
            <li class="flex w-full items-center py-2 cursor-pointer hover:bg-gray-300" v-for="user_info in arrUserSystem"
                :key="user_info.name" @click="onClickAddMember(user_info)">
                <UserAvatar :user="user_info.name" />
                <div class="ml-3">
                    <div class="text-base font-medium text-gray-800">
                        {{ user_info.full_name }}
                    </div>
                    <div class="text-sm text-gray-600">
                        {{ user_info.email }}
                    </div>
                </div>
            </li>
        </ul>
    </div>
    <div class="mt-1 text-gray-600 text-sm">Press Enter to add new invatation</div>
    <ul role="list" class="mt-2 divide-y overflow-y-auto max-h-80">
        <li class="flex w-full items-center py-2" v-for="member in arrMember" :key="member.id">
            <UserAvatar :user="member.id_user" />
            <div class="ml-3">
                <div class="text-base font-medium text-gray-800">
                    {{ member.full_name }}
                </div>
                <div class="text-sm text-gray-600">
                    {{ member.email }}
                </div>
            </div>
            <div class="ml-auto">
                <FormControl class="w-40" type="select" :options="[
                    {
                        label: 'Manager',
                        value: 'manager',
                    },
                    {
                        label: 'Member',
                        value: 'member',
                    },
                    {
                        label: 'Remove',
                        value: 'remove',
                    },
                ]" size="sm" variant="subtle" :disabled="false" v-model="member.role"
                    @change="onChangeRole(member)" />
            </div>
        </li>
    </ul>
    <Dialog
        :options="{
            title: 'Remove member',
            message: 'Removing member from ' + typeParent + ' prevents them from accessing its content. You can add them again later.',
            size: 'xl',
            actions: [
                {
                    label: 'Remove',
                    variant: 'solid',
                    theme: 'red',
                    onClick: () => onRemoveMember()
                },
            ],
        }"
        v-model="showDialogRemove"
    />
</template>

<script>

import { FormControl, createResource } from 'frappe-ui'

export default {
    name: 'MemberTeamProject',
    components: [FormControl],
    props: ["idTeamProject", "typeParent"],
    emits: ["addMember", "changeRole"],
    resources: {
        initMemberById() {
            return {
                url: "gameplan.api.get_members_by_type",
                method: "GET",
                params: {
                    team_project: this.idTeamProject,
                    type_filter: this.typeParent
                },
                auto: false,
                onSuccess(data) {
                    this.arrMember = data
                }
            }
        },
        removeMemberById(){
            return {
                url: "gameplan.api.delete_member_by_id",
                method: "GET",
                params: {
                    id_member: this.memberAction.id
                },
                auto: false,
                onSuccess(data){
                    if(data == "ok"){
                        this.$resources.initMemberById.fetch()
                    }
                }
            }
        },
        updateRoleMemberById(){
            return {
                url: "gameplan.api.update_role_member_by_id",
                method: "GET",
                params: {
                    id_member: this.memberAction.id,
                    role_member: this.memberAction.role
                },
                auto: false,
                onSuccess(data){
                    if(data == "ok"){
                        this.$resources.initMemberById.fetch()
                    }
                }
            }
        },
        userSystem(){
            return {
                url: "gameplan.api.get_user_system_by_filter",
                method: "GET",
                params: {
                    txtSearch: this.nameOrEmailMember
                },
                auto: true,
                onSuccess(data){
                    this.arrUserSystem = data
                }
            }
        }
    },
    data() {
        return {
            nameOrEmailMember: "",
            arrMember: [],
            showDialogRemove: false,
            memberAction: null,
            debounceSearch: 500,
            displayUserSystem: false,
            arrUserSystem: []
        }
    },
    computed: {
    },
    mounted() {
        if (this.idTeamProject != null) {
            this.$resources.initMemberById.fetch()
        }
    },
    methods: {
        onChangeRole(member) {
            this.memberAction = member
            if (member.role == "remove") {
                this.showDialogRemove = true
            }else{
                if(this.idTeamProject != null && this.idTeamProject != ""){
                    this.$resources.updateRoleMemberById.fetch()
                }
                this.$emit('changeRole', this.arrMember)
            }
        },
        onRemoveMember(){
            if(this.idTeamProject != null && this.idTeamProject != ""){
                this.$resources.removeMemberById.fetch()
                this.showDialogRemove = false;
            }else{
                for(let i = 0; i < this.arrMember.length; i++){
                    if(this.arrMember[i].id = this.memberAction.id){
                        this.arrMember.splice(i, 1)
                        break
                    }
                }
            }
            this.$emit('changeRole', this.arrMember)
        },
        onFocusInputUser(){
            this.displayUserSystem = true
        },
        onClickAddMember(item){
            this.displayUserSystem = false
            let me = this;
            if(this.idTeamProject != null && this.idTeamProject != ""){
                let sourceAddMember = createResource({
                    url: "gameplan.api.add_role_member_by_id",
                    method: "POST",
                    auto: false,
                    onSuccess(data){
                        me.arrMember.push({
                            'id_user': data.id_user,
                            'full_name': data.full_name,
                            'email': data.email,
                            'role': "member",
                            'id': data.id
                        })
                        me.$emit('addMember', me.arrMember)
                    }
                })
                sourceAddMember.submit({team_project: this.idTeamProject, type_filter: this.typeParent, id_user: item.name})
            }else{
                this.arrMember.push({
                    'id_user': item.name,
                    'full_name': item.full_name,
                    'email': item.email,
                    'role': "member",
                    'id': item.name
                })
                this.$emit('addMember', this.arrMember)
            }
        }
    },
    watch: {
        nameOrEmailMember(newVal){
            this.$resources.userSystem.fetch()
        } 
    }
}
</script>
<style scoped></style>