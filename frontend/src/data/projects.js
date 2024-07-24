import { computed } from 'vue'
import { createListResource, createResource } from 'frappe-ui'

export let projects = createListResource({
  doctype: 'GP Project',
  fields: [
    'name',
    'title',
    'icon',
    'team',
    'archived_at',
    'is_private',
    'modified',
    'tasks_count',
    'discussions_count',
  ],
  orderBy: 'title asc',
  pageLength: 999,
  cache: 'Projects',
  transform(projects) {
    return projects.map((project) => {
      project.route = {
        name: 'Project',
        params: {
          teamId: project.team,
          projectId: project.name,
        },
      }
      return project
    })
  },
  auto: true,
})

export let projects_by_role = createResource({
  url: "gameplan.api.get_projects_by_role",
  method: "GET",
  auto: true,
  transform(data) {
    return data.map((project) => {
      project.route = {
        name: 'Project',
        params: {
          teamId: project.team,
          projectId: project.name,
        },
      }
      return project
    })
  }
})

export function getTeamProjects(team) {
  return activeProjects.value.filter((project) => project.team === team) || []
}

export let activeProjects = computed(
  () => projects_by_role.data?.filter((project) => !project.archived_at) || []
)

export let getProject = (projectId) => {
  return projects_by_role.data.find(
    (project) => project.name.toString() === projectId.toString()
  )
}
