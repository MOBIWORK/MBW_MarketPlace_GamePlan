<template>
  <Dialog
    v-model="show"
    :options="{ size: 'xl', position: 'top' }"
    @after-leave="filteredOptions = []"
  >
    <template #body>
      <div>
        <Combobox
          nullable
          @update:model-value="onSelection"
          v-slot="{ activeIndex }"
        >
          <div class="relative">
            <div class="absolute inset-y-0 left-0 flex items-center pl-4.5">
              <LucideSearch class="h-4 w-4" />
            </div>
            <ComboboxInput
              :placeholder="__('Search')"
              class="w-full border-none bg-transparent py-3 pl-11.5 pr-4.5 text-base text-gray-800 placeholder-gray-500 focus:ring-0"
              @input="onInput"
              autocomplete="off"
            />
          </div>
          <ComboboxOptions
            class="max-h-96 overflow-auto border-t border-gray-100"
            static
            :hold="true"
          >
            <div
              class="mb-2 mt-4.5 first:mt-3"
              v-for="(group, index) in groupedSearchResults"
              :key="group.title"
            >
              <div
                class="mb-2.5 px-4.5 text-base text-gray-600"
                v-if="!group.hideTitle"
              >
                {{ group.title }}
              </div>
              <ComboboxOption
                v-for="item in group.items"
                :key="`${item.doctype}:${item.name}`"
                v-slot="{ active }"
                :value="item"
                class="px-2.5"
                :disabled="item.disabled"
              >
                <component
                  :is="group.component"
                  :item="item"
                  :active="active"
                />
              </ComboboxOption>
            </div>
          </ComboboxOptions>
        </Combobox>
      </div>
    </template>
  </Dialog>
</template>
<script>
import { h, ref } from 'vue'
import {
  Combobox,
  ComboboxInput,
  ComboboxOptions,
  ComboboxOption,
} from '@headlessui/vue'
import fuzzysort from 'fuzzysort'
import { activeTeams } from '@/data/teams'
import { activeProjects } from '@/data/projects'
import { activeUsers } from '@/data/users'
import { activeDiscussion } from '@/data/discussions'
import { activePage } from '@/data/pages'
import { activeTask } from '@/data/tasks'
import ItemTeam from './ItemTeam.vue'
import ItemProject from './ItemProject.vue'
import Item from './Item.vue'
import ItemDiscussion from './ItemDiscussion.vue'
import ItemPage from './ItemPage.vue'
import ItemTask from './ItemTask.vue'
import UserAvatar from '../UserAvatar.vue'
import LucideHome from '~icons/lucide/home'
import LucideUsers from '~icons/lucide/users'
import LucideBell from '~icons/lucide/bell'
import LucideSearch from '~icons/lucide/file-search'

let show = ref(false)

export function showCommandPalette() {
  show.value = true
}

export function hideCommandPalette() {
  show.value = false
}

export function toggleCommandPalette() {
  show.value = !show.value
}

