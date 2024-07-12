import { createListResource, createResource } from 'frappe-ui'
import { computed } from 'vue'

export let teams = createResource({
  url: "gameplan.api.get_teams_by_role",
  method: "GET",
  auto: true,
  onSuccess() {
    unreadItems.fetch()
  },
  transform(data) {
    console.log(data);
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
  }
})

export let unreadItems = createResource({
  url: 'gameplan.api.get_unread_items',
  cache: 'UnreadItems',
})

export let activeTeams = computed(() => {
  return (teams.data || [])
    .filter((team) => !team.archived_at)
    .map((team) => {
      if (unreadItems.data) {
        team.unread = unreadItems.data[team.name] || 0
      }
      return team
    })
})

export let getTeam = (teamId) => {
  return teams.data.find((team) => team.name.toString() === teamId.toString())
}
