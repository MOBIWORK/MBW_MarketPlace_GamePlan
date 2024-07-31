<template>
  <div class="flex" v-if="project">
    <DiscussionView
      class="w-full"
      :postId="postId"
      :read-only-mode="isReadOnlyMode(project) || $readOnlyMode"
    />
  </div>
</template>
<script>
import { Avatar, TextEditor } from 'frappe-ui'
import Link from '@/components/Link.vue'
import Reactions from '@/components/Reactions.vue'
import DiscussionList from '@/components/DiscussionList.vue'
import DiscussionView from '@/components/DiscussionView.vue'
import { teams, teams_by_role } from '@/data/teams'
import { getUser } from '@/data/users'

export default {
  name: 'ProjectDiscussion',
  props: ['team', 'project', 'teamId', 'projectId', 'postId', 'slug'],
  components: {
    TextEditor,
    Avatar,
    Link,
    Reactions,
    DiscussionList,
    DiscussionView,
  },
  watch: {
    postId: {
      immediate: true,
      handler() {
        for (let team of teams_by_role.data || []) {
          if (team.name === this.team.doc.name) {
            team.open = true
          }
        }
      },
    },
  },
  methods: {
    isActive(update) {
      return Number(this.$route.params.postId) === update.name
    },
    isReadOnlyMode(project){
      if(project.doc.owner == getUser('sessionUser').name) return false;
      else{
        let roleProject = this.$getRoleByUser(null, this.project.doc)
        if(roleProject != null) {
          if(roleProject == "manager") return false
        }else{  
          let roleTeam = this.$getRoleByUser(this.team.doc, null)
          if (roleTeam == "member" || roleTeam == "guest") return true
          return false
        }
      }
    }
  },
}
</script>