export default {
  name: 'CommandPalette',
  data() {
    return {
      query: '',
      filteredOptions: [],
    }
  },
  resources: {
    search() {
      return {
        url: 'gameplan.command_palette.search',
        makeParams(query) {
          return { query }
        },
        debounce: 300,
        transform(groups) {
          for (let group of groups) {
            if (group.title === 'Discussions') {
              group.component = 'Item'
              group.items = group.items.map((item) => {
                item.route = {
                  name: 'ProjectDiscussion',
                  params: {
                    postId: item.name,
                    projectId: item.payload.project,
                    teamId: item.payload.team,
                  },
                }
                return item
              })
            }
            if (group.title === 'Tasks') {
              group.component = 'Item'
              group.items = group.items.map((item) => {
                item.route = {
                  name: item.project ? 'ProjectTaskDetail' : 'Task',
                  params: {
                    taskId: item.name,
                    projectId: item.payload.project,
                    teamId: item.payload.team,
                  },
                }
                return item
              })
            }
            if (group.title === 'Pages') {
              group.component = 'Item'
              group.items = group.items.map((item) => {
                item.route = {
                  name: 'ProjectPage',
                  params: {
                    pageId: item.name,
                    projectId: item.payload.project,
                    teamId: item.payload.team,
                  },
                }
                return item
              })
            }
          }
          return groups
        },
      }
    },
  },
  watch: {
    show(value) {
      if (value) {
        this.query = ''
      }
    },
  },
  setup() {
    return { show }
  },
  components: {
    Combobox,
    ComboboxInput,
    ComboboxOptions,
    ComboboxOption,
    ItemTeam,
    ItemProject,
    Item,
    ItemDiscussion,
    ItemPage,
    ItemTask
  },
  mounted() {
    this.addKeyboardShortcut()
  },
  beforeUnmount() {
    hideCommandPalette()
  },
  methods: {
    onInput(e) {
      this.query = e.target.value
      if (this.query) {
        let results = fuzzysort
          .go(this.query, this.searchList, {
            key: 'title',
            limit: 100,
            threshold: -10000,
          })
          .map((result) => result.obj)

        this.filteredOptions = results

        if (this.query.length > 2) {
          this.$resources.search.submit(this.query)
        }
      } else {
        this.filteredOptions = []
      }
    },
    onSelection(value) {
      if (value) {
        this.$router.push(value.route)
        hideCommandPalette()
      }
    },
    addKeyboardShortcut() {
      window.addEventListener('keydown', (e) => {
        if (
          e.key === 'k' &&
          (e.ctrlKey || e.metaKey) &&
          !e.target.classList.contains('ProseMirror')
        ) {
          toggleCommandPalette()
          e.preventDefault()
        }
      })
    },
  },
  computed: {
    searchList() {
      let list = []
      let teamsByName = {}
      let projectsByName = {}
      for (const team of activeTeams.value) {
        teamsByName[team.name] = team
        list.push({
          type: 'Team',
          group: 'Teams',
          doctype: 'GP Team',
          name: team.name,
          title: team.title,
          icon: team.icon,
          modified: team.modified,
          route: {
            name: 'Team',
            params: { teamId: team.name },
          },
        })
      }

      for (const project of activeProjects.value) {
        let team = teamsByName[project.team] || null
        projectsByName[project.name] = project
        list.push({
          type: 'Project',
          group: 'Projects',
          doctype: 'GP Project',
          name: project.name,
          title: project.title,
          team: team?.title,
          modified: project.modified,
          route: {
            name: 'Project',
            params: { teamId: project.team, projectId: project.name },
          },
        })
      }

      for (const user of activeUsers.value) {
        list.push({
          type: 'People',
          group: 'People',
          doctype: 'GP User Profile',
          name: user.name,
          title: user.full_name,
          modified: user.modified,
          icon: () => h(UserAvatar, { user: user.email, size: 'sm' }),
          route: {
            name: 'PersonProfile',
            params: { personId: user.user_profile },
          },
        })
      }

      for(const discussion of activeDiscussion.value){
        let project = projectsByName[discussion.project] || null
        list.push({
          type: 'Discussion',
          group: 'Discussions',
          doctype: 'GP Dicussion',
          name: discussion.name,
          title: discussion.title,
          project: project?.title,
          modified: discussion.modified,
          route: {
            name: 'ProjectDiscussion',
            params: { teamId: discussion.team, projectId: discussion.name, postId: discussion.name }
          }
        })
      }

      for(const page of activePage.value){
        let project = null
        if(page.project != null && page.project != "") project = projectsByName[page.project] || null
        let pageInfo = {
          type: 'Page',
          group: 'Pages',
          doctype: 'GP Page',
          name: page.name,
          title: page.title,
          project: project?.title,
          modified: page.modified
        }
        if(page.project != null && page.project != ""){
          pageInfo['route'] = {
            name: 'ProjectPage',
            params: {
              teamId: page.team,
              projectId: page.project,
              pageId: page.name
            }
          }
        }else{
          pageInfo['route'] = {
            name: 'Page',
            params: {
              pageId: page.name
            }
          }
        }
        list.push(pageInfo)
      }

      for(const task of activeTask.value){
        let project = null
        if(task.project != null && task.project != "") project = projectsByName[task.project] || null
        let taskInfo = {
          type: 'Task',
          group: 'Tasks',
          doctype: 'GP Task',
          name: task.name,
          title: task.title,
          project: project?.title,
          modified: task.modified
        }
        if(task.project != null && task.project != ""){
          taskInfo['route'] = {
            name: 'ProjectTaskDetail',
            params: {
              teamId: task.team,
              projectId: task.project,
              taskId: task.name
            }
          }
        }else{
          taskInfo['route'] = {
            name: 'Task',
            params: {
              taskId: task.name
            }
          }
        }
        list.push(taskInfo)
      }
      return list
    },
    navigationItems() {
      return {
        title: __('Jump to'),
        component: 'Item',
        items: [
          {
            title: __('Home'),
            icon: () => h(LucideHome),
            route: { name: 'Home' },
          },
          {
            title: __('People'),
            icon: () => h(LucideUsers),
            route: { name: 'People' },
            condition: () => this.$user().isNotGuest,
          },
          {
            title: __('Notifications'),
            icon: () => h(LucideBell),
            route: { name: 'Notifications' },
            condition: () => this.$user().isNotGuest,
          },
        ].filter((item) => (item.condition ? item.condition() : true)),
      }
    },
    fullSearchItem() {
      return {
        title: __('Search'),
        hideTitle: true,
        component: 'Item',
        items: [
          {
            title: `${__('Search for')} "${this.query}"`,
            icon: () => h(LucideSearch),
            route: { name: 'Search', query: { q: this.query } },
          },
        ],
      }
    },
    groupedSearchResults() {
      let groups = [
        { title: __('Teams'), component: 'ItemTeam' },
        { title: __('Projects'), component: 'ItemProject' },
        { title: __('People'), component: 'Item' },
        { title: __('Discussions'), component: 'ItemDiscussion'},
        { title: __('Pages'), component: 'ItemPage'},
        { title: __('Tasks'), component: 'ItemTask'}
      ]
      let itemsByGroup = {}
      for (const group of groups) {
        itemsByGroup[group.title] = []
      }
      for (const item of this.filteredOptions) {
        itemsByGroup[item.group].push(item)
      }
      let localResults = groups
        .map((group) => {
          return {
            ...group,
            items: itemsByGroup[group.title],
          }
        })
        .filter((group) => group.items.length > 0)

      let serverResults =
        this.query.length > 2 && this.$resources.search.data
          ? this.$resources.search.data
          : []
      let results = [...localResults, ...serverResults]
      return [
        ...(this.query.length > 2 ? [this.fullSearchItem] : []),
        ...(results.length === 0 ? [this.navigationItems] : []),
        ...results,
      ]
    },
  },
}
</script>
