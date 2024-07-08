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
import { teams } from '@/data/teams'
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
        for (let team of teams.data || []) {
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
      //Boolean(project.doc.archived_at)
      if(project.doc.owner == getUser('sessionUser').name) return false;
      return true;
    }
  },
}
</script>
