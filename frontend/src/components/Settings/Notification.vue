<template>
    <div class="flex min-h-0 flex-col mb-5">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold leading-none">{{__('Notifications')}}</h2>
      </div>
      <div class="my-3 text-sm text-gray-900">{{__('Email to receive notifications')}}: {{get_email()}}</div>
      <div class="overflow-y-auto">
        <div class="w-full block mb-1" v-for="permissionNotification in permissionNotifications">
            <NotificationSettingItem :id="permissionNotification.id" :title="permissionNotification.title" 
                :arr_permission="permissionNotification.arr_permission"></NotificationSettingItem>
        </div>
      </div>
    </div>
  </template>
  <script>
  import { Checkbox, createResource } from 'frappe-ui'
  import { getUser } from '@/data/users'
  import {configNotifications} from '@/data/notifications'
  import NotificationSettingItem from './NotificationSettingItem.vue'

  export default {
    name: 'Notification',
    components: { Checkbox, NotificationSettingItem },
    data() {
      return {
        permissionNotifications: []
      }
    },
    mounted(){
        let me = this;
        let configNotification = createResource({
            url: "gameplan.api.get_config_notifications",
            method: "GET",
            onSuccess(data) {
                me.permissionNotifications = data
            }
        })
        configNotification.fetch();
    },
    methods: {
        get_email(){
            return getUser('sessionUser').email;
        }
    },
  }
  
  </script>
  