<template>
  <div>
    <header
      class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5"
    >
      
      <div class="flex items-center space-x-2">
        <span class="hidden text-sm text-gray-600 sm:block" v-if="page.doc">
          {{__('Last updated')}} {{ $dayjs(page.doc.modified).format('LLL') }}
        </span>
        <Button
          v-show="page.doc && page.isDirty && !readOnlyControl"
          variant="solid"
          @click="save"
          :loading="page.save.loading"
        >
          {{__('Save')}}
        </Button>
      </div>
    </header>
    <div class="mx-auto w-full px-5">
      <div class="py-6" v-if="page.doc">
        <span class="text-sm text-gray-600 sm:hidden">
          {{__('Last updated')}} {{ $dayjs(page.doc.modified).format('LLL') }}
        </span>
        <div class="mb-2">
          <input
            class="w-full border-0 p-0 pt-4 text-3xl font-semibold focus:outline-none focus:ring-0"
            type="text"
            :value="page.doc.title"
            @input="page.doc.title = $event.target.value"
            @keydown.enter="$refs.content.editor.commands.focus()"
            ref="titleInput"
            :readonly="readOnlyControl"
          />
        </div>
        <TextEditor
            editor-class="rounded-b-lg max-w-[unset] prose-sm h-mbw-fit-page overflow-y-auto"
            :content="page.doc.content"
            @change="page.doc.content = $event"
            :placeholder="!readOnlyControl? __('Start writing here...') : ''"
            ref="content"
            :editable="!readOnlyControl"
          >
            <template v-if="!readOnlyControl" v-slot:bottom>
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
      </div>
    </div>
  </div>
</template>
<script>
import { Breadcrumbs, getCachedDocumentResource } from 'frappe-ui'
import { getTeam, getTeamInfo } from '@/data/teams'
import { getProject } from '@/data/projects'
import TextEditor from '@/components/TextEditor.vue'
import TextEditorFixedMenu from 'frappe-ui/src/components/TextEditor/TextEditorFixedMenu.vue'
import { getUser } from '@/data/users'

export default {
  name: 'Page',
  props: ['pageId', 'slug'],
  components: { TextEditor, Breadcrumbs, TextEditorFixedMenu },
  resources: {
    page() {
      return {
        type: 'document',
        doctype: 'GP Page',
        name: this.pageId,
        onSuccess(data) {
          this.updateUrlSlug()
          this.$nextTick(() => {
            this.$refs.titleInput?.focus()
          })
        },
      }
    },
    permission_page(){
      return {
        url: "gameplan.api.permission_page",
        method: "GET",
        params: {
          page: this.pageId
        },
        auto: true
      }
    }
  },
  mounted() {
    document.addEventListener('keydown', this.handleKeyboardShortcuts)
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeyboardShortcuts)
  },
  methods: {
    handleKeyboardShortcuts(e) {
      if (e.key === 's' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        this.save()
      }
    },
    save() {
      this.page.save.submit(null, {
        onSuccess() {
          this.updateUrlSlug()
        },
      })
    },
    updateUrlSlug() {
      if (
        !this.$route.params.slug ||
        this.$route.params.slug !== this.page.doc.slug
      ) {
        this.$router.replace({
          name: this.page.doc.project ? 'ProjectPage' : 'Page',
          params: {
            ...this.$route.params,
            slug: this.page.doc.slug,
          },
          query: this.$route.query,
        })
      }
    }
  },
  computed: {
    page() {
      return this.$resources.page
    },
    isDirty() {
      if (!this.page.doc) return false
      return (
        this.page.doc.title !== this.title ||
        this.page.doc.content !== this.content
      )
    },
    breadcrumbs() {
      if (!this.page.doc) return []
      if (!this.page.doc.project) {
        return [
          { label: __('My Pages'), route: { name: 'MyPages' } },
          {
            label: this.pageTitle,
            route: {
              name: 'Page',
              params: { pageId: this.pageId, slug: this.slug },
            },
          },
        ]
      }
      let team = getTeam(this.page.doc.team)
      let project = getProject(this.page.doc.project)

      if (!(team && project)) return []
      return [
        {
          label: team.title,
          icon: team.icon,
          route: { name: 'Team', params: { teamId: team.name } },
        },
        {
          label: project.title,
          route: {
            name: 'Project',
            params: {
              teamId: team.name,
              projectId: project.name,
            },
          },
        },
        {
          label: __('Pages'),
          route: {
            name: 'ProjectPages',
            params: {
              teamId: team.name,
              projectId: project.name,
            },
          },
        },
        {
          label: this.pageTitle,
          route: {
            name: 'Page',
            params: { pageId: this.pageId, slug: this.slug },
          },
        },
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
    pageTitle() {
      let page = getCachedDocumentResource('GP Page', this.pageId)
      return page?.doc?.title || this.pageId
    },
    readOnlyControl(){
      let permission = this.$resources.permission_page.data
      if(permission == "write") return false
      else return true
    }
  },
}
</script>
