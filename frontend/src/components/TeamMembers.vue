<template>
  <div class="flex items-center">
    <div class="flex items-center rounded-xl">
      <Button
        v-if="!team.doc.members.length"
        @click="inviteMemberDialog = true"
      >
        <template #prefix><LucideUserPlus class="w-4" /></template>
        {{__('Add Members')}}
      </Button>
      <template v-else>
        <button
          class="ml-4 flex items-center rounded-full"
          @click="inviteMemberDialog = true"
        >
          <div
            class="-ml-2 flex items-center rounded-full border-2 border-white"
            v-for="member in members"
            :key="member.name"
          >
            <UserAvatar :user="member.user" />
          </div>
        </button>
        <div v-if="members.length >= 5" class="w-7 h-7 rounded-full p-2 bg-gray-200	text-sm pl-0.5 pt-1.5">
          {{onRenderMemberLength()}}
        </div>
      </template>
    </div>
  </div>
  <AddMemberDialog :resource="team" v-model="inviteMemberDialog" @reloadMember="onReloadMember($event)"/>
</template>
<script>
import { Avatar } from 'frappe-ui'
import AddMemberDialog from '@/components/AddMemberDialog.vue'

export default {
  name: 'TeamHomeMembers',
  props: ['team'],
  components: {
    Avatar,
    AddMemberDialog,
  },
  data() {
    return {
      inviteMemberDialog: false,
    }
  },
  computed: {
    members() {
      let arr_team = this.team.doc.members.filter(
        (member) => member.status != 'Invited'
      )
      if(arr_team.length <= 5) return arr_team
      return arr_team.slice(0, 5)
    },
  },
  methods: {
    onReloadMember(event){
      let arrMember = []
      for(let i = 0; i < event.length; i++){
        let filterMember = this.team.doc.members.filter((member) => member.name == event[i].id)
        if(filterMember.length > 0) arrMember.push(filterMember[0])
      }
      this.team.doc.members = arrMember
    },
    onRenderMemberLength(){
      let arr_team = this.team.doc.members.filter(
        (member) => member.status != 'Invited'
      )
      return `+${arr_team.length - 5}`
    }
  }
}
</script>
