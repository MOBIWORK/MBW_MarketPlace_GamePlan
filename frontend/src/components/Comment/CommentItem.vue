<template>
    <div class="w-full relative">
        <div :id="'line_comment_' + comment_info.name" class="border-l-2 absolute h-full" style="left:14px;border-color: rgba(235, 235, 235, 1);" v-show="showListReplies"></div>
        <div class="my-3 flex items-start">
            <UserAvatar :user="comment_info.owner" size="xl" class="w-8 mr-3" />
            <div class="w-full">
                <div class="flex items-center">
                    <div class="font-medium text-base">{{getUserByName(comment_info.owner).full_name}}</div>
                    <div class="ml-2 px-2 py-1 rounded-full text-sm" style="background-color: rgba(0, 122, 255, 0.15);color: rgba(24, 119, 242, 1);" v-if="comment_info.owner == getUserByName('sessionUser').name">
                        {{__('Owner')}}
                    </div>
                    <div class="ml-3 flex items-center">
                         <div style="background-color: rgba(97, 97, 97, 0.5);" class="rounded-full h-1.5 w-1.5"></div>
                        <time
                            class="text-gray-600 ml-2 text-sm"
                            :datetime="comment_info.creation"
                            :title="$dayjs(comment_info.creation)"
                            >
                            {{ $dayjs(comment_info.creation).fromNow() }}
                        </time>
                    </div>
                    <div class="ml-3 flex items-center" v-if="comment_info.modified != null && comment_info.modified != '' && comment_info.modified != comment_info.owner">
                        <div style="background-color: rgba(97, 97, 97, 0.5);" class="rounded-full h-1.5 w-1.5"></div>
                        <div class="text-gray-600 ml-2 text-sm">
                            <span>{{__('Edited')}} &nbsp;</span>
                            <time
                                :datetime="comment_info.modified"
                                :title="$dayjs(comment_info.modified)"
                                >
                                {{ $dayjs(comment_info.modified).fromNow() }}
                            </time>
                            </div>
                        </div>
                    </div>
                    <template v-if="comment_info.showEdit">
                        <CommentReplyEditor class="my-2"
                            :value="comment_info.content"
                            @change="comment_info['edit_content'] = $event"
                            :editable="true"
                            :submitButtonProps="{
                                onClick: () => onSubmitUpdateCommentParent()
                            }"
                            :discardButtonProps="{
                                onClick: () => onImshowEditCommentParent()
                            }"
                        />
                    </template>
                    <template v-if="!comment_info.showEdit">
                        <CommentReplyEditor class="my-2"
                            :value="comment_info.content"
                            :editable="false"
                        />
                    </template>
                    <div class="flex items-center">
                        <div class="flex items-center cursor-pointer mr-3" @click="onReplyComment(comment_info)">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M13.9531 7.24219C13.9635 7.21094 13.974 7.17188 13.9844 7.125C13.9948 7.07812 14 7.03385 14 6.99219C14 6.89844 13.9818 6.8125 13.9453 6.73438C13.9089 6.65625 13.8594 6.58594 13.7969 6.52344L10.4688 3.17969C10.4062 3.1276 10.3359 3.08594 10.2578 3.05469C10.1797 3.02344 10.099 3.00781 10.0156 3.00781C9.82812 3.00781 9.66927 3.07292 9.53906 3.20312C9.40885 3.33333 9.34375 3.48698 9.34375 3.66406C9.34375 3.75781 9.35938 3.84375 9.39062 3.92188C9.42188 4 9.46875 4.07031 9.53125 4.13281L11.7188 6.32031H5.32812C4.86979 6.32031 4.4375 6.40885 4.03125 6.58594C3.63542 6.76302 3.28646 7.0026 2.98438 7.30469C2.68229 7.60677 2.44271 7.96094 2.26562 8.36719C2.08854 8.76302 2 9.19531 2 9.66406V12.3203C2 12.5078 2.0651 12.6667 2.19531 12.7969C2.32552 12.9271 2.48438 12.9922 2.67188 12.9922C2.84896 12.9922 3.0026 12.9271 3.13281 12.7969C3.26302 12.6667 3.32812 12.5078 3.32812 12.3203V9.66406C3.32812 9.11198 3.52344 8.64062 3.91406 8.25C4.30469 7.85938 4.77604 7.66406 5.32812 7.66406H11.7188L9.53125 9.85156C9.46875 9.91406 9.41927 9.98698 9.38281 10.0703C9.34635 10.1536 9.32812 10.2422 9.32812 10.3359C9.32812 10.5234 9.39323 10.6823 9.52344 10.8125C9.65365 10.9427 9.80729 11.0078 9.98438 11.0078C10.0885 11.0078 10.1797 10.9896 10.2578 10.9531C10.3359 10.9167 10.4062 10.8672 10.4688 10.8047L13.7969 7.46094C13.8281 7.42969 13.8568 7.39583 13.8828 7.35938C13.9089 7.32292 13.9323 7.28906 13.9531 7.25781V7.24219Z" fill="#637381"/>
                            </svg>
                            <div class="ml-1 text-sm weight font-medium" style="color: rgba(99, 115, 129, 1);">{{__('Reply')}}</div>
                        </div>
                        <Reactions
                            doctype="GP Comment"
                            :name="comment_info.name"
                            v-model:reactions="comment_info.reactions"
                        />
                        <Dropdown
                            v-if="comment_info.owner == getUserByName('sessionUser').name"
                            class="ml-3"
                            :options="[
                                {
                                    label: 'Edit',
                                    onClick: () => onEditCommentParent(comment_info),
                                    icon: 'edit'
                                },{
                                    label: 'Delete',
                                    onClick: () => onDeleteCommentParent(comment_info),
                                    icon: 'trash'
                                }
                            ]"
                            >
                            <Button :variant="'ghost'">
                                <template #icon>
                                    <FeatherIcon
                                        name="more-horizontal"
                                        class="h-4 w-4"
                                    />
                                </template>
                            </Button>
                        </Dropdown>
                    </div>
                    <template v-if="showListReplies">
                        <div :id="'comment_child_' + comment_child.name" class="mt-3 flex items-start relative" v-for="comment_child in comment_info.children">
                            <div class="border-b-2 absolute" style="width: 35px;border-color: rgba(235, 235, 235, 1);top:11px;left:-30px"></div>
                            <UserAvatar :user="comment_child.owner" size="xl" class="w-8 mr-3" />
                            <div class="w-full">
                                <div class="flex items-center">
                                    <div class="font-medium text-base">{{getUserByName(comment_child.owner).full_name}}</div>
                                    <div class="ml-2 px-2 py-1 rounded-full text-sm" style="background-color: rgba(0, 122, 255, 0.15);color: rgba(24, 119, 242, 1);" v-if="comment_child.owner == getUserByName('sessionUser').name">
                                        {{__('Owner')}}
                                    </div>
                                    <div class="flex items-center ml-1" v-if="comment_child.reply_child == 1 && comment_child.reply_child_user != null">
                                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M13.9531 7.24219C13.9635 7.21094 13.974 7.17188 13.9844 7.125C13.9948 7.07812 14 7.03385 14 6.99219C14 6.89844 13.9818 6.8125 13.9453 6.73438C13.9089 6.65625 13.8594 6.58594 13.7969 6.52344L10.4688 3.17969C10.4062 3.1276 10.3359 3.08594 10.2578 3.05469C10.1797 3.02344 10.099 3.00781 10.0156 3.00781C9.82812 3.00781 9.66927 3.07292 9.53906 3.20312C9.40885 3.33333 9.34375 3.48698 9.34375 3.66406C9.34375 3.75781 9.35938 3.84375 9.39062 3.92188C9.42188 4 9.46875 4.07031 9.53125 4.13281L11.7188 6.32031H5.32812C4.86979 6.32031 4.4375 6.40885 4.03125 6.58594C3.63542 6.76302 3.28646 7.0026 2.98438 7.30469C2.68229 7.60677 2.44271 7.96094 2.26562 8.36719C2.08854 8.76302 2 9.19531 2 9.66406V12.3203C2 12.5078 2.0651 12.6667 2.19531 12.7969C2.32552 12.9271 2.48438 12.9922 2.67188 12.9922C2.84896 12.9922 3.0026 12.9271 3.13281 12.7969C3.26302 12.6667 3.32812 12.5078 3.32812 12.3203V9.66406C3.32812 9.11198 3.52344 8.64062 3.91406 8.25C4.30469 7.85938 4.77604 7.66406 5.32812 7.66406H11.7188L9.53125 9.85156C9.46875 9.91406 9.41927 9.98698 9.38281 10.0703C9.34635 10.1536 9.32812 10.2422 9.32812 10.3359C9.32812 10.5234 9.39323 10.6823 9.52344 10.8125C9.65365 10.9427 9.80729 11.0078 9.98438 11.0078C10.0885 11.0078 10.1797 10.9896 10.2578 10.9531C10.3359 10.9167 10.4062 10.8672 10.4688 10.8047L13.7969 7.46094C13.8281 7.42969 13.8568 7.39583 13.8828 7.35938C13.9089 7.32292 13.9323 7.28906 13.9531 7.25781V7.24219Z" fill="#637381"/>
                                        </svg>
                                        <div class="ml-1 text-sm weight font-medium" style="color: rgba(99, 115, 129, 1);">{{getUserByName(comment_child.reply_child_user).full_name}}</div>
                                    </div>
                                    <div class="ml-3 flex items-center">
                                        <div style="background-color: rgba(97, 97, 97, 0.5);" class="rounded-full h-1.5 w-1.5"></div>
                                        <time
                                            class="text-gray-600 ml-2 text-sm"
                                            :datetime="comment_child.creation"
                                            :title="$dayjs(comment_child.creation)"
                                            >
                                            {{ $dayjs(comment_child.creation).fromNow() }}
                                        </time>
                                    </div>
                                    <div class="ml-3 flex items-center" v-if="comment_child.modified != null && comment_child.modified != '' && comment_child.modified != comment_child.owner">
                                        <div style="background-color: rgba(97, 97, 97, 0.5);" class="rounded-full h-1.5 w-1.5"></div>
                                        <div class="text-gray-600 ml-2 text-sm">
                                            <span>{{__('Edited')}} &nbsp;</span>
                                            <time
                                            :datetime="comment_child.modified"
                                            :title="$dayjs(comment_child.modified)"
                                            >
                                            {{ $dayjs(comment_child.modified).fromNow() }}
                                        </time>
                                        </div>
                                    </div>
                                </div>
                                <template v-if="comment_child.showEdit">
                                    <CommentReplyEditor class="my-2"
                                        :value="comment_child.content"
                                        :editable="true"
                                        @change="comment_child['edit_content'] = $event"
                                        :submitButtonProps="{
                                            onClick: () => onSubmitUpdateCommentChild(comment_child)
                                        }"
                                        :discardButtonProps="{
                                            onClick: () => onImshowEditCommentChild(comment_child)
                                        }"
                                    />
                                </template>
                                <template v-if="!comment_child.showEdit">
                                    <CommentReplyEditor class="my-2"
                                        :value="comment_child.content"
                                        :editable="false"
                                    />
                                </template>
                                <div class="flex items-center">
                                    <div class="flex items-center cursor-pointer mr-3" @click="onReplyCommentChild(comment_child)">
                                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M13.9531 7.24219C13.9635 7.21094 13.974 7.17188 13.9844 7.125C13.9948 7.07812 14 7.03385 14 6.99219C14 6.89844 13.9818 6.8125 13.9453 6.73438C13.9089 6.65625 13.8594 6.58594 13.7969 6.52344L10.4688 3.17969C10.4062 3.1276 10.3359 3.08594 10.2578 3.05469C10.1797 3.02344 10.099 3.00781 10.0156 3.00781C9.82812 3.00781 9.66927 3.07292 9.53906 3.20312C9.40885 3.33333 9.34375 3.48698 9.34375 3.66406C9.34375 3.75781 9.35938 3.84375 9.39062 3.92188C9.42188 4 9.46875 4.07031 9.53125 4.13281L11.7188 6.32031H5.32812C4.86979 6.32031 4.4375 6.40885 4.03125 6.58594C3.63542 6.76302 3.28646 7.0026 2.98438 7.30469C2.68229 7.60677 2.44271 7.96094 2.26562 8.36719C2.08854 8.76302 2 9.19531 2 9.66406V12.3203C2 12.5078 2.0651 12.6667 2.19531 12.7969C2.32552 12.9271 2.48438 12.9922 2.67188 12.9922C2.84896 12.9922 3.0026 12.9271 3.13281 12.7969C3.26302 12.6667 3.32812 12.5078 3.32812 12.3203V9.66406C3.32812 9.11198 3.52344 8.64062 3.91406 8.25C4.30469 7.85938 4.77604 7.66406 5.32812 7.66406H11.7188L9.53125 9.85156C9.46875 9.91406 9.41927 9.98698 9.38281 10.0703C9.34635 10.1536 9.32812 10.2422 9.32812 10.3359C9.32812 10.5234 9.39323 10.6823 9.52344 10.8125C9.65365 10.9427 9.80729 11.0078 9.98438 11.0078C10.0885 11.0078 10.1797 10.9896 10.2578 10.9531C10.3359 10.9167 10.4062 10.8672 10.4688 10.8047L13.7969 7.46094C13.8281 7.42969 13.8568 7.39583 13.8828 7.35938C13.9089 7.32292 13.9323 7.28906 13.9531 7.25781V7.24219Z" fill="#637381"/>
                                        </svg>
                                        <div class="ml-1 text-sm weight font-medium" style="color: rgba(99, 115, 129, 1);">{{__('Reply')}}</div>
                                    </div>
                                    <Reactions
                                        doctype="GP Comment"
                                        :name="comment_child.name"
                                        v-model:reactions="comment_child.reactions"
                                    />
                                    <Dropdown
                                        v-if="comment_child.owner == getUserByName('sessionUser').name"
                                        class="ml-3"
                                        :options="[
                                            {
                                                label: 'Edit',
                                                onClick: () => onEditCommentChild(comment_child),
                                                icon: 'edit'
                                            },{
                                                label: 'Delete',
                                                onClick: () => onDeleteCommentChild(comment_child),
                                                icon: 'trash'
                                            }
                                        ]"
                                        >
                                        <Button :variant="'ghost'">
                                            <template #icon>
                                                <FeatherIcon
                                                    name="more-horizontal"
                                                    class="h-4 w-4"
                                                />
                                            </template>
                                        </Button>
                                    </Dropdown>
                                </div>
                            </div>
                        </div>
                    </template>
                    <div class="flex mt-1 w-full" v-if="comment_info.children.length > 0 && showReplyComment == false">
                        <div
                            class="-ml-2 flex items-center rounded-full border-2 border-white"
                            v-for="user in user_reply"
                            :key="user"
                        >
                            <UserAvatar :user="user" size="md" />
                        </div>
                        <div v-if="num_user_reply > 0" class="w-7 h-7 rounded-full p-2 bg-gray-100	text-sm flex justify-center items-center text-gray-700">
                            +{{num_user_reply}}
                        </div>
                        <div class="ml-2 cursor-pointer text-sm font-medium flex items-center" style="color: rgba(33, 43, 54, 1);" @click="onShowListReplies()">
                            <span v-if="showListReplies==false">{{__('Show (')}}{{comment_info.children.length}}{{__(') replies')}}</span>
                            <span v-if="showListReplies==true">{{__('Hide (')}}{{comment_info.children.length}}{{__(') replies')}}</span>
                        </div>
                    </div>
                    <div class="mt-3 flex items-center" v-if="showReplyComment">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M13.9531 7.24219C13.9635 7.21094 13.974 7.17188 13.9844 7.125C13.9948 7.07812 14 7.03385 14 6.99219C14 6.89844 13.9818 6.8125 13.9453 6.73438C13.9089 6.65625 13.8594 6.58594 13.7969 6.52344L10.4688 3.17969C10.4062 3.1276 10.3359 3.08594 10.2578 3.05469C10.1797 3.02344 10.099 3.00781 10.0156 3.00781C9.82812 3.00781 9.66927 3.07292 9.53906 3.20312C9.40885 3.33333 9.34375 3.48698 9.34375 3.66406C9.34375 3.75781 9.35938 3.84375 9.39062 3.92188C9.42188 4 9.46875 4.07031 9.53125 4.13281L11.7188 6.32031H5.32812C4.86979 6.32031 4.4375 6.40885 4.03125 6.58594C3.63542 6.76302 3.28646 7.0026 2.98438 7.30469C2.68229 7.60677 2.44271 7.96094 2.26562 8.36719C2.08854 8.76302 2 9.19531 2 9.66406V12.3203C2 12.5078 2.0651 12.6667 2.19531 12.7969C2.32552 12.9271 2.48438 12.9922 2.67188 12.9922C2.84896 12.9922 3.0026 12.9271 3.13281 12.7969C3.26302 12.6667 3.32812 12.5078 3.32812 12.3203V9.66406C3.32812 9.11198 3.52344 8.64062 3.91406 8.25C4.30469 7.85938 4.77604 7.66406 5.32812 7.66406H11.7188L9.53125 9.85156C9.46875 9.91406 9.41927 9.98698 9.38281 10.0703C9.34635 10.1536 9.32812 10.2422 9.32812 10.3359C9.32812 10.5234 9.39323 10.6823 9.52344 10.8125C9.65365 10.9427 9.80729 11.0078 9.98438 11.0078C10.0885 11.0078 10.1797 10.9896 10.2578 10.9531C10.3359 10.9167 10.4062 10.8672 10.4688 10.8047L13.7969 7.46094C13.8281 7.42969 13.8568 7.39583 13.8828 7.35938C13.9089 7.32292 13.9323 7.28906 13.9531 7.25781V7.24219Z" fill="#637381"/>
                        </svg>
                        <div class="text-gray-600 ml-2 text-sm">Reply</div>
                        <div class="text-gray-600 ml-1 text-sm">{{getUserByName(replyComment.owner).full_name}}</div>
                    </div>
                    <div class="mt-1 w-full" v-if="showReplyComment">
                        <CommentReplyEditor
                            :value="contentRepplyComment"
                            @change="contentRepplyComment = $event"
                            :submitButtonProps="{
                                onClick: () => onSubmitReplyCommnet()
                            }"
                            :discardButtonProps="{
                                onClick: () => onCancelReplyComment(),
                            }"
                        />
                    </div>
                </div>
        </div>
        <Dialog
            :options="{
                title: __('Delete comment?'),
                message: __('This action can not be undone'),
                size: 'xl',
                actions: [
                    {
                        label: __('Delete'),
                        variant: 'solid',
                        theme: 'red',
                        onClick: () => onConfirmDeleteComment()
                    }
                ],
            }"
            v-model="showDialogDeleteComment"
        />
    </div>
