<template>
  <div class="flex flex-col">
    <router-view v-slot="{ Component, route }">
      <header
        class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5"
        v-if="!route.meta?.hideHeader"
      >
        <div class="flex items-center">
          <Breadcrumbs class="h-7 mr-4" :items="breadcrumbs">
            <template #prefix="{ item }">
              <span
                class="mr-2 flex rounded-sm text-2xl leading-none"
                v-if="item.icon"
              >
                {{ item.icon }}
              </span>
            </template>
          </Breadcrumbs>
          <TextInput v-if="route.name=='ProjectPages'" class="border-none md:w-96" type="text" size="sm" :placeholder="__('Search title, author')" v-model="search" :debounce="800" @update:modelValue="onChangeSearch()">
            <template #suffix>
              <LucideSearch class="h-4 w-4" />
            </template>
          </TextInput>
        </div>
        <template v-if="route.name=='ProjectDiscussions'">
          <Button
            variant="solid"
            v-if="!project.doc.archived_at && !readOnlyByRole()"
            :route="{ name: 'ProjectDiscussionNew' }"
          >
            <template #prefix>
              <LucidePlus class="h-4 w-4" />
            </template>
            {{ __('Add new') }}
          </Button>
        </template>
        <template v-if="route.name=='ProjectTasks'">
          <Button variant="solid" @click="showNewTaskDialog" v-if="!readOnlyByRole()">
            <template #prefix>
              <LucidePlus class="h-4 w-4" />
            </template>
            {{__('Add new')}}
          </Button>
        </template>
        <template v-if="route.name=='ProjectPages'">
          <div class="flex items-center space-x-2">
            <Dropdown
              :options="[
                {
                  label: __('Date Updated'),
                  onClick: () => (listOptionsPage.orderBy = 'modified desc'),
                },
                {
                  label: __('Date Created'),
                  onClick: () => (listOptionsPage.orderBy = 'creation desc'),
                },
              ]"
            >
              <Button>
                <div class="flex items-center">
                  <ArrowDownUp
                    class="mr-1.5 h-4 w-4 leading-none"
                    :stroke-width="1.5"
                  />
                  <span> {{ __('Sort') }} </span>
                </div>
              </Button>
            </Dropdown>
            <Button variant="solid" @click="$resources.newPage.submit()" v-if="!readOnlyByRole()">
              <template #prefix><LucidePlus class="w-4" /></template>
              {{ __('Add new') }}
            </Button>
            </div>
        </template>

        <div
          v-if="$route.name === 'ProjectOverview'"
          class="flex items-center space-x-2"
        >
          <Tooltip
            v-if="project.doc.is_private"
            :text="__('This project is only visible to team members')"
          >
            <Badge size="lg">
              <template #prefix><LucideLock class="w-3" /></template>
              {{ __('Private') }}
            </Badge>
          </Tooltip>
          <Badge size="lg" v-if="project.doc.archived_at">
            <template #prefix><LucideArchive class="w-3" /></template>
            {{ __('Archived') }}
          </Badge>
          <template v-if="!isMobile">
            <Button
              v-if="project.doc.is_followed"
              @click="project.unfollow.submit()"
              :loading="project.unfollow.loading"
            >
              <template #prefix><LucideBell class="w-4" /></template>
              {{ __('Following') }}
            </Button>
            <Button
              v-else
              @click="project.follow.submit()"
              :loading="project.follow.loading"
            >
              <template #prefix><LucideBellPlus class="w-4" /></template>
              {{ __('Follow') }}
            </Button>
          </template>
          <Dropdown
            v-if="$user().isNotGuest"
            placement="left"
            :button="{
              icon: 'more-horizontal',
              variant: 'ghost',
              label: __('Options'),
            }"
            :options="[
              {
                label: __('Edit'),
                icon: 'edit',
                onClick: () => (projectEditDialog.show = true),
                condition: () => !project.doc.archived_at,
              },
              {
                label: __('Follow'),
                icon: 'plus',
                onClick: () => project.follow.submit(),
                condition: () => isMobile && !project.doc.is_followed,
              },
              {
                label: __('Following'),
                icon: 'check',
                onClick: () => project.unfollow.submit(),
                condition: () => isMobile && project.doc.is_followed,
              },
              {
                label: __('Manage Guests'),
                icon: 'user-plus',
                onClick: () => (inviteGuestDialog.show = true),
                condition: () => !project.doc.archived_at,
              },
              {
                label: __('Move to another team'),
                icon: 'log-out',
                onClick: () => (projectMoveDialog.show = true),
                condition: () => !project.doc.archived_at,
              },
              {
                label: __('Archive this project'),
                icon: 'trash-2',
                onClick: archiveProject,
                condition: () => !project.doc.archived_at,
              },
              {
                label: __('Unarchive this project'),
                icon: 'trash-2',
                onClick: unarchiveProject,
                condition: () => project.doc.archived_at,
              },
            ]"
          />
        </div>
        <Dialog
          :options="{
            title: __('Edit Project'),
            actions: [
              {
                label: __('Save'),
                variant: 'solid',
                onClick({ close }) {
                  return project.setValue
                    .submit({
                      title: project.doc.title,
                      is_private: project.doc.is_private,
                    })
                    .then(() => { projectEditDialog.show = false })
                },
              },
            ],
          }"
          v-model="projectEditDialog.show"
        >
          <template #body-content>
            <FormControl
              class="mb-2"
              :label="__('Title')"
              v-model="project.doc.title"
              :placeholder="__('Project title')"
            />
            <FormControl
              v-if="!team.doc.is_private"
              :label="__('Visibility')"
              type="select"
              :options="[
                { label: __('Visible to everyone'), value: 0 },
                { label: __('Visible to team members (Private)'), value: 1 },
              ]"
              v-model="project.doc.is_private"
            />
            <ErrorMessage class="mt-2" :message="project.setValue.error" />
          </template>
        </Dialog>
        <Dialog
          :options="{
            title: __('Move project to another team'),
          }"
          @close="
            () => {
              projectMoveDialog.team = null
              project.moveToTeam.reset()
            }
          "
          v-model="projectMoveDialog.show"
        >
          <template #body-content>
            <Autocomplete
              :options="moveToTeamsList"
              v-model="projectMoveDialog.team"
              :placeholder="__('Select a team')"
            >
              <template #item-prefix="{ option }">
                <span class="mr-2">{{ option.icon }}</span>
              </template>
            </Autocomplete>
            <ErrorMessage class="mt-2" :message="project.moveToTeam.error" />
          </template>
          <template #actions>
            <Button
              class="w-full"
              variant="solid"
              :loading="project.moveToTeam.loading"
              @click="
                () => {
                  project.moveToTeam.submit(
                    { team: projectMoveDialog.team?.value },
                    {
                      validate() {
                        if (!projectMoveDialog.team?.value) {
                          return __('Team is required to move this project')
                        }
                      },
                      onSuccess() {
                        onProjectMove()
                      },
                    }
                  )
                }
              "
            >
              {{
                projectMoveDialog.team
                  ? `${__('Move to')} ${projectMoveDialog.team.label}`
                  : __('Move')
              }}
            </Button>
          </template>
        </Dialog>
        <InviteGuestDialog
          v-if="$user().isNotGuest"
          v-model="inviteGuestDialog.show"
          :project="project"
        />

        <Dialog
          :options="{
            title: __('Archive project'),
            message: __('Are you sure you want to archive this project?'),
            actions: [
              {
                label: __('Archive'),
                variant: 'solid',
                onClick: ({ close }) => {
                  return this.project.archive.submit(null, {
                    onSuccess: () => {
                      reloadProjects()
                      showArchiveProjectDialog = false 
                    },
                  })
                },
              }
            ],
          }"
          v-model="showArchiveProjectDialog"
        />
        <Dialog
          :options="{
            title: __('Unarchive Project'),
            message: __('Are you sure you want to unarchive this project?'),
            actions: [
              {
                label: __('Unarchive'),
                variant: 'solid',
                onClick: ({ close }) => {
                  return this.project.unarchive.submit(null, {
                    onSuccess: ()=>{
                      reloadProjects()
                      showUnArchiveProjectDialog = false
                    },
                  })
                },
              },
              {
                label: __('Cancel'),
              }
            ],
          }"
          v-model="showUnArchiveProjectDialog"
        />
        <NewTaskDialog ref="newTaskDialog" />
      </header>

      <component
        v-if="project"
        :is="Component"
        :class="{ 'mx-auto w-full px-5': !route.meta?.fullWidth }"
        :project="project"
        :team="team"
        :listOptionsPage="listOptionsPage"
      />
    </router-view>
  </div>
