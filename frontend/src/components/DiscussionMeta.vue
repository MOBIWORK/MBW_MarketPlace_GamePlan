<template>
  <div class="leading-5">
    <span class="text-base text-gray-800">
      <UserProfileLink class="hover:text-blue-600" :user="discussion.owner">
        {{ $user(discussion.owner).full_name }}
      </UserProfileLink>
      {{__('in')}}
      <DiscussionBreadcrumbs :discussion="discussion" />
    </span>
    <span> &middot; </span>
    <span class="text-base text-gray-600">
      {{
        discussion.participants_count == 1
          ? `${__('1 participant')}`
          : `${discussion.participants_count} ${__('participants')}`
      }}
    </span>
  </div>
</template>
<script>
import DiscussionBreadcrumbs from './DiscussionBreadcrumbs.vue'
import UserProfileLink from './UserProfileLink.vue'

export default {
  name: 'DiscussionMeta',
  props: ['discussion'],
  components: { UserProfileLink, DiscussionBreadcrumbs },
}
</script>
