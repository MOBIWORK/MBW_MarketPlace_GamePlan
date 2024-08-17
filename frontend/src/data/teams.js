import { createListResource, createResource } from 'frappe-ui'
import { computed } from 'vue'

export let teams = createListResource({
  type: 'list',
  doctype: 'GP Team',
  fields: [
    'name',
    'title',
    'icon',
    'modified',
    'creation',
    'archived_at',
    'is_private'
  ],
  orderBy: 'title asc',
  cache: 'Teams',
  pageLength: 999,
  auto: true,
  onSuccess() {
    unreadItems.fetch()
  },
  transform(data) {
    return data.map((team) => {
      return {
        ...team,
        route: {
          name: 'Team',
          params: { teamId: team.name },
        },
        open: false,
        projects: [],
      }
    })
  },
})

export let unreadItems = createResource({
  url: 'gameplan.api.get_unread_items',
  cache: 'UnreadItems',
})

export let teams_by_role = createResource({
  url: "gameplan.api.get_teams_by_role",
  method: "GET",
  auto: false,
  onSuccess() {
    unreadItems.fetch()
  },
  transform(data) {
    return data.map((team) => {
      return {
        ...team,
        route: {
          name: 'Team',
          params: { teamId: team.name },
        },
        open: false,
        projects: [],
      }
    })
  },
})

export let activeTeams = computed(() => {
  return (teams_by_role.data || [])
    .filter((team) => !team.archived_at)
    .map((team) => {
      if (unreadItems.data) {
        team.unread = unreadItems.data[team.name] || 0
      }
      return team
    })
})

export let getTeam = (teamId) => {
  return teams_by_role.data.find((team) => team.name.toString() === teamId.toString())
}

export let getTeamInfo = (teamId) => {
  let resourceTeam = createResource({
    url: "frappe.client.get",
    method: "POST",
    auto: true,
    params: {
      doctype: "GP Team",
      name: teamId
    }
  })
  return resourceTeam
}