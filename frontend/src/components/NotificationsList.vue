<template>
    <div class="h-full w-full bg-white">
        <div class="border-b">
            <div class="flex items-center justify-between p-3">
                <div class="font-semibold text-2xl">Notifications</div>
                <div class="flex items-center">
                    <Button
                        :variant="'ghost'"
                        theme="gray"
                        size="sm"
                        label="Mark all as read"
                        :loading="$resources.markAllAsRead.loading"
                        @click="$resources.markAllAsRead.submit"
                        >
                        Mark all as read
                    </Button>
                    <div class="text-base cursor-pointer pr-1" @click="onMarkAllRead()"></div>
                    <Dropdown :options="[
                        {
                            label: 'Settings',
                            onClick: () => onSettingNotification()
                        }, {
                            label: 'Notification page',
                            onClick: () => onRouteNoticationPage(),
                            condition: () => parent_panel=='sidebar'
                        }
                    ]">
                        <Button :variant="'ghost'">
                            <template #icon>
                                <svg height="18px" xmlns="http://www.w3.org/2000/svg" width="21" viewBox="0 0 21 21"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" class="feather feather-more-vertical">
                                    <circle cx="12" cy="12" r="1"></circle>
                                    <circle cx="12" cy="5" r="1"></circle>
                                    <circle cx="12" cy="19" r="1"></circle>
                                </svg>
                            </template>
                        </Button>
                    </Dropdown>
                </div>
            </div>
        </div>
        <div class="flex items-center px-3 py-3">
            <div class="flex items-center px-3 py-1 mr-2 rounded-lg cursor-pointer"
                :class="{ 'active-status': activeStatus == 'all' }" @click="onChangeStatusFilter('all')">
                <div class="pr-2 text-base">All</div>
                <div class="text-sm px-3 py-1 rounded-md font-normal" style="background-color: rgba(0, 0, 0, 0.06);">{{
                    $resources.all_notifications.data }}</div>
            </div>
            <div class="flex items-center px-3 py-1 rounded-lg cursor-pointer"
                :class="{ 'active-status': activeStatus == 'unread' }" @click="onChangeStatusFilter('unread')">
                <div class="pr-2 text-base">Unread</div>
                <div class="text-sm px-3 py-1 rounded-md font-normal" style="background-color: rgba(0, 0, 0, 0.06);">{{
                    $resources.unread_notifications.data }}</div>
            </div>
        </div>
        <div class="overflow-auto" style="height: 89%;">
            <template v-for="notification in $resources.notifications.data">
                <div class="px-4 py-2.5" @click="onReadNotification(notification)">
                    <div class="flex cursor-pointer items-start gap-2.5 hover:bg-gray-100 border-b">
                        <div class="mt-1 flex items-center gap-2.5">
                            <UserAvatar :user="notification.from_user" size="lg" />
                        </div>
                        <div class="flex items-center justify-between w-full">
                            <div class="mr-2">
                                <div v-html="notification.message" />
                                <div class="text-sm text-gray-600 flex items-center mt-1 mb-1">
                                    <div class="mr-2">{{ formatTimeAgo(notification.creation) }}</div>
                                    <div class="flex items-center"
                                        v-if="notification.project_title != null && notification.project_title != ''">
                                        <div style="background-color: rgba(97, 97, 97, 0.5);"
                                            class="rounded-full h-2 w-2 mr-2"></div>
                                        <div>{{ notification.project_title }}</div>
                                    </div>
                                </div>
                            </div>
                            <div class="w-8 flex justify-end">
                                <div class="h-2 w-2 rounded-full ml-1"
                                    :class="[notification.read == 1 ? 'bg-transparent' : 'unread']" />
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </div>
    </div>
</template>

<script>

import { Dropdown, Button } from 'frappe-ui'
import UserAvatar from '@/components/UserAvatar.vue'
import { timeAgo } from '@/utils'
import { showSettingsDialog } from '@/components/Settings/SettingsDialog.vue'
import { unreadNotifications } from '@/data/notifications'
import { h } from 'vue'

export default {
    name: 'NotificationsList',
    components: { Dropdown, Button, UserAvatar },
    props: {
        parent_panel: {
            type: String
        }
    },
    data() {
        return {
            activeStatus: "all"
        }
    },
    resources: {
        notifications() {
            return {
                url: 'gameplan.api.get_notifications_by_filter',
                method: 'GET',
                params: {
                    status: this.activeStatus
                },
                auto: true,
                transform(data) {
                    console.log(data)
                },
            }
        },
        unread_notifications() {
            return {
                url: 'gameplan.api.unread_notifications',
                method: 'GET',
                auto: true
            }
        },
        all_notifications() {
            return {
                url: 'gameplan.api.all_notifications',
                method: 'GET',
                auto: true
            }
        },
        lst_notifications(){
            return {
                type: 'list',
                doctype: 'GP Notification'
            }
        },
        markAllAsRead() {
            return {
                url: 'gameplan.api.mark_all_notifications_as_read',
                onSuccess() {
                    this.$resources.unread_notifications.fetch()
                    this.$resources.notifications.fetch()
                    unreadNotifications.fetch()
                },
            }
        }
    },
    computed: {
    },
    mounted() {
        this.$socket.on('gp_notification', () => {
            this.$resources.unread_notifications.fetch()
            this.$resources.all_notifications.fetch()
            this.$resources.notifications.fetch()
        })
    },
    methods: {
        onSettingNotification() {
            showSettingsDialog(__('Notification'))
        },
        onRouteNoticationPage() {
            this.$router.push({
                name: 'Notifications'
            })
        },
        onChangeStatusFilter(status) {
            this.activeStatus = status
        },
        formatTimeAgo(time) {
            return timeAgo(time)
        },
        onReadNotification(notification){
            this.$resources.lst_notifications.setValue.submit(
                {
                    name: notification.name,
                    read: 1,
                },
                {
                onSuccess: () => {
                    this.$resources.unread_notifications.fetch()
                    this.$resources.notifications.fetch()
                    unreadNotifications.fetch()
                },
                }
            )
            if(notification.type == "Task"){
                if(notification.project != null && notification.project != ""){
                    this.$router.push({
                        name: 'ProjectTaskDetail',
                        params: {
                            projectId: notification.project,
                            teamId: notification.team,
                            taskId: notification.task
                        }
                    })
                }else{
                    this.$router.push({
                        name: 'Task',
                        params: {
                            taskId: notification.task
                        }
                    })
                }
                
            }else if (notification.type == "Discussion"){
                this.$router.push({
                    name: 'ProjectDiscussion',
                    params: {
                        teamId: notification.team,
                        projectId: notification.project,
                        postId: notification.discussion,
                    }
                })
            }else if(notification.type == "Page"){
                if(notification.project != null && notification.team != null){
                    this.$router.push({
                        name: 'ProjectPages',
                        params: {
                            teamId: notification.team,
                            projectId: notification.project
                        }
                    })
                }else{
                    this.$router.push({
                        name: 'MyPages'
                    })
                }
            }else if(notification.type == "Project"){
                this.$router.push({
                    name: 'Project',
                    params: {
                        teamId: notification.team,
                        projectId: notification.project
                    }
                })
            }else if(notification.type == "Team"){
                this.$router.push({
                    name: 'Team',
                    params: {
                        teamId: notification.team
                    }
                })
            }
        }
    }
}
</script>

<style scoped>
    .active-status {
        background-color: rgba(0, 0, 0, 0.08);
    }
    .unread{
        background-color: rgba(229, 28, 0, 1);
    }
</style>