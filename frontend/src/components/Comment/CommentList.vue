<template>
    <div class="w-full h-full relative">
        <div class="flex items-center justify-between">
            <div class="text-lg font-semibold">{{__('Comment')}}</div>
            <Button variant="solid" theme="gray" @click="onShowNewComment()">
                <template #prefix><LucidePlus class="h-4 w-4" /></template>
                {{__('New comment')}}
          </Button>
        </div>
        <div :class="[showNewComment? 'contain-new-comment' : 'without-new-comment']">
            <div class="mb-3" v-for="comment in comments">
                <CommentItem :comment_info="comment"></CommentItem>
            </div>
        </div>
        <div class="absolute h-32 inset-x-0 bottom-0" v-if="showNewComment">
            This is create comment
        </div>
    </div>
</template>

<script>
import{
    Button
} from 'frappe-ui'
import CommentItem from '@/components/Comment/CommentItem.vue'

export default{
    name: "CommentList",
    props: {
        doctype: {
            type: String
        },
        reference_name: {
            type: String
        }
    },
    components: [
        Button,
        CommentItem
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
                            if(arr_child[i].doc_parent == arr[j].name){
                                arr[j].children.push(arr_child[i])
                            }
                        }
                    }
                    return arr
                },
                onSuccess(data){
                    console.log("Dòng 65 : ", data)
                }
            }
        }
    },
    data(){
        return {
            showNewComment: false
        }
    },
    methods: {
        onShowNewComment(){
            this.showNewComment = true
            console.log("show comment")
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
        height: calc(100% - 144px);
    }
    .without-new-comment{
        height: calc(100% - 16px);
    }
</style>