</template>
<script>
import { computed } from 'vue'
import {
  Autocomplete,
  Dropdown,
  FormControl,
  Breadcrumbs,
  frappeRequest,
  Input,
  Tooltip,
  Select,
  Textarea,
  Dialog,
  getCachedListResource,
  TextInput
} from 'frappe-ui'
import Pie from '@/components/Pie.vue'
import IconPicker from '@/components/IconPicker.vue'
import Links from '@/components/Links.vue'
import Tabs from '@/components/Tabs.vue'
import InviteGuestDialog from '@/components/InviteGuestDialog.vue'
import { projects, projects_by_role } from '@/data/projects'
import { activeTeams, teams, teams_by_role } from '@/data/teams'
import PinIcon from '~icons/lucide/pin'
import { useScreenSize } from '@/utils/composables'
import { getUser } from '@/data/users'
import ArrowDownUp from '~icons/lucide/arrow-up-down'

export default {
  name: 'Project',
  props: ['team', 'project'],
  components: {
    Input,
    Dropdown,
    Pie,
    IconPicker,
    Links,
    Tabs,
    Autocomplete,
    Tooltip,
    InviteGuestDialog,
    FormControl,
    Select,
    Textarea,
    Breadcrumbs,
    ArrowDownUp,
    TextInput
  },
  setup() {
    const size = useScreenSize()
    const isMobile = computed(() => size.width < 640)
    return {
      PinIcon,
      isMobile,
    }
  },
  data() {
    return {
      projectMoveDialog: { show: false, team: null },
      projectEditDialog: { show: false },
      inviteGuestDialog: { show: false },
      showArchiveProjectDialog: false,
      showUnArchiveProjectDialog: false,
      newTaskDialog: null,
      listOptions:{
        filters: {
          project: this.project.name
        }
      },
      listOptionsPage: {
        orderBy: "modified desc",
        search: null,
        project: this.project.name
      },
      search: ""
    }
  },
  computed: {
    moveToTeamsList() {
      return activeTeams.value
        .filter((d) => d.name != this.team.name)
        .map((d) => ({
          label: d.title,
          value: d.name,
          icon: d.icon,
        }))
    },
    task() {
      let task = null
      if (this.$route.name === 'ProjectTaskDetail') {
        task = this.$getDocumentResource('GP Task', this.$route.params.taskId)
      }
      return task
    },
    breadcrumbs() {
      let items = [
        {
          label: this.team.doc.title,
          icon: this.team.doc.icon,
          route: { name: 'Team', params: { teamId: this.team.doc.name } },
        },
        {
          label: this.project.doc.title,
          route: {
            name: 'Project',
            params: {
              teamId: this.team.doc.name,
              projectId: this.project.doc.name,
            },
          },
        },
      ]
      if (
        [
          'ProjectDiscussions',
          'ProjectDiscussion',
          'ProjectDiscussionNew',
        ].includes(this.$route.name)
      ) {
        items.push({
          label: __('Discussions'),
          route: {
            name: 'ProjectDiscussions',
            params: {
              teamId: this.team.doc.name,
              projectId: this.project.doc.name,
            },
          },
        })
      }
      if (this.$route.name === 'ProjectDiscussion') {
        let discussion = this.$getDocumentResource(
          'GP Discussion',
          this.$route.params.postId
        )
        items.push({
          label: discussion?.doc?.title || this.$route.params.postId,
          route: {
            name: 'ProjectDiscussion',
            params: {
              teamId: this.team.doc.name,
              projectId: this.project.doc.name,
              postId: this.$route.params.postId,
            },
          },
        })
      }
      if (this.$route.name === 'ProjectDiscussionNew') {
        items.push({
          label: __('New Discussion'),
          route: {
            name: 'ProjectDiscussionNew',
            params: {
              teamId: this.team.doc.name,
              projectId: this.project.doc.name,
            },
          },
        })
      }

      if (['ProjectTasks', 'ProjectTaskDetail'].includes(this.$route.name)) {
        items.push({
          label: __('Tasks'),
          route: {
            name: 'ProjectTasks',
            params: {
              teamId: this.team.doc.name,
              projectId: this.project.doc.name,
            },
          },
        })
      }

      if (this.$route.name === 'ProjectTaskDetail') {
        let task = this.$getDocumentResource(
          'GP Task',
          this.$route.params.taskId
        )
        items.push({
          label: task?.doc?.title || this.$route.params.taskId,
          route: {
            name: 'ProjectTaskDetail',
            params: {
              teamId: this.team.doc.name,
              projectId: this.project.doc.name,
              taskId: this.$route.params.taskId,
            },
          },
        })
      }

      if (['ProjectPages', 'ProjectPage'].includes(this.$route.name)) {
        items.push({
          label: __('Pages'),
          route: {
            name: 'ProjectPages',
            params: {
              teamId: this.team.doc.name,
              projectId: this.project.doc.name,
            },
          },
        })
      }

      if (this.$route.name === 'ProjectPage') {
        let page = this.$getDocumentResource(
          'GP Page',
          this.$route.params.pageId
        )
        items.push({
          label: page?.doc?.title || this.$route.params.pageId,
          route: {
            name: 'ProjectPage',
            params: {
              teamId: this.team.doc.name,
              projectId: this.project.doc.name,
              pageId: this.$route.params.pageId,
            },
          },
        })
      }

      return items
    },
  },
  methods: {
    archiveProject() {
      this.showArchiveProjectDialog = true;
    },
    unarchiveProject() {
      this.showUnArchiveProjectDialog = true;
    },
    onProjectMove() {
      this.projectMoveDialog.show = false
      projects_by_role.fetch()
      for (let team of teams_by_role.data || []) {
        if (
          [this.team.doc.name, this.projectMoveDialog.team.value].includes(
            team.name
          )
        ) {
          if (this.projectMoveDialog.team.value === team.name) {
            team.open = true
          }
        }
      }
      this.$router.push({
        name: 'ProjectOverview',
        params: {
          teamId: this.projectMoveDialog.team.value,
          projectId: this.project.name,
        },
      })
      this.projectMoveDialog.team = null
      this.project.moveToTeam.reset()
    },
    showNewTaskDialog(){
      let me = this;
      this.$refs.newTaskDialog.show({
        defaults: {
          project: this.listOptions.filters.project,
          assigned_to: getUser('sessionUser').name,
        },
        onSuccess: () => {
          let tasks = getCachedListResource(['Tasks', this.listOptions])
          if (tasks) {
            tasks.reload()
          }
        },
      })
    },
    onChangeSearch(){
      this.listOptionsPage.search = this.search;
    },
    readOnlyByRole(){
      let role = this.$getRoleByUser(this.team.doc, this.project.doc)
      if(role == "guest") return true
      return false
    },
    reloadProjects(){
      projects_by_role.fetch()
    }
  },
  resources: {
    newPage() {
      return {
        url: 'frappe.client.insert',
        params: {
          doc: {
            doctype: 'GP Page',
            project: this.project.name,
            title: __('Untitled'),
            content: '',
          },
        },
        onSuccess(doc) {
          this.$router.push({
            name: 'ProjectPage',
            params: { pageId: doc.name },
          })
        },
      }
    },
  }
}
</script>
