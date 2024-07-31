<template>
  <div class="mt-6">
    <ReadmeEditor
      :resource="team"
      fieldname="readme"
      :border="true"
      :collapsible="true"
      :editable="!team.doc.archived_at"
      :readOnly="readOnlyByRole()"
    />

    <div class="mt-8">
      <div class="mb-5 flex items-center justify-between space-x-2">
        <h2 class="text-2xl font-semibold text-gray-900">{{ __('Projects') }}</h2>
        <div class="flex items-stretch space-x-2">
          <TabButtons
            :buttons="[{ label: __('Active') }, { label: __('Archived') }]"
            v-model="activeTab"
          />
          <Button
            v-if="teamProjects.length && !readOnlyByRole()"
            @click="createNewProjectDialog = true"
            variant="solid"
          >
            <template #prefix>
              <LucidePlus class="h-4 w-4" />
            </template>
            {{ __('Add Project') }}
          </Button>
        </div>
      </div>
      <ul role="list" class="grid grid-cols-1 gap-5 sm:grid-cols-4">
        <li
          v-for="project in projectsList"
          :key="project.name"
          class="flow-root"
        >
          <div
            class="group relative items-center rounded-lg p-3 shadow transition-colors focus-within:ring focus-within:ring-gray-300 hover:bg-gray-100"
          >
            <div>
              <h3 class="overflow-hidden text-lg font-medium text-gray-900">
                <router-link
                  :to="{
                    name: 'Project',
                    params: { projectId: project.name },
                  }"
                  class="inline-flex w-full overflow-hidden text-ellipsis whitespace-nowrap focus:outline-none"
                >
                  <span class="absolute inset-0" aria-hidden="true" />
                  <span class="inline-flex items-center">
                    {{ project.title }}
                    <LucideLock
                      v-if="project.is_private"
                      class="ml-1 h-3 w-3"
                    />
                  </span>
                </router-link>
              </h3>
              <p class="mt-1 text-base">
                <template v-if="project.tasks_count">
                  <span class="text-gray-900">
                    {{ project.tasks_count }}
                  </span>
                  <span class="text-gray-700"
                    >&nbsp;{{ project.tasks_count === 1 ? __('task') : __('tasks') }}
                  </span>
                  &middot;
                </template>
                <template v-if="project.discussions_count">
                  <span class="text-gray-900">
                    {{ project.discussions_count }}
                  </span>
                  <span class="text-gray-700"
                    >&nbsp;{{
                      project.discussions_count === 1
                        ? __('discussion')
                        : __('discussions')
                    }}
                  </span>
                </template>
                <span
                  class="text-gray-700"
                  v-if="project.tasks_count + project.discussions_count == 0"
                >
                  {{ $dayjs(project.creation).fromNow() }}
                </span>
              </p>
            </div>
          </div>
        </li>
        <button
          v-if="teamProjects.length === 0"
          class="group relative flex items-center space-x-4 rounded-xl border border-gray-100 p-2 text-left transition-colors focus-within:ring-2 focus-within:ring-blue-500 hover:bg-gray-100"
          @click="createNewProjectDialog = true"
        >
          <div
            class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-gray-100 transition-colors group-hover:bg-white"
          >
            <LucidePlus class="w-5 text-gray-600" />
          </div>
          <div>
            <h3 class="text-lg font-medium text-gray-900">{{ __('Add Project') }}</h3>
          </div>
        </button>
      </ul>
      <Dialog
        :options="{ title: __('Create project') }"
        v-model="createNewProjectDialog"
      >
        <template #body-content>
          <div class="space-y-5">
            <FormControl
              label="Title"
              v-model="newProject.title"
              @keydown.enter="createProject"
            />
            <FormControl
              v-if="!team.doc.is_private"
              type="select"
              :label="__('Visibility')"
              :options="[
                { label: __('Visible to everyone'), value: 0 },
                { label: __('Visible to team members (Private)'), value: 1 },
              ]"
              v-model="newProject.is_private"
            />
            <ErrorMessage :message="projects.insert.error" />
          </div>
        </template>
        <template #actions>
          <Button
            size="md"
            class="w-full"
            variant="solid"
            @click="createProject"
            :loading="projects.insert.loading"
          >
            Create
          </Button>
        </template>
      </Dialog>
    </div>
  </div>
</template>
<script>
import { Dialog, FormControl, TextInput, TabButtons } from 'frappe-ui'
import { projects, getTeamProjects, projects_by_role } from '@/data/projects'

export default {
  name: 'TeamOverview',
  props: ['team'],
  components: {
    Dialog,
    TabButtons,
    TextInput,
    FormControl
  },
  data() {
    return {
      createNewProjectDialog: false,
      newProject: { title: '', is_private: 0 },
      activeTab: 'Active',
    }
  },
  computed: {
    projects() {
      return projects
    },
    projectsList() {
      return this.activeTab === 'Active'
        ? this.activeProjects
        : this.archivedProjects
    },
    activeProjects() {
      return this.teamProjects.filter((project) => !project.archived_at)
    },
    archivedProjects() {
      return this.teamProjects.filter((project) => project.archived_at)
    },
    teamProjects() {
      return getTeamProjects(this.team.name)
    },
  },
  methods: {
    createProject() {
      projects.insert.submit(
        {
          team: this.team.name,
          ...this.newProject,
        },
        {
          onSuccess: (project) => {
            projects_by_role.fetch()
            this.newProject = this.$options.data().newProject
            this.createNewProjectDialog = false
            this.$router.push({
              name: 'Project',
              params: { projectId: project.name },
            })
          },
        }
      )
    },
    readOnlyByRole(){
      let role = this.$getRoleByUser(this.team.doc, null);
      if (role == "member" || role == "guest") return true
      return false
    }
  },
}
</script>
