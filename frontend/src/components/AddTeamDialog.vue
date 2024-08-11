<template>
  <Dialog :options="{ title: __('Add Team') }" v-model="showDialog">
    <template #body-content>
      <div class="space-y-4">
        <FormControl
          :label="__('Team Name')"
          type="text"
          v-model="newTeam.title"
          :placeholder="__('Team Name')"
          @keydown.enter="createTeam($event.target.value)"
          autocomplete="off"
        />
        <FormControl
          type="select"
          :label="__('Visibility')"
          :options="[
            { label: __('Visible to everyone'), value: 0 },
            { label: __('Visible to team members (Private)'), value: 1 },
          ]"
          v-model="newTeam.is_private"
        />
        <ng-template v-if="newTeam.is_private==1">
          <div class="text-gray-600 text-sm mb-1 mt-3">Add members</div>
          <TextInput
              ref="target"
              :type="'text'"
              size="sm"
              variant="subtle"
              placeholder="Enter name or email address"
              autocomplete="off"
              modelValue=""
              v-model="nameOrEmailMember" @focus="onFocusInputUser()" @keydown.enter.prevent="onEnterInputUser($event)"
          />
          <div ref="result_user" class="max-h-50 overflow-y-auto absolute z-50 mt-1 rounded-lg bg-white text-base shadow-2xl" style="width: 91%;"
              v-if="displayUserSystem">
              <template v-if="arrUserSystem.length > 0">
                  <ul role="list" class="mt-2 ml-2 divide-y overflow-y-auto" style="max-height: 7rem;">
                      <li class="flex w-full items-center py-2 cursor-pointer hover:bg-gray-300" v-for="user_info in arrUserSystem"
                          :key="user_info.name" @click="onClickAddMember(user_info)">
                          <UserAvatar :user="user_info.name" />
                          <div class="ml-3">
                              <div class="text-base font-medium text-gray-800 truncate max-w-sm">
                                  {{ user_info.full_name }}
                              </div>
                              <div class="text-sm text-gray-600 truncate max-w-sm">
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
          <div class="mt-1 text-gray-600 text-sm">Enter name or email addess to add new invitation</div>
          <ul role="list" class="mt-2 divide-y overflow-y-auto max-h-56">
            <li class="flex w-full items-center py-2" v-for="member in arrMember" :key="member.id">
                <UserAvatar :user="member.id_user" v-if="member.id_user != null"/>
                <div class="ml-3">
                    <div class="text-base font-medium text-gray-800 truncate w-52">
                        {{ member.full_name }}
                    </div>
                    <div class="text-sm text-gray-600 truncate w-52" style="height:1rem;">
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
                    ]" size="sm" variant="subtle" :disabled="readOnly==true" v-model="member.role"
                        @change="onChangeRole(member)" />
                </div>
            </li>
        </ul>
        </ng-template>
        <ErrorMessage :message="teams.insert.error?.messages" />
      </div>
    </template>
    <template #actions>
      <Button
        variant="solid"
        class="w-full"
        @click="createTeam(teamName)"
        :loading="teams.insert?.loading"
      >
        {{__('Create Team')}}
      </Button>
    </template>
  </Dialog>
</template>
<script>
import { teams, teams_by_role } from '@/data/teams'
import { onClickOutside } from '@vueuse/core'
import { createToast } from '@/utils'
import { getUser } from '@/data/users'

export default {
  name: 'AddTeamDialog',
  props: ['show'],
  emits: ['success', 'update:show'],
  data() {
    return {
      newTeam: { title: '', is_private: 0 },
      teams,
      nameOrEmailMember: "",
      displayUserSystem: false,
      arrUserSystem: [],
      arrMember: [
        {
          'id_user': getUser('sessionUser').name,
          'full_name': getUser('sessionUser').full_name,
          'email': getUser('sessionUser').email,
          'role': "manager",
          'id': getUser('sessionUser').name
        }
      ],
      target: null,
      result_user: null
    }
  },
  resources: {
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
    },
    team_creation(){
      return{
        url: "gameplan.api.create_team",
        method: "POST",
        auto: false,
        onSuccess(data){
          if(data.status == "ok"){
            teams_by_role.fetch()
            this.showDialog = false
            console.log(data.message)
            this.$emit('success', data.message)
            this.newTeam = {}
          }else{
            createToast({
              title: __('Lỗi thêm mới nhóm'),
              icon: 'x',
              iconClasses: 'text-red-600',
            })
          }
        }
      }
    }
  },
  methods: {
    createTeam() {
      console.log(this.newTeam);
      console.log(this.arrMember);
      let objPost = {
        'title': this.newTeam.title,
        'is_private': this.newTeam.is_private,
        'arr_member': []
      }
      for(let i = 0; i < this.arrMember.length; i++){
        let objMenber = {
          'id': this.arrMember[i].id_user,
          'email': this.arrMember[i].email
        }
        objPost.arr_member.push(objMenber)
      }
      this.$resources.team_creation.submit(objPost)
      return;
      teams.insert.submit(this.newTeam, {
        onSuccess: (team) => {
          //this.$resetData('newTeam')
          teams_by_role.fetch()
          this.showDialog = false
          this.$emit('success', team)
        },
      })
    },
    onFocusInputUser(){
      this.displayUserSystem = true
    },
    onEnterInputUser(event){
      this.displayUserSystem = false
      event.stopPropagation();
      const regular_email = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if(!regular_email.test(this.nameOrEmailMember)){
        createToast({
          title: __('Định dạng email không hợp lệ. Vui lòng nhập lại email để thêm vào nhóm'),
          icon: 'x',
          iconClasses: 'text-red-600',
        })
        return
      }
      let memberFilter = this.arrMember.filter(x => x.id == this.nameOrEmailMember)
      if(memberFilter.length == 0){
        this.arrMember.push({
          'id_user': null,
          'full_name': this.nameOrEmailMember,
          'email': this.nameOrEmailMember,
          'role': "member",
          'id': this.nameOrEmailMember
        })
      }
    },
    onClickAddMember(item){
      this.displayUserSystem = false
      let memberFilter = this.arrMember.filter(x => x.id == item.name);
      if(memberFilter.length == 0){
        this.arrMember.push({
          'id_user': item.name,
          'full_name': item.full_name,
          'email': item.email,
          'role': "member",
          'id': item.name
        })
      }
    },
    onChangeRole(member){
      if (member.role == "remove") {
        if(this.arrMember.length == 1){
          this.arrMember[0].role = "manager";
          return
        }
        for(let i = 0; i < this.arrMember.length; i++){
          if(this.arrMember[i].id == member.id){
            this.arrMember.splice(i, 1)
          }
        }
      }else if(member.role == "member"){
        if(this.arrMember.length == 1){
          this.arrMember[0].role = "manager";
          return
        }
      }
    },
    handleClickOutside(event) {
      if(this.$refs.target && this.$refs.result_user && !this.$refs.target.el.contains(event.target) 
        && ! this.$refs.result_user.contains(event.target)){
        this.displayUserSystem = false
      }
    }
  },
  computed: {
    showDialog: {
      get() {
        return this.show
      },
      set(val) {
        this.$emit('update:show', val)
      },
    },
  },
  watch: {
    nameOrEmailMember(newVal){
      this.$resources.userSystem.fetch()
    } 
  },
  mounted(){
    onClickOutside([this.target, this.result_user], this.handleClickOutside);
  }
}
</script>
