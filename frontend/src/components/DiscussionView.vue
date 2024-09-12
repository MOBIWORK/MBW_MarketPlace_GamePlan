<template>
  <div class="relative flex h-full flex-col" v-if="postId && discussion">
    <div class="mx-auto w-full relative h-full">
      <div class="pt-6">
        <div class="flex items-start justify-between space-x-1 min-w-0">
          <div v-if="editingTitle" class="w-full">
            <div class="mb-2">
              <input
                v-if="editingTitle"
                type="text"
                class="w-full rounded border-0 bg-gray-100 px-2 py-1 text-xl font-semibold focus:ring-0"
                ref="title"
                v-model="discussion.title"
                :placeholder="__('Title')"
                @keydown.enter="
                  () => {
                    $resources.discussion.setValue
                      .submit({ title: discussion.title })
                      .then(() => this.updateUrlSlug())
                    editingTitle = false
                  }
                "
                @keydown.esc="
                  () => {
                    $resources.discussion.reload()
                    editingTitle = false
                  }
                "
                v-focus
              />
              <p class="mt-1 text-sm text-gray-600">
                {{__('Edit title and press enter. Press escape to cancel.')}}
              </p>
            </div>
          </div>
          <h1 v-else class="flex items-center text-2xl font-semibold truncate">
            <Tooltip
              v-if="discussion.closed_at"
              :text="__('This discussion is closed')"
            >
              <LucideLock
                class="mr-2 h-4 w-4 text-gray-700"
                :stroke-width="2"
              />
            </Tooltip>
            <span>
              {{ discussion.title }}
            </span>
          </h1>
          <Dropdown
            class="ml-auto"
            placement="right"
            :button="{
              icon: 'more-horizontal',
              variant: 'ghost',
              label: __('Discussion Options')
            }"
            :options="actions"
          />
        </div>
        <div class="mt-1.5 flex items-center text-base" v-show="!editingTitle">
          <DiscussionBreadcrumbs :discussion="discussion" />
          <span class="px-1.5">&middot;</span>
          <span class="text-gray-600">
            {{
              discussion.participants_count == 1
                ? __('1 participant')
                : `${discussion.participants_count} ${__('participants')}`
            }}
          </span>
        </div>
        
        <template v-if="discussion.conclusion != '' && discussion.conclusion != null">
          <div class="flex mt-4">
            <div class="text-1xl font-semibold">Conclusion</div>
            <div class="ml-auto flex space-x-2">
            <Button
              v-if="!readOnlyMode"
              variant="ghost"
              @click="onEditConclusion"
              :label="__('Edit conclusion')"
            >
              <template #icon><LucideEdit class="w-4" /></template>
            </Button>
            <Button
              v-if="!readOnlyMode"
              variant="ghost"
              class="ml-0"
              @click="onDeleteConclusion"
              :label="__('Delete conclusion')"
            >
              <template #icon><LucideTrash2 class="w-4 " style="color: red;" /></template>
            </Button>
          </div>
          </div>
          <TextEditor
            class="mb-4 border-b pb-3"
            editor-class="rounded-b-lg max-w-[unset] prose-sm overflow-auto w-100"
            :content="discussion.conclusion"
            :editable="false"
          ></TextEditor>
        </template>

        <div v-if="discussion.content != '' && discussion.content != null" class="text-1xl font-semibold mb-2 mt-3">Content</div>
        <div class="mb-2 flex w-full items-center mt-2">
          <UserProfileLink class="mr-3" :user="discussion.owner">
            <UserAvatar :user="discussion.owner" />
          </UserProfileLink>
          <div class="flex flex-col md:block">
            <UserProfileLink
              class="text-base font-medium hover:text-blue-600"
              :user="discussion.owner"
            >
              {{ $user(discussion.owner).full_name }}
              <span class="hidden md:inline">&nbsp;&middot;&nbsp;</span>
            </UserProfileLink>
            <time
              class="text-base text-gray-600"
              :datetime="discussion.creation"
              :title="$dayjs(discussion.creation)"
            >
              {{ $dayjs(discussion.creation).fromNow() }}
            </time>
          </div>
          <div class="ml-auto flex space-x-2">
            <Button
              v-if="!readOnlyMode && !editingContent"
              variant="ghost"
              @click="editingContent = true"
              :label="__('Edit Post')"
            >
              <template #icon><LucideEdit class="w-4" /></template>
            </Button>
          </div>
        </div>

        <div
          v-show="discussion.content != '' && discussion.content != null"
          :class="{
            'rounded-lg border p-4 focus-within:border-gray-400':
              editingContent,
          }"
        >
          <CommentEditor
            :value="discussion.content"
            @change="discussion.content = $event"
            :submitButtonProps="{
              variant: 'solid',
              onClick: () => {
                $resources.discussion.setValue.submit({
                  content: discussion.content,
                })
                editingContent = false
              },
              loading: $resources.discussion.setValue.loading,
            }"
            :discardButtonProps="{
              onClick: () => {
                editingContent = false
                $resources.discussion.reload()
              },
            }"
            :editable="editingContent"
          />
        </div>
        <div class="mt-2 mb-3">
          <Reactions
            doctype="GP Discussion"
            :name="discussion.name"
            v-model:reactions="discussion.reactions"
          />
        </div>

        <div class="w-full mb-6 mt-1">
          <Connection ref="lst_connection" :reference_doctype="'GP Discussion'" :reference_name="discussion.name" :project="discussion.project"
            :readOnly="readOnlyMode">
          </Connection>
        </div>

        <div class="text-1xl font-semibold mb-2">Activity</div>
        <div class="flex items-center">
          <span class="text-sm">{{__('Show')}}:</span>
          <!-- <div class="ml-4 mbw-bg-activity mbw-text-activity rounded px-2 py-1 cursor-pointer" :class="{'mbw-activity-active':activeActivity=='all'}" @click="activeActivity='all'">All</div> -->
          <div class="ml-2 mbw-bg-activity mbw-text-activity rounded px-2 py-1 cursor-pointer" :class="{'mbw-activity-active':activeActivity=='comment'}" @click="activeActivity='comment'">Comments</div>
          <div class="ml-2 mbw-bg-activity mbw-text-activity rounded px-2 py-1 cursor-pointer" :class="{'mbw-activity-active':activeActivity=='history'}" @click="activeActivity='history'">History</div>
        </div>
      </div>
      <!-- <template v-if="activeActivity=='all'">
        <CommentsArea
          doctype="GP Discussion"
          :name="discussion.name"
          :newCommentsFrom="discussion.last_unread_comment"
          :read-only-mode="readOnlyMode"
          :disable-new-comment="discussion.closed_at"
        />
      </template> -->
      <template v-if="activeActivity=='comment'">
        <CommentListDiscussion :doctype="'GP Discussion'" :reference_name="postId" :show_label="false" :enable_add_comment="!discussion.closed_at"></CommentListDiscussion>
        
        <!-- <CommentsArea
          doctype="GP Discussion"
          :name="discussion.name"
          :newCommentsFrom="discussion.last_unread_comment"
          :read-only-mode="false"
          :disable-new-comment="discussion.closed_at"
          :filterType="'comment'"
        /> -->
      </template>
      <template v-if="activeActivity=='history'">
        <CommentsArea
          doctype="GP Discussion"
          :name="discussion.name"
          :newCommentsFrom="false"
          :read-only-mode="readOnlyMode"
          :disable-new-comment="true"
          :filterType="'history'"
        />
      </template>
      <Dialog
        :options="{
          title: __('Move discussion to another project'),
        }"
        @close="
          () => {
            discussionMoveDialog.project = null
            $resources.discussion.moveToProject.reset()
          }
        "
        v-model="discussionMoveDialog.show"
      >
        <template #body-content>
          <Autocomplete
            :options="projectOptions"
            v-model="discussionMoveDialog.project"
            :placeholder="__('Select a project')"
          />
          <ErrorMessage
            class="mt-2"
            :message="$resources.discussion.moveToProject.error"
          />
        </template>
        <template #actions>
          <Button
            class="w-full"
            variant="solid"
            :loading="$resources.discussion.moveToProject.loading"
            @click="
              $resources.discussion.moveToProject.submit({
                project: discussionMoveDialog.project?.value,
              })
            "
          >
            {{
              discussionMoveDialog.project
                ? `${__('Move to')} ${discussionMoveDialog.project.label}`
                : __('Move')
            }}
          </Button>
        </template>
      </Dialog>
      <RevisionsDialog
        v-model="showRevisionsDialog"
        doctype="GP Discussion"
        :name="discussion.name"
        fieldname="content"
      />

      <Dialog
        :options="{
          title: __('Pin discussion'),
          message: __('When a discussion is pinned, it shows up on top of the discussion list in {0}. Do you want to pin this discussion?', [
            projectDiscussion.title
          ]),
          icon: { name: 'arrow-up-left' },
          actions: [
            {
              label: __('Pin'),
              onClick: ({ close }) =>
                this.$resources.discussion.pinDiscussion.submit().then(() => {
                  showPinDiscussionDialog = false;
                }),
                variant: 'solid',
            },
          ],
        }"
        v-model="showPinDiscussionDialog"
      />
      <Dialog
        :options="{
          title: __('Unpin discussion'),
          message: __(`Do you want to unpin this discussion?`),
          icon: { name: 'arrow-down-left' },
          actions: [
            {
              label: __('Unpin'),
              onClick: ({ close }) =>
                    this.$resources.discussion.unpinDiscussion
                      .submit()
                      .then(() => {showUnPinDiscussionDialog = false;}),
                  variant: 'solid',
            },
          ],
        }"
        v-model="showUnPinDiscussionDialog"
      />
      <Dialog v-model="showCloseDiscussionDialog" :options="{
        size: '2xl',
      }">
        <template #body-title>
          <div class="flex w-full items-center">
            <UserProfileLink class="mr-2" :user="idSessionUser">
              <UserAvatar :user="idSessionUser" />
            </UserProfileLink>
            <UserProfileLink
              class="text-base font-medium hover:text-blue-600"
              :user="idSessionUser"
            >
              {{ fullNameSessionUser }}
            </UserProfileLink>
          </div>
        </template>
        <template #body-content>
          <TextEditor
            class="mt-1"
            editor-class="rounded-b-lg max-w-[unset] prose-sm h-60 overflow-auto w-100"
            :content="content"
            @change="onNewPostChange"
            :placeholder="__('Add a conclusion')"
          >
            <template v-slot:bottom>
              <div
                class="mt-2 flex flex-col justify-between sm:flex-row sm:items-center"
              >
                <TextEditorFixedMenu
                  class="overflow-x-auto"
                  :buttons="textEditorMenuButtons"
                />
              </div>
            </template>
          </TextEditor>
        </template>
        <template #actions>
          <div class="flex justify-end -pt-6">
            <Button @click="showCloseDiscussionDialog = false">
              Discard
            </Button>
            <Button class="ml-2" variant="solid" @click="onSubmitConclusion">
              Submit
            </Button>
          </div>
        </template>
      </Dialog>
      <Dialog
        :options="{
          title: __('Re-open discussion'),
          message: __('Do you want to re-open this discussion? Anyone can comment on it again.'),
          icon: { name: 'unlock' },
          actions: [
            {
              label: __('Re-open'),
              onClick: ({ close }) =>
                this.$resources.discussion.reopenDiscussion
                      .submit()
                      .then(() => {showReopenDiscussionDialog = false}),
              variant: 'solid',
            },
          ],
        }"
        v-model="showReopenDiscussionDialog"
      />
      <Dialog
        :options="{
          title: __('Delete discussion'),
          message: __('This action can not be undone'),
          actions: [
          {
              label: __('Delete'),
              onClick: () => onDeleteDiscussion(),
              variant: 'solid',
              theme: 'red',
            },
            {
              label: __('Cancel'),
            },
          ],
        }"
        v-model="showDeleteDiscussionDialog"
      />
      <Dialog
        :options="{
          title: __('Delete conclusion'),
          message: __('This action can not be undone'),
          actions: [
          {
              label: __('Delete'),
              onClick: () => onAcceptDeleteConclusion(),
              variant: 'solid',
              theme: 'red',
            },
            {
              label: __('Cancel'),
            },
          ],
        }"
        v-model="showDeleteConclusionDialog"
      />
      <NewTaskDialog ref="newTaskDialog" />
    </div>
  </div>
