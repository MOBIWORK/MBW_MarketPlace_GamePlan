<template>
  <Avatar
    v-if="user"
    :label="$user(user).full_name"
    :image="$user(user).user_image"
    :style="{
      backgroundColor: $user(user).image_background_color || null,
      filter: $user(user).isDisabled ? 'grayscale(1)' : null,
      borderColor: userActive? 'rgb(14 165 233)': null,
      borderWidth: userActive? '2px' : null
    }"
    :title="$user(user).isDisabled ? __('User is disabled') : null"
    v-bind="$attrs"
    class="cursor-pointer"
    @click="onActiveUser()"
  />
</template>
<script>
import { Avatar } from 'frappe-ui'

export default {
  name: 'UserAvatar',
  inheritAttrs: false,
  components: { Avatar },
  props: ['user', 'active_check', 'check_user'],
  emits: ['activeUserEvent', 'deactiveUserEvent'],
  data(){
    return {
      userActive: this.check_user
    }
  },
  methods: {
    onActiveUser(){
      if(this.active_check){
        this.userActive = !this.userActive
        if(this.userActive) this.$emit('activeUserEvent', this.user)
        else this.$emit('deactiveUserEvent', this.user)
      }
    }
  },
  watch: {
    check_user(newCheck, oldCheck){
      this.userActive = this.check_user
    }
  }
}
</script>
