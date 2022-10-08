<template>
  <div class="flex flex-col">
    <div
      v-if="$resources.comments.data == null"
      class="flex animate-pulse items-start space-x-3 px-2 py-4 text-base"
    >
      <div class="h-8 w-8 rounded-full bg-gray-200"></div>
      <div>
        <div class="flex h-8 flex-col justify-center">
          <div class="h-2 w-40 bg-gray-200"></div>
        </div>
        <div class="flex flex-col gap-2">
          <div v-for="i in 4">
            <div
              class="h-2 bg-gray-200"
              :style="{ width: `${Math.max(Math.random() * 800, 600)}px` }"
            ></div>
          </div>
        </div>
      </div>
    </div>
    <div class="px-1 pb-20" v-if="timelineItems.length">
      <template v-for="item in timelineItems" :key="item.name">
        <div
          v-if="newMessagesFrom && newMessagesFrom == item.name"
          class="relative my-4"
          role="separator"
        >
          <div class="border-b border-blue-600"></div>
          <span
            class="absolute -top-2 left-1/2 -translate-x-1/2 bg-white px-2 text-sm font-medium text-blue-600"
          >
            New comments
          </span>
        </div>
        <Comment
          :class="{
            'border-t': item.name != newMessagesFrom,
          }"
          v-if="item.doctype == 'Team Comment'"
          :ref="($comment) => setCommentRef($comment, item)"
          :comment="item"
          :highlightedComment="highlightedComment"
          :readOnlyMode="readOnlyMode"
          :comments="$resources.comments"
        />
        <Activity
          class="border-t"
          v-else-if="item.doctype == 'Team Activity'"
          :activity="item"
        />
      </template>
    </div>

    <div
      v-if="!readOnlyMode && !disableNewComment"
      class="sticky bottom-0 mt-2 bg-white py-4"
      ref="addComment"
    >
      <button
        class="flex w-full items-center rounded-lg bg-gray-100 py-2 px-2 text-left text-base text-gray-600 hover:bg-gray-200"
        @click="showCommentBox = true"
        v-show="!showCommentBox"
      >
        <UserAvatar class="mr-3" :user="$user().name" size="sm" />
        Add a comment
      </button>
      <div
        v-show="showCommentBox"
        class="w-full rounded-lg border bg-white p-4 focus-within:border-gray-400"
        @keydown.ctrl.enter.capture.stop="submitComment"
        @keydown.meta.enter.capture.stop="submitComment"
      >
        <div class="mb-4 flex items-center space-x-2">
          <UserAvatar :user="$user().name" size="sm" />
          <span class="text-base font-medium text-gray-900">
            {{ $user().full_name }}
          </span>
        </div>
        <CommentEditor
          ref="newCommentEditor"
          :value="newComment"
          @change="onNewCommentChange"
          :submitButtonProps="{
            onClick: submitComment,
            loading: $resources.comments.insert.loading,
            disabled: commentEmpty,
          }"
          :discardButtonProps="{
            onClick: discardComment,
          }"
          :editable="showCommentBox"
          placeholder="Add a comment"
        />
      </div>
    </div>
  </div>
</template>
<script>
import { nextTick } from 'vue'
import { getScrollParent } from '@/utils'
import CommentEditor from '@/components/CommentEditor.vue'
import Comment from './Comment.vue'
import Activity from './Activity.vue'

export default {
  name: 'CommentsArea',
  props: [
    'doctype',
    'name',
    'newCommentsFrom',
    'readOnlyMode',
    'disableNewComment',
  ],
  components: {
    CommentEditor,
    Comment,
    Activity,
  },
  data() {
    let draftComment = localStorage.getItem(this.draftCommentKey())
    return {
      commentMap: {},
      showCommentBox: false,
      newComment: draftComment || '',
      newMessagesFrom: this.newCommentsFrom,
      highlightedComment: '',
    }
  },
  watch: {
    showCommentBox(val) {
      if (val) {
        nextTick(() => {
          this.$refs.newCommentEditor?.editor.commands.focus()
          this.scrollToEnd()
        })
      }
    },
  },
  mounted() {
    if (!this.$refs.newCommentEditor?.editor.isEmpty) {
      this.showCommentBox = true
    }
    this.$socket.on('new_activity', (data) => {
      if (
        data.reference_doctype == this.doctype &&
        data.reference_name == this.name
      ) {
        this.$resources.activities.reload()
      }
    })
  },
  beforeUnmount() {
    this.$socket.off('new_activity')
  },
  resources: {
    comments() {
      return {
        type: 'list',
        doctype: 'Team Comment',
        fields: [
          'name',
          'content',
          'owner',
          'creation',
          'modified',
          'deleted_at',
        ],
        transform(data) {
          for (let d of data) {
            d.doctype = 'Team Comment'
            this.commentMap[d.name] = d
            d.reactions = []
          }
          return data
        },
        filters: {
          reference_doctype: this.doctype,
          reference_name: this.name,
        },
        order_by: 'creation asc',
        limit: 99999,
        setValue: {
          onSuccess() {
            this.attachReactionsToComments()
          },
        },
        fetchOne: {
          onSuccess() {
            this.attachReactionsToComments()
          },
        },
        onSuccess(comments) {
          setTimeout(() => {
            if (this.$route.query.comment) {
              this.scrollToComment(Number(this.$route.query.comment))
            } else if (!this.$route.query.fromSearch) {
              this.scrollToEnd()
            }
          }, 300)
          this.attachReactionsToComments()
        },
      }
    },
    reactions() {
      if (!this.$resources.comments.data?.length) return
      let comments = this.$resources.comments.data.map((d) => d.name)
      return {
        type: 'list',
        doctype: 'Team Reaction',
        fields: ['user', 'emoji', 'parent'],
        filters: {
          parenttype: 'Team Comment',
          parent: ['in', comments],
        },
        parent: 'Team Comment',
        order_by: 'parent asc, idx asc',
        limit: 99999,
        onSuccess() {
          this.attachReactionsToComments()
        },
      }
    },
    activities() {
      return {
        type: 'list',
        doctype: 'Team Activity',
        fields: ['name', 'user', 'action', 'data', 'creation'],
        filters: {
          reference_doctype: this.doctype,
          reference_name: this.name,
        },
        order_by: 'creation asc',
        limit: 99999,
        transform(activities) {
          for (let activity of activities) {
            activity.doctype = 'Team Activity'
          }
          return activities
        },
      }
    },
  },
  methods: {
    submitComment() {
      if (this.commentEmpty) {
        return
      }
      this.$resources.comments.setData((data) => {
        data.push({
          owner: this.$user().name,
          content: this.newComment,
          reference_doctype: this.doctype,
          reference_name: this.name,
          loading: true,
          reactions: [],
          creation: this.$dayjs().format('YYYY-MM-DD HH:mm:ss'),
        })
        return data
      })
      this.$resources.comments.insert.submit(
        {
          reference_doctype: this.doctype,
          reference_name: this.name,
          content: this.newComment,
        },
        {
          onError(error) {
            this.$resources.comments.setData((data) => {
              let lastComment = data[data.length - 1]
              lastComment.loading = false
              lastComment.error = error
              return data
            })
            this.$toast({
              title: 'Error adding new comment',
              text: error.messages.join(', '),
              position: 'bottom-center',
              icon: 'alert-circle',
              iconClasses: 'text-red-600',
            })
          },
        }
      )
      this.resetCommentState()
    },
    scrollToComment(id) {
      if (!id) return
      let comment = this.commentMap[id]
      if (!comment) return

      this.$nextTick(() => {
        if (comment.$el?.scrollIntoView) {
          comment.$el.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
            inline: 'nearest',
          })
        }
        this.highlightedComment = id
        setTimeout(() => (this.highlightedComment = null), 10000)
      })
    },
    scrollToEnd() {
      if (window.scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    },
    discardComment() {
      if (!this.editorObject.isEmpty) {
        this.$dialog({
          title: 'Discard comment',
          message: 'Are you sure you want to discard your comment?',
          actions: [
            {
              label: 'Discard comment',
              handler: ({ close }) => {
                this.resetCommentState()
                close()
              },
              appearance: 'primary',
            },
            {
              label: 'Keep comment',
            },
          ],
        })
      } else {
        this.resetCommentState()
      }
    },
    attachReactionsToComments() {
      if (!this.$resources.reactions?.data) return
      for (let d of this.$resources.comments.data) {
        this.commentMap[d.name] = d
        d.reactions = []
      }
      for (let reaction of this.$resources.reactions.data) {
        let comment = this.commentMap[reaction.parent]
        if (comment) {
          comment.reactions.push({
            user: reaction.user,
            emoji: reaction.emoji,
          })
        }
      }
    },
    onNewCommentChange(content) {
      this.newComment = content

      // save draft comment to local storage
      setTimeout(() => {
        // set timeout to move it off main thread
        localStorage.setItem(this.draftCommentKey(), content)
      }, 0)
    },
    resetCommentState() {
      this.newComment = ''
      this.showCommentBox = false
      localStorage.removeItem(this.draftCommentKey())
    },
    draftCommentKey() {
      return `draft-comment-${this.doctype}-${this.name}`
    },
    setCommentRef($comment, comment) {
      if ($comment?.$el) {
        comment.$el = $comment.$el
      }
    },
  },
  computed: {
    timelineItems() {
      let items = []
      if (this.$resources.comments.data?.length) {
        items = items.concat(this.$resources.comments.data)
      }
      if (this.$resources.activities.data?.length) {
        items = items.concat(this.$resources.activities.data)
      }
      return items.sort((a, b) => {
        return new Date(a.creation) - new Date(b.creation)
      })
    },
    commentEmpty() {
      return !this.newComment || this.newComment === '<p></p>'
    },
    editorObject() {
      return this.$refs.newCommentEditor?.editor
    },
  },
}
</script>