</template>
<script>
import { Autocomplete, Dropdown, Dialog, Tooltip } from 'frappe-ui'
import Reactions from './Reactions.vue'
import CommentsArea from '@/components/CommentsArea.vue'
import CommentEditor from './CommentEditor.vue'
import TextEditor from '@/components/TextEditor.vue'
import UserProfileLink from './UserProfileLink.vue'
import DiscussionMeta from './DiscussionMeta.vue'
import DiscussionBreadcrumbs from './DiscussionBreadcrumbs.vue'
import RevisionsDialog from './RevisionsDialog.vue'
import { focus } from '@/directives'
import { copyToClipboard } from '@/utils'
import { activeTeams } from '@/data/teams'
import { getTeamProjects } from '@/data/projects'
import { getUser } from '@/data/users'
import TextEditorFixedMenu from 'frappe-ui/src/components/TextEditor/TextEditorFixedMenu.vue'
import Connection from '@/components/Connection.vue'
import CommentListDiscussion from '@/components/CommentDiscussion/CommentListDiscussion.vue'

export default {
  name: 'DiscussionView',
  props: ['postId', 'readOnlyMode'],
  directives: {
    focus,
  },
  components: {
    TextEditor,
    Reactions,
    CommentsArea,
    Dropdown,
    Dialog,
    Autocomplete,
    UserProfileLink,
    CommentEditor,
    Tooltip,
    DiscussionMeta,
    DiscussionBreadcrumbs,
    RevisionsDialog,
    TextEditorFixedMenu,
    Connection,
    CommentListDiscussion
  },
  resources: {
    discussion() {
      return {
        type: 'document',
        doctype: 'GP Discussion',
        name: this.postId,
        realtime: true,
        whitelistedMethods: {
          trackVisit: 'track_visit',
          closeDiscussion: 'close_discussion',
          reopenDiscussion: 'reopen_discussion',
          pinDiscussion: 'pin_discussion',
          unpinDiscussion: 'unpin_discussion',
          deleteDiscussion: 'delete_discussion',
          updateConclusion: 'update_conclusion',
          moveToProject: {
            method: 'move_to_project',
            validate(params) {
              if (!params.args.project) {
                return 'Project is required to move this discussion'
              }
            },
            onError() {
              this.discussionMoveDialog.show = true
            },
            onSuccess() {
              this.onDiscussionMove()
            },
          }
        },
        onSuccess(doc) {
          this.updateUrlSlug()
          if (
            !this.$route.query.comment &&
            !this.$route.query.poll &&
            !this.$route.query.fromSearch &&
            (doc.last_unread_comment || doc.last_unread_poll)
          ) {
            this.$router.replace({
              query: {
                comment: doc.last_unread_comment || undefined,
                poll: doc.last_unread_poll || undefined,
              },
            })
          }

          if (
            this.$route.name === 'ProjectDiscussion' &&
            Number(this.$route.params.postId) === doc.name
          ) {
            this.$resources.discussion.trackVisit.submit()
          }
        },
      }
    },
  },
  data() {
    return {
      editingContent: false,
      editingTitle: false,
      discussionMoveDialog: {
        show: false,
        project: null,
      },
      showRevisionsDialog: false,
      showNavbar: false,
      showPinDiscussionDialog: false,
      projectDiscussion: {},
      showUnPinDiscussionDialog: false,
      showCloseDiscussionDialog: false,
      showReopenDiscussionDialog: false,
      showDeleteDiscussionDialog: false,
      idSessionUser: getUser('sessionUser').name,
      fullNameSessionUser: getUser('sessionUser').full_name,
      content: '',
      showDeleteConclusionDialog: false,
      activeActivity: 'comment',
      newTaskDialog: null,
      lst_connection: null
    }
  },
  methods: {
    copyLink() {
      let location = window.location
      let url = `${location.origin}${location.pathname}`
      copyToClipboard(url)
    },
    onDiscussionMove() {
      this.$nextTick(() => {
        this.discussionMoveDialog.show = false
        this.discussionMoveDialog.project = null

        this.$router.replace({
          name: 'ProjectDiscussion',
          params: {
            teamId: this.discussion.team,
            projectId: this.discussion.project,
            postId: this.discussion.name,
          },
        })
      })
      this.$resources.discussion.moveToProject.reset()
    },
    updateUrlSlug() {
      let doc = this.discussion
      if (!this.$route.params.slug || this.$route.params.slug !== doc.slug) {
        this.$router.replace({
          name: 'ProjectDiscussion',
          params: {
            ...this.$route.params,
            slug: doc.slug,
          },
          query: this.$route.query,
        })
      }
    },
    onPinDiscussion(){
      this.projectDiscussion = this.$getDoc('GP Project', this.discussion.project);
      this.showPinDiscussionDialog = true;
    },
    onDeleteDiscussion(){
      let me = this;
      this.$resources.discussion.deleteDiscussion
                    .submit()
                    .then(() => {
                      me.$router.push({ name: 'ProjectDiscussions' })
                    })
    },
    onSubmitConclusion(){
      let me = this;
      this.$resources.discussion.updateConclusion.submit({
        conclusion: this.content
      }).then(() => {
        me.showCloseDiscussionDialog = false;
      })
    },
    onNewPostChange(value) {
      this.content = value
    },
    onEditConclusion(){
      this.content = this.discussion.conclusion;
      this.showCloseDiscussionDialog = true;
    },
    onDeleteConclusion(){
      this.showDeleteConclusionDialog = true;
    },
    onAcceptDeleteConclusion(){
      let me = this;
      this.$resources.discussion.updateConclusion.submit({
        conclusion: ""
      }).then(() => {
        me.showDeleteConclusionDialog = false;
      })
    }
  },
  computed: {
    discussion() {
      return this.$resources.discussion.doc
    },
    projectOptions() {
      return activeTeams.value.map((team) => ({
        group: team.title,
        items: getTeamProjects(team.name).map((project) => ({
          label: project.title,
          value: project.name,
        })),
      }))
    },
    actions() {
      return [
        {
          label: __('Edit Title'),
          icon: 'edit',
          condition: () => !this.readOnlyMode,
          onClick: () => {
            this.editingTitle = true
          },
        },
        {
          label: __('Revisions'),
          icon: 'rotate-ccw',
          onClick: () => (this.showRevisionsDialog = true),
        },
        {
          label: __('Copy link'),
          icon: 'link',
          onClick: this.copyLink,
        },
        {
          label: __('Pin discussion...'),
          icon: 'arrow-up-left',
          condition: () => !this.discussion.pinned_at && !this.readOnlyMode,
          onClick: this.onPinDiscussion
        },
        {
          label: __('Unpin discussion...'),
          icon: 'arrow-down-left',
          condition: () => this.discussion.pinned_at && !this.readOnlyMode,
          onClick: () => {
            this.showUnPinDiscussionDialog = true;
          },
        },
        {
          label: __('Close discussion...'),
          icon: 'lock',
          condition: () => !this.discussion.closed_at && !this.readOnlyMode,
          onClick: () => {
            this.$resources.discussion.closeDiscussion.submit();
            this.content = this.discussion.conclusion;
            this.showCloseDiscussionDialog = true;
          },
        },
        {
          label: __('Re-open discussion...'),
          icon: 'unlock',
          condition: () => this.discussion.closed_at && !this.readOnlyMode,
          onClick: () => {
            this.showReopenDiscussionDialog = true;
          },
        },
        {
          label: __('Move to...'),
          icon: 'log-out',
          condition: () => !this.readOnlyMode,
          onClick: () => {
            this.discussionMoveDialog.show = true
          },
        },
        {
          label: __('Add task'),
          icon: 'activity',
          condition: () => !this.readOnlyMode,
          onClick: () => {
            let me = this;
            this.$refs.newTaskDialog.show({
              defaults: {
                project: this.discussion.project,
                assigned_to: getUser('sessionUser').name,
              },
              onSuccess: (data) => {
                me.$refs.lst_connection.onCreateConnectionByTask(data.name)
              },
            })
          },
        },
        {
          label: __('Delete'),
          icon: 'trash-2',
          condition: () => !this.readOnlyMode,
          onClick: () => {
            this.showDeleteDiscussionDialog = true;
          }
        },
        {
          label: __('Add conclusion'),
          icon: 'plus',
          condition: () => !this.readOnlyMode,
          onClick: () => {
            this.content = this.discussion.conclusion;
            this.showCloseDiscussionDialog = true;
          }
        }
      ]
    },
    textEditorMenuButtons() {
      return [
        'Paragraph',
        ['Heading 2', 'Heading 3', 'Heading 4', 'Heading 5', 'Heading 6'],
        'Separator',
        'Bold',
        'Italic',
        'Separator',
        'Bullet List',
        'Numbered List',
        'Separator',
        'Align Left',
        'Align Center',
        'Align Right',
        'FontColor',
        'Separator',
        'Image',
        'Video',
        'Link',
        'Blockquote',
        'Code',
        'Horizontal Rule',
        [
          'InsertTable',
          'AddColumnBefore',
          'AddColumnAfter',
          'DeleteColumn',
          'AddRowBefore',
          'AddRowAfter',
          'DeleteRow',
          'MergeCells',
          'SplitCell',
          'ToggleHeaderColumn',
          'ToggleHeaderRow',
          'ToggleHeaderCell',
          'DeleteTable',
        ],
        'Separator',
        'Undo',
        'Redo',
      ]
    },
  },
  pageMeta() {
    if (!this.discussion) return
    let project = this.$getDoc('GP Project', this.discussion.project)
    if (!project) return
    return {
      title: [this.discussion.title, project.title].filter(Boolean).join(' - '),
      emoji: project.icon,
    }
  },
}
</script>
<style scoped>
  .mbw-bg-activity{
    background-color: #091E420F;
  }
  .mbw-bg-activity:hover{
    background-color: #67402a2c;
  }
  .mbw-activity-active{
    color: #0C66E4 !important;
    background-color: #E9F2FF !important;
  }
  .mbw-text-activity{
    font-weight: 500;
    font-size: 14px;
    font-style: normal;
    font-family: inherit;
    text-align: center;
    color: #172B4D;
  }
</style>