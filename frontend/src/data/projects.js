import { computed } from 'vue'
import { createListResource, createResource } from 'frappe-ui'

export let projects = createResource({
  url: "gameplan.api.get_projects_by_role",
  method: "GET",
  auto: true,
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
  }
})

export function getTeamProjects(team) {
  return activeProjects.value.filter((project) => project.team === team) || []
}

export let activeProjects = computed(
  () => projects.data?.filter((project) => !project.archived_at) || []
)

export let getProject = (projectId) => {
  return projects.data.find(
    (project) => project.name.toString() === projectId.toString()
  )
}
