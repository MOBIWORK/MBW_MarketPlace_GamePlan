<template>
    <div class="w-full h-full relative">
        <div class="flex items-center" :class="[show_label? 'justify-between' : 'justify-end']">
            <div class="text-lg font-semibold" v-if="show_label">{{__('Comment')}}</div>
            <Button variant="solid" theme="gray" @click="onShowNewComment()">
                <template #prefix><LucidePlus class="h-4 w-4" /></template>
                {{__('New comment')}}
          </Button>
        </div>
        <div :class="[showNewComment? 'contain-new-comment' : 'without-new-comment']">
            <div class="mb-3" v-for="comment in comments">
                <CommentItem :comment_info="comment" @replyCommentParent="(evt) => onReplyCommentParent(evt)"
                    @replyCommentChild="(evt) => onReplyCommentChild(evt)" @deleteComment="(evt) => onDeleteComment(evt)"
                    @updateComment="(evt) => onUpdateComment(evt)"></CommentItem>
            </div>
        </div>
        <div class="absolute h-32 inset-x-0 bottom-0" v-if="showNewComment">
            <CommentReplyEditor
                :value="contentAddComment"
                @change="contentAddComment = $event"
                :submitButtonProps="{
                    onClick: () => onSubmitCommnet()
                }"
                :discardButtonProps="{
                    onClick: () => onImshowAddComment(),
                }"
                />
        </div>
    </div>
</template>

<script>
import{
    Button
} from 'frappe-ui'
import CommentItem from '@/components/Comment/CommentItem.vue'
import CommentReplyEditor from '@/components/Comment/CommentReplyEditor.vue'

export default{
    name: "CommentList",
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
        CommentReplyEditor
    ],
    resources: {
        doc_comment(){
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
                transform(data){
                    let arr = []
                    let arr_child = []
                    for(let i = 0; i < data.length; i++){
                        if(data[i].doc_parent != null && data[i].doc_parent != ""){
                            arr_child.push(data[i])
                        }else{
                            data[i]["children"] = []
                            arr.push(data[i])
                        }
                    }
                    for(let i = 0; i < arr_child.length; i++){
                        for(let j = 0; j < arr.length; j++){
                            if(arr_child[i].root_name == arr[j].name){
                                arr[j].children.push(arr_child[i])
                            }
                        }
                    }
                    return arr
                },
                runDocMethod: {
                    onSuccess(){
                        this.$resources.doc_comment.fetch()
                    }
                },
                setValue: {
                    onSuccess(){
                        this.$resources.doc_comment.fetch()
                    }
                },
                insert: {
                    onSuccess(){
                        this.onImshowAddComment()
                    }
                }
            }
        }
    },
    data(){
        return {
            showNewComment: false,
            contentAddComment: ""
        }
    },
    methods: {
        onShowNewComment(){
            this.showNewComment = true
        },
        onReplyCommentParent(data){
            this.$resources.doc_comment.insert.submit({
                'content': data.content,
                'reference_doctype': this.doctype,
                'reference_name': this.reference_name,
                'doc_parent': data.parent,
                'reply_child': 0,
                'root_name': data.root_name
            })
        },
        onReplyCommentChild(data){
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
        onDeleteComment(data){
            this.$resources.doc_comment.runDocMethod.submit({
                method: 'delete_comment',
                name: data
            })
        },
        onUpdateComment(data){
            this.$resources.doc_comment.setValue.submit({
                name: data.name,
                content: data.content
            })
        },
        onSubmitCommnet(){
            this.$resources.doc_comment.insert.submit({
                'content': this.contentAddComment,
                'reference_doctype': this.doctype,
                'reference_name': this.reference_name
            })
        },
        onImshowAddComment(){
            this.showNewComment = false
            this.contentAddComment = ""
        }
    },
    computed: {
        comments(){
            return this.$resources.doc_comment.data
        }
    }
}
</script>

<style scoped>
    .contain-new-comment{
        height: calc(100% - 170px);
        overflow-y: auto;
    }
    .without-new-comment{
        height: calc(100% - 16px);
    }
</style>