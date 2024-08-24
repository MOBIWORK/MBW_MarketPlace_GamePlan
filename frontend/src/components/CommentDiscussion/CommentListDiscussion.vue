<template>
    <div class="w-full relative max-h-[627px]">
        <div class="flex items-center" :class="[show_label ? 'justify-between' : 'justify-end']">
            <div class="text-lg font-semibold" v-if="show_label">{{ __('Comment') }}</div>
            <Button variant="solid" theme="gray" @click="onShowNewComment()">
                <template #prefix>
                    <LucidePlus class="h-4 w-4" />
                </template>
                {{ __('New comment') }}
            </Button>
        </div>
        <div :class="[showNewComment ? 'contain-new-comment' : 'without-new-comment']" class="max-h-[600px] min-h-[600px] overflow-y-auto" style="scrollbar-width: none;">
            <div class="mb-3" v-for="comment in comments">
                <PollDiscussion v-if="comment.doctype == 'GP Poll'" class="border-b"
                    :ref="($poll) => setItemRef($poll, comment)" :poll="comment" :readOnlyMode="true" />
                <CommentItem v-else :comment_info="comment" @replyCommentParent="(evt) => onReplyCommentParent(evt)"
                    @replyCommentChild="(evt) => onReplyCommentChild(evt)"
                    @deleteComment="(evt) => onDeleteComment(evt)" @updateComment="(evt) => onUpdateComment(evt)">
                </CommentItem>
            </div>
        </div>
    </div>
    <div v-show="showNewComment"
        class="w-full rounded-lg border bg-white p-4 focus-within:border-gray-400 absolute bottom-1">
        <div class="mb-4 flex items-center">
            <UserAvatar :user="$user().name" size="sm" />
            <span class="ml-2 text-base font-medium text-gray-900">
                {{ $user().full_name }}
            </span>
            <TabButtons class="ml-auto" :buttons="[{ label: __('Comment') }, { label: 'Poll' }]"
                v-model="newCommentType" />
        </div>
        <ErrorMessage :message="$resources.polls.insert.error" />
        <CommentReplyEditor v-if="newCommentType == 'Comment'" :value="contentAddComment"
            @change="contentAddComment = $event" :submitButtonProps="{
                onClick: () => onSubmitCommnet()
            }" :discardButtonProps="{
                    onClick: () => onImshowAddComment(),
                }" />
        <PollEditor v-show="newCommentType == 'Poll'" v-model:poll="newPoll" :submitButtonProps="{
            onClick: submitPoll,
            loading: $resources.polls.insert.loading,
        }" :discardButtonProps="{
                onClick: discardPoll,
            }" />
    </div>
</template>

<script>
import {
    Button
} from 'frappe-ui'
import CommentItem from '@/components/Comment/CommentItem.vue'
import CommentReplyEditor from '@/components/Comment/CommentReplyEditor.vue'
import PollEditor from '@/components/PollEditor.vue'
import TabButtons from '@/components/frappe-ui/TabButtons.vue'
import PollDiscussion from './PollDiscussion.vue'

