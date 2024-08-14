<template>
  <div class="flex" v-if="project">
    <DiscussionView
      class="w-full"
      :postId="postId"
      :read-only-mode="isReadOnlyMode || $readOnlyMode"
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
  resources: {
    permission_discussion(){
      return {
        url: "gameplan.api.permission_discussion",
        method: "GET",
        params: {
          discussion: this.postId
        },
        auto: true
      }
    }
  },
  methods: {
    isActive(update) {
      return Number(this.$route.params.postId) === update.name
    }
  },
  computed: {
    isReadOnlyMode(){
      let perrmission = this.$resources.permission_discussion.data
      if(perrmission == "write") return false
      else return true
    }
  }
}
</script>
