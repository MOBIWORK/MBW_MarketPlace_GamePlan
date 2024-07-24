<template>
    <div class="text-gray-600 text-sm mb-1">Add members</div>
    <TextInput
        ref="target"
        :type="'text'"
        size="sm"
        variant="subtle"
        placeholder="Enter name or email address"
        autocomplete="off"
        modelValue=""
        v-model="nameOrEmailMember" :debounce="debounceSearch" @focus="onFocusInputUser()" @keyup.enter.native="onEnterInputUser()"
    />
    <div ref="result_user" class="max-h-50 overflow-y-auto absolute z-50 mt-1 rounded-lg bg-white text-base shadow-2xl" style="width: 91%;"
        v-if="displayUserSystem">
        <template v-if="arrUserSystem.length > 0">
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
        </template>
        <template v-else>
            <div class="m-2 text-sm text-gray-700">Không có dữ liệu</div>
        </template>
    </div>
    <div class="mt-1 text-gray-600 text-sm">Enter name or email addess to add new invatation</div>
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
import { onClickOutside } from '@vueuse/core';

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
            arrUserSystem: [],
            target: null,
            result_user: null
        }
    },
    computed: {
    },
    mounted() {
        if (this.idTeamProject != null) {
            this.$resources.initMemberById.fetch()
        }
        onClickOutside([this.target, this.result_user], this.handleClickOutside);
    },
    methods: {
        onChangeRole(member) {
            this.memberAction = member
            if (member.role == "remove") {
                this.showDialogRemove = true
            }else{
                if(this.idTeamProject != null && this.idTeamProject != ""){
                    this.$resources.updateRoleMemberById.params = {
                        id_member: this.memberAction.id,
                        role_member: this.memberAction.role
                    }
                    this.$resources.updateRoleMemberById.fetch()
                }
                this.$emit('changeRole', this.arrMember)
            }
        },
        onRemoveMember(){
            if(this.idTeamProject != null && this.idTeamProject != ""){
                this.$resources.removeMemberById.params = {id_member: this.memberAction?.id}
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
            let arrMemberTrigger = this.arrMember.filter(x => x.id != this.memberAction.id)
            this.$emit('changeRole', arrMemberTrigger)
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
                        if(data.id_user != null){
                            me.arrMember.push({
                                'id_user': data.id_user,
                                'full_name': data.full_name,
                                'email': data.email,
                                'role': "member",
                                'id': data.id
                            })
                            me.$emit('addMember', me.arrMember)
                        }
                        
                    }
                })
                sourceAddMember.submit({team_project: this.idTeamProject, type_filter: this.typeParent, id_user: item.name})
            }else{
                let memberFilter = this.arrMember.filter(x => x.email == item.email)
                if(memberFilter.length == 0){
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
        handleClickOutside(event) {
            if(this.$refs.target && this.$refs.result_user && !this.$refs.target.el.contains(event.target) 
                && ! this.$refs.result_user.contains(event.target)){
                this.displayUserSystem = false
            }
        },
        onEnterInputUser(){
            console.log(this.nameOrEmailMember)
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