export default {
    name: "CommentListDiscussion",
    props: {
        doctype: {
            type: String
        },
        reference_name: {
            type: String
        },
        show_label: {
            type: Boolean,
            default: true
        }
    },
    components: [
        Button,
        CommentItem,
        CommentReplyEditor,
        PollEditor,
        TabButtons,
        PollDiscussion
    ],
    resources: {
        doc_comment() {
            return {
                type: 'list',
                doctype: 'GP Comment',
                fields: [
                    'name',
                    'content',
                    'owner',
                    'creation',
                    'modified',
                    'deleted_at',
                    'doc_parent',
                    'reply_child',
                    'reply_child_user',
                    'root_name',
                    { reactions: ['name', 'user', 'emoji'] }
                ],
                filters: {
                    reference_doctype: this.doctype,
                    reference_name: this.reference_name,
                },
                auto: true,
                orderBy: 'creation desc',
                pageLength: 99999,
                transform(data) {
                    let arr = []
                    let arr_child = []
                    for (let i = 0; i < data.length; i++) {
                        if (data[i].doc_parent != null && data[i].doc_parent != "") {
                            arr_child.push(data[i])
                        } else {
                            data[i]["children"] = []
                            arr.push(data[i])
                        }
                    }
                    for (let i = 0; i < arr_child.length; i++) {
                        for (let j = 0; j < arr.length; j++) {
                            if (arr_child[i].root_name == arr[j].name) {
                                arr[j].children.push(arr_child[i])
                            }
                        }
                    }
                    return arr
                },
                runDocMethod: {
                    onSuccess() {
                        this.$resources.doc_comment.fetch()
                    }
                },
                setValue: {
                    onSuccess() {
                        this.$resources.doc_comment.fetch()
                    }
                },
                insert: {
                    onSuccess() {
                        this.onImshowAddComment()
                    }
                }
            }
        },
        polls() {
            return {
                type: 'list',
                doctype: 'GP Poll',
                fields: [
                    'name',
                    'title',
                    'anonymous',
                    'multiple_answers',
                    'creation',
                    'owner',
                    'stopped_at',
                    { options: ['name', 'title', 'idx', 'percentage'] },
                    { votes: ['user', 'option'] },
                    { reactions: ['name', 'user', 'emoji'] },
                ],
                filters: {
                    discussion: this.reference_name,
                },
                orderBy: 'creation desc',
                auto: true,
                pageLength: 99999,
                transform(data) {
                    for (let d of data) {
                        d.doctype = 'GP Poll'
                    }
                    return data
                },
                onSuccess() {
                    if (this.$route.query.poll) {
                        let poll = this.$resources.polls.getRow(this.$route.query.poll)
                        this.scrollToItem(poll)
                    }
                },
            }
        }
    },
    data() {
        return {
            showNewComment: false,
            contentAddComment: "",
            newCommentType: 'Comment',
            newPoll: {
                title: '',
                multiple_answers: false,
                options: [
                    { title: '', idx: 1 },
                    { title: '', idx: 2 },
                ],
            }
        }
    },
    methods: {
        onShowNewComment() {
            this.showNewComment = true
        },
        onReplyCommentParent(data) {
            this.$resources.doc_comment.insert.submit({
                'content': data.content,
                'reference_doctype': this.doctype,
                'reference_name': this.reference_name,
                'doc_parent': data.parent,
                'reply_child': 0,
                'root_name': data.root_name
            })
        },
        onReplyCommentChild(data) {
            this.$resources.doc_comment.insert.submit({
                'content': data.content,
                'reference_doctype': this.doctype,
                'reference_name': this.reference_name,
                'doc_parent': data.parent,
                'reply_child': 1,
                'reply_child_user': data.user,
                'root_name': data.root_name
            })
        },
        onDeleteComment(data) {
            this.$resources.doc_comment.runDocMethod.submit({
                method: 'delete_comment',
                name: data
            })
        },
        onUpdateComment(data) {
            this.$resources.doc_comment.setValue.submit({
                name: data.name,
                content: data.content
            })
        },
        onSubmitCommnet() {
            this.$resources.doc_comment.insert.submit({
                'content': this.contentAddComment,
                'reference_doctype': this.doctype,
                'reference_name': this.reference_name
            })
        },
        onImshowAddComment() {
            this.showNewComment = false
            this.contentAddComment = ""
        },
        async scrollToItem(item) {
            if (!item) return
            await nextTick()
            if (item.$el) {
                this.highlightedItem = item
                this.scrollToElement(item.$el)
            }
            setTimeout(() => {
                this.highlightedItem = null
                this.$router.replace({ query: {} })
            }, 10000)
        },
        scrollToElement($el) {
            let scrollContainer = getScrollContainer()
            let headerHeight = 64
            let top = $el.offsetTop - scrollContainer.scrollTop - headerHeight
            scrollContainer.scrollBy({ top, left: 0, behavior: 'smooth' })
        },
        scrollToEnd() {
            let scrollContainer = getScrollContainer()
            scrollContainer.scrollTop = scrollContainer.scrollHeight
        },
        submitPoll() {
            if (this.doctype !== 'GP Discussion') return
            return this.$resources.polls.insert.submit(
                {
                    ...this.newPoll,
                    discussion: this.reference_name,
                },
                {
                    onSuccess() {
                        this.discardPoll()
                    },
                }
            )
        },
        discardPoll() {
            this.showNewComment = false
            this.newCommentType = "Comment"
            this.newPoll = {
                title: '',
                multiple_answers: false,
                options: [
                    { title: '', idx: 1 },
                    { title: '', idx: 2 },
                ],
            }
        },
        setItemRef($component, item) {
            if ($component?.$el) {
                item.$el = $component.$el
            }
        }
    },
    computed: {
        comments() {
            let items = []
            if (this.$resources.doc_comment.data?.length) items = items.concat(this.$resources.doc_comment.data)
            if (this.$resources.polls.data?.length) items = items.concat(this.$resources.polls.data)
            return items
        }
    }
}
</script>

<style scoped>
.contain-new-comment {
    height: calc(100% - 250px);
    overflow-y: auto;
}

.without-new-comment {
    height: calc(100% - 16px);
}
</style>