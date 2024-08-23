<template>
    <div :class="editable? 'border rounded-lg' : ''">
        <TextEditor
        ref="textEditor"
        :editor-class="['prose-sm max-w-none', editable && 'min-h-[4rem] p-3']"
        :content="value"
        @change="editable ? $emit('change', $event) : null"
        :starterkit-options="{ heading: { levels: [2, 3, 4, 5, 6] } }"
        :placeholder="placeholder"
        :editable="editable"
        @focus="onFocusEditor"
        >
            <template v-slot:editor="{ editor }">
                <EditorContent
                :class="[editable && 'max-h-28 overflow-y-auto']"
                :editor="editor"
                />
            </template>
            <template v-slot:bottom>
                <div
                v-if="editable"
                class="mt-2 flex flex-col justify-between sm:flex-row sm:items-center border-t py-2 px-2"
                >
                <div class="flex items-center">
                  <TextEditorFixedMenu
                    class="-ml-1 overflow-x-auto"
                    :buttons="textEditorMenuButtons"
                  />
                  <div class="h-4 w-[2px] border-l" style="margin-left: -5px;margin-right: 5px;"></div>
                  <CommentReactionEditor @selectEmoji="(evt) => onSelectEmoji(evt)"></CommentReactionEditor>
                </div>
                <div class="mt-2 flex items-center justify-end space-x-2 sm:mt-0">
                    <Button v-bind="discardButtonProps || {}"> Discard </Button>
                    <Button variant="solid" v-bind="submitButtonProps || {}">
                    {{__('Comment')}}
                    </Button>
                </div>
                </div>
            </template>
        </TextEditor>
    </div>
  </template>
  
  <script>
  import { EditorContent } from '@tiptap/vue-3'
  import TextEditor from '@/components/TextEditor.vue'
  import { TextEditorFixedMenu } from 'frappe-ui/src/components/TextEditor'
  import CommentReactionEditor from '@/components/Comment/CommentReactionEditor.vue'
  
  export default {
    name: 'CommentReplyEditor',
    props: {
      value: {
        type: String,
        default: '',
      },
      placeholder: {
        type: String,
        default: null,
      },
      editable: {
        type: Boolean,
        default: true,
      },
      editorProps: {
        type: Object,
        default: () => ({}),
      },
      submitButtonProps: {
        type: Object,
        default: () => ({}),
      },
      discardButtonProps: {
        type: Object,
        default: () => ({}),
      },
    },
    emits: ['change','focus'],
    expose: ['editor'],
    components: { TextEditor, TextEditorFixedMenu, EditorContent },
    methods: {
      onFocusEditor(){
      },
      onSelectEmoji(data){
        let editor = this.$refs.textEditor.editor
        editor.commands.insertContent(data)
        editor.commands.focus()
        this.$emit('change', editor.getHTML())
      }
    },
    computed: {
      editor() {
        return this.$refs.textEditor.editor
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
        ]
      },
    },
  }
  </script>
  