</template>

<script>
import { getUser } from '@/data/users'
import Reactions from '@/components/Reactions.vue'
import {
    Dropdown,
    Button,
    FeatherIcon,
    Dialog
} from 'frappe-ui'
import CommentReplyEditor from '@/components/Comment/CommentReplyEditor.vue'

export default{
    name: 'CommentItem',
    props: {
        comment_info: {
            type: Object
        }
    },
    emits: ['replyCommentParent', 'replyCommentChild', 'deleteComment', 'updateComment'],
    data(){
        return{
            showListReplies: false,
            showReplyComment: false,
            replyParent: false,
            replyComment: null,
            contentRepplyComment: "",
            showDialogDeleteComment: false,
            nameDeleteComment: "",
            isEditCommentChild: false
        }
    },
    components: {
        Dropdown,
        Button,
        FeatherIcon,
        Dialog,
        CommentReplyEditor
    },
    methods: {
        getUserByName(name){
            return getUser(name)
        },
        onReplyComment(data){
            this.showReplyComment = true
            this.replyParent = true
            this.replyComment = data
        },
        onSubmitReplyCommnet(){
            if(this.replyParent){
                this.$emit('replyCommentParent', {
                    'parent': this.replyComment.name,
                    'content': this.contentRepplyComment,
                    'root_name': this.replyComment.name
                })
            }else{
                this.$emit('replyCommentChild', {
                    'parent': this.replyComment.name,
                    'content': this.contentRepplyComment,
                    'user': this.replyComment.owner,
                    'root_name': this.replyComment.root_name
                })
            }
            this.onCancelReplyComment()
        },
        onCancelReplyComment(){
            this.showReplyComment = false
            this.contentRepplyComment = ""
            this.replyParent = false
            this.replyComment = null
        },
        onEditCommentParent(data){
            this.comment_info.showEdit = true
        },
        onImshowEditCommentParent(){
            this.comment_info.showEdit = false
        },
        onSubmitUpdateCommentParent(){
            let dataUpdate = {
                'name': this.comment_info.name,
                'content': this.comment_info.edit_content
            }
            this.$emit('updateComment', dataUpdate)
            this.comment_info.content = this.comment_info.edit_content
            this.onImshowEditCommentParent()
        },
        onDeleteCommentParent(data){
            this.nameDeleteComment = data.name
            this.showDialogDeleteComment = true
        },
        onReplyCommentChild(data){
            this.showReplyComment = true
            this.replyParent = false
            this.replyComment = data
        },
        onEditCommentChild(data){
            data.showEdit = true
        },
        onSubmitUpdateCommentChild(data){
            let dataUpdate = {
                'name': data.name,
                'content': data.edit_content
            }
            this.$emit('updateComment', dataUpdate)
            data.content = data.edit_content
            this.onImshowEditCommentChild(data)
        },
        onImshowEditCommentChild(data){
            data.showEdit = false
        },
        onDeleteCommentChild(data){
            this.nameDeleteComment = data.name
            this.showDialogDeleteComment = true
            
        },
        onConfirmDeleteComment(){
            this.$emit('deleteComment', this.nameDeleteComment)
            this.nameDeleteComment = ""
            this.showDialogDeleteComment = false
        },
        onShowListReplies(){
            this.showListReplies = !this.showListReplies
        }
    },
    computed: {
        user_reply(){
            let arrUserReply = []
            for(let i = 0; i < this.comment_info.children.length; i++){
                let itemReply = this.comment_info.children[i]
                if(arrUserReply.indexOf(itemReply.owner) < 0){
                    arrUserReply.push(itemReply.owner)
                    if(arrUserReply.length == 3) break
                }
            }
            return arrUserReply
        },
        num_user_reply(){
            let arr_user = []
            for(let i = 0; i < this.comment_info.children.length; i++){
                if(arr_user.indexOf(this.comment_info.children[i].owner) < 0) arr_user.push(this.comment_info.children[i].owner)
            }
            if(arr_user.length <= 3) return 0
            return arr_user.length - 3
        }
    },
    updated(){
        let line_comment = document.getElementById(`line_comment_${this.comment_info.name}`)
        if(this.comment_info.children.length > 0 && this.showListReplies){
            setTimeout(() => {
                let lengthComment = this.comment_info.children.length
                let lastItem = this.comment_info.children[lengthComment - 1]
                if(document.getElementById(`comment_child_${lastItem.name}`) != null){
                    let heighLastItem = document.getElementById(`comment_child_${lastItem.name}`).offsetHeight
                    line_comment.style.height = `calc(100% - ${heighLastItem + 20}px)`
                }
            }, 50);
            
        }
    }
}
</script>

<style scoped>
</style>