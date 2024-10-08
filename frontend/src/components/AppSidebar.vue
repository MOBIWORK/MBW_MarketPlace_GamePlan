<template>
  <div
    class="absolute right-0 z-10 h-full w-1 cursor-col-resize bg-gray-300 opacity-0 transition-opacity hover:opacity-100"
    :class="{ 'opacity-100': sidebarResizing }"
    @mousedown="startResize"
  />
  <div
    v-show="sidebarResizing"
    class="fixed z-20 mt-3 -translate-x-[130%] rounded-md bg-gray-800 px-2 py-1 text-base text-white"
    :style="{ left: sidebarWidth + 'px' }"
  >
    {{ sidebarWidth }}
  </div>

  <div
    class="inline-flex h-full flex-1 flex-col overflow-auto border-r bg-gray-50 pb-40"
    :style="{ width: `${sidebarWidth}px` }"
  >
    <div class="flex flex-col px-2 py-2">
      <UserDropdown />
    </div>
    <div class="flex-1">
      <nav class="space-y-0.5 px-2">
        <Links
          :links="navigation"
          class="flex items-center rounded px-2 py-1 text-gray-800 transition"
          active="bg-white shadow-sm"
          inactive="hover:bg-gray-100"
        >
          <template v-slot="{ link }">
            <div class="flex w-full items-center space-x-2">
              <span class="grid h-5 w-6 place-items-center">
                <component :is="link.icon" class="h-4 w-4 text-gray-700" />
              </span>
              <span class="text-sm">{{ __(link.name) }}</span>
              <span
                v-if="link.count"
                class="!ml-auto block text-xs text-gray-600"
              >
                {{ link.count }}
              </span>
            </div>
          </template>
        </Links>
        <button id="notifications-btn"
          class="flex w-full items-center rounded px-2 py-1 text-gray-800 "
          :class="[activeNotification? 'bg-white shadow-sm' : '']"
          @click="onToggleNotification()"  
        >
          <div class="flex w-full items-center">
            <span class="grid h-5 w-6 place-items-center">
              <LucideBell class="h-4 w-4 text-gray-700" />
            </span>
            <span class="ml-2 text-sm">{{__('Notifications')}}</span>
            <span class="ml-auto text-sm">
              <Badge
                v-if="
                  notification.count
                "
                :label="notification.count"
                variant="subtle"
              />
              <div
                v-else-if="notification.count"
                class="absolute -left-1.5 top-1 z-20 h-[5px] w-[5px] translate-x-6 translate-y-1 rounded-full bg-gray-800 ring-1 ring-white"
              />
            </span>
          </div>
        </button>
        <button
          v-if="$user().isNotGuest"
          class="flex w-full items-center rounded px-2 py-1 text-gray-800"
          :class="[
            /Search/.test($route.name)
              ? 'bg-white shadow-sm'
              : 'hover:bg-gray-100',
          ]"
          @click="showCommandPalette"
        >
          <div class="flex w-full items-center">
            <span class="grid h-5 w-6 place-items-center">
              <LucideSearch class="h-4 w-4 text-gray-700" />
            </span>
            <span class="ml-2 text-sm">{{__('Search')}}</span>
            <span class="ml-auto text-sm text-gray-500">
              <template v-if="$platform === 'mac'">⌘K</template>
              <template v-else>Ctrl+K</template>
            </span>
          </div>
        </button>
      </nav>
      <div class="mt-6 flex items-center justify-between px-3">
        <div class="flex items-center">
          <h3 class="text-sm font-medium text-gray-600">{{__('Teams')}}</h3>
          <Button
            v-if="!isExpandAll"
            :label="__('Expand all')"
            variant="ghost"
            @click="onExpanAll()"
          >
            <template #icon><LucideChevronRight class="h-4 w-4" /></template>
          </Button>
          <Button
            v-if="isExpandAll"
            :label="__('Collapse all')"
            variant="ghost"
            @click="onCollapseAll()"
          >
            <template #icon><LucideChevronDown class="h-4 w-4" /></template>
          </Button>
        </div>
        
        <Button
          :label="__('Create Team')"
          variant="ghost"
          v-if="$getRoleByUser(null, null) != 'guest'"
          @click="showAddTeamDialog = true"
        >
          <template #icon><LucidePlus class="h-4 w-4" /></template>
        </Button>
      </div>
      <nav class="mt-1 space-y-0.5 px-2" id="lst_teams">
        <div v-for="team in activeTeams" :key="team.name" :id="team.name">
          <Link
            :link="team"
            class="flex items-center rounded px-2 py-1 transition"
          >
            <button
              @click.prevent="
                () => onExpandOrCollapseItem(team)
              "
              class="mr-1.5 grid h-4 w-4 place-items-center rounded hover:bg-gray-200"
            >
              <ChevronTriangle
                class="h-3 w-3 text-gray-500 transition duration-200"
                :class="[team.open ? 'rotate-90' : 'rotate-0']"
              />
            </button>
            <div class="flex w-full items-center">
              <span class="flex h-5 w-5 items-center justify-center text-xl">
                {{ team.icon }}
              </span>
              <span class="ml-2 text-sm">{{ team.title }}</span>
              <LucideLock v-if="team.is_private" class="ml-2 h-3 w-3" />
              <div class="ml-auto">
                <Tooltip
                  v-if="team.unread"
                  :text="`${team.unread} unread posts`"
                >
                  <span class="text-xs text-gray-600">{{ team.unread }}</span>
                </Tooltip>
              </div>
            </div>
          </Link>
          <div class="mb-2 mt-0.5 space-y-0.5 pl-7" v-show="team.open">
            <Link
              :key="project.name"
              v-for="project in teamProjects(team.name)"
              :link="project"
              :ref="($comp) => setProjectRef($comp, project)"
              class="flex h-7 items-center rounded-md px-2 text-gray-800 transition"
              active="bg-white shadow-sm"
              inactive="hover:bg-gray-100"
            >
              <template v-slot="{ link: project }">
                <span class="inline-flex items-center space-x-2 w-full">
                  <span class="text-sm truncate w-full">{{ project.title }}</span>
                  <LucideLock v-if="project.is_private" class="h-3 w-3" />
                </span>
              </template>
            </Link>
            <div
              class="flex h-7 items-center px-2 text-sm text-gray-600"
              v-if="teamProjects(team.name).length === 0"
            >
              {{__('No projects')}}
            </div>
          </div>
        </div>
      </nav>
      <div
        v-if="teams.fetched && !activeTeams.length"
        class="px-3 py-2 text-sm text-gray-500"
      >
        {{__('No teams')}}
      </div>
    </div>
    <AddTeamDialog
      v-model:show="showAddTeamDialog"
      @success="
        (team) => {
          showAddTeamDialog = false
          $router.push({
            name: 'TeamOverview',
            params: { teamId: team.name },
          })
        }
      "
    />
  </div>
  <NotificationsSidebar :visible="isVisibleNotification" @changeVisible="(visible) => changeVisible(visible)" @markAllRead="onLoadUnreadNotification()"/>
</template>
<script>
import { Tooltip } from 'frappe-ui'
import Links from './Links.vue'
import Link from './Link.vue'
import AddTeamDialog from './AddTeamDialog.vue'
import UserDropdown from './UserDropdown.vue'
import ChevronTriangle from './icons/ChevronTriangle.vue'
import { activeTeams, teams, teams_by_role } from '@/data/teams'
import { getTeamProjects } from '@/data/projects'
import { unreadNotifications } from '@/data/notifications'
import { showCommandPalette } from '@/components/CommandPalette/CommandPalette.vue'
import LucideUsers2 from '~icons/lucide/users-2'
import LucideInbox from '~icons/lucide/inbox'
import LucideListTodo from '~icons/lucide/list-todo'
import LucideNewspaper from '~icons/lucide/newspaper'
import LucideFiles from '~icons/lucide/files'
import { getUser } from '@/data/users'
import NotificationsSidebar from '@/components/NotificationsSidebar.vue'
import Sortable from 'sortablejs';

export default {
  name: 'AppSidebar',
  components: {
    AddTeamDialog,
    Links,
    Link,
    UserDropdown,
    Tooltip,
    ChevronTriangle,
    NotificationsSidebar
  },
  data() {
    return {
      sidebarOpen: true,
      sidebarWidth: 256,
      sidebarResizing: false,

      showAddTeamDialog: false,
      teams,
      isExpandAll: false,
      isVisibleNotification: false
    }
  },
  mounted() {
    var me = this
    teams_by_role.fetch()
    let sidebarWidth = parseInt(localStorage.getItem('sidebarWidth') || 256)
    this.sidebarWidth = sidebarWidth
    let el = document.getElementById("lst_teams")
    var sortable = Sortable.create(el, {
      onEnd: function(evt){
        let elementChild = el.children
        let arrOrderByTeam = []
        for(let i = 0; i < elementChild.length; i++){
          arrOrderByTeam.push(elementChild[i].id)
        }
        localStorage.setItem(`orderByTeamCache_${getUser('sessionUser').name}`, JSON.stringify(arrOrderByTeam))
      }
    });
  },
  computed: {
    notification(){
      return {
        name: "Notification",
        icon: LucideInbox,
        count: unreadNotifications.data || 0
      }
    },
    navigation() {
      return [
        {
          name: 'Discussions',
          icon: LucideNewspaper,
          route: {
            name: 'Discussions',
          },
        },
        {
          name: 'My Tasks',
          icon: LucideListTodo,
          route: {
            name: 'MyTasks',
          },
          isActive: /MyTasks|Task/g.test(this.$route.name),
        },
        {
          name: 'My Pages',
          icon: LucideFiles,
          route: {
            name: 'MyPages',
          },
          isActive: /MyPages|Page/g.test(this.$route.name),
        },
        {
          name: 'People',
          icon: LucideUsers2,
          route: {
            name: 'People',
          },
          isActive: /People|PersonProfile/g.test(this.$route.name),
          condition: () => this.$user().isNotGuest,
        }
      ].filter((nav) => (nav.condition ? nav.condition() : true))
    },
    activeTeams() {
      let strActiveTeamCache = localStorage.getItem(`activeTeamCache_${getUser('sessionUser').name}`)
      let objActiveTeamCache = {}
      if(strActiveTeamCache != null && strActiveTeamCache != "") objActiveTeamCache = JSON.parse(strActiveTeamCache)
      let strOrderByTeamCache = localStorage.getItem(`orderByTeamCache_${getUser('sessionUser').name}`)
      let arrOrderByTeamCache = []
      if(strOrderByTeamCache != null && strOrderByTeamCache != "") arrOrderByTeamCache = JSON.parse(strOrderByTeamCache)
      let activeSortedTeams = []
      if(arrOrderByTeamCache.length > 0){
        let arrTeamTemp = []
        for(let i = 0; i < activeTeams.value.length; i++){
          if(arrOrderByTeamCache.indexOf(activeTeams.value[i].name) < 0) arrTeamTemp.push(activeTeams.value[i]) //Đưa những nhóm chưa được lưu trữ sắp xếp vào mảng tạm
        }
        //Từ mảng team lưu trữ localstorage ánh xạ sang danh sách team theo mã lưu trữ
        for(let i = 0; i < arrOrderByTeamCache.length; i++){
          let activeTeamFilter = activeTeams.value.filter(x => x.name == arrOrderByTeamCache[i])
          if(activeTeamFilter.length > 0){
            activeSortedTeams.push(activeTeamFilter[0])
          }
        }
        //Bổ sung những team chưa được lưu trong localstorage
        for(let i = 0; i < arrTeamTemp.length; i++){
          activeSortedTeams.push(arrTeamTemp[i])
        }
      }else{
        activeSortedTeams = activeTeams.value
      }
      let activeTeamsNew = activeSortedTeams.map((team) => {
        team.class = function ($route, link) {
          if (
            ['TeamLayout', 'Team', 'TeamOverview'].includes($route.name) &&
            $route.params.teamId === link.route.params.teamId
          ) {
            return 'bg-white shadow-sm text-gray-800'
          }
          return 'text-gray-800 hover:bg-gray-100'
        }
        if(objActiveTeamCache.hasOwnProperty(team.name)) team["open"] = objActiveTeamCache[team.name];
        return team
      });
      return activeTeamsNew;
    },
    activeNotification(){
      return /Notifications/g.test(this.$route.name)
    }
  },
  methods: {
    onToggleNotification(){
      this.isVisibleNotification = true
    },
    changeVisible(visible){
      this.isVisibleNotification = visible
    },
    teamProjects(teamName) {
      return getTeamProjects(teamName)
        .filter((project) => !project.archived_at)
        .map((project) => {
          if (
            this.$route.name === 'ProjectDiscussion' &&
            this.$route.params.projectId == project.name
          ) {
            project.isActive = true
            this.scrollProjectIntoView(project)
          } else {
            project.isActive = false
          }
          return project
        })
    },
    setProjectRef($comp, project) {
      this.$projectRefs = this.$projectRefs || {}
      if ($comp) {
        this.$projectRefs[project.name] = $comp.getRef()
      }
    },
    async scrollProjectIntoView(project) {
      await this.$nextTick()
      const $el = this.$projectRefs[project.name]
      if ($el) {
        $el.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
          inline: 'nearest',
        })
      }
    },
    startResize() {
      document.addEventListener('mousemove', this.resize)
      document.addEventListener('mouseup', () => {
        document.body.classList.remove('select-none')
        document.body.classList.remove('cursor-col-resize')
        localStorage.setItem('sidebarWidth', this.sidebarWidth)
        this.sidebarResizing = false
        document.removeEventListener('mousemove', this.resize)
      })
    },
    resize(e) {
      this.sidebarResizing = true
      document.body.classList.add('select-none')
      document.body.classList.add('cursor-col-resize')
      this.sidebarWidth = e.clientX

      // snap to 256
      let range = [256 - 10, 256 + 10]
      if (this.sidebarWidth > range[0] && this.sidebarWidth < range[1]) {
        this.sidebarWidth = 256
      }

      if (this.sidebarWidth < 12 * 16) {
        this.sidebarWidth = 12 * 16
      }
      if (this.sidebarWidth > 24 * 16) {
        this.sidebarWidth = 24 * 16
      }
    },
    showCommandPalette,
    onExpanAll(){
      let objActiveTeamCache = {};
      for(let i = 0; i < this.activeTeams.length; i++){
        this.activeTeams[i].open = true;
        objActiveTeamCache[this.activeTeams[i].name] = true;
      }
      localStorage.setItem(`activeTeamCache_${getUser('sessionUser').name}`, JSON.stringify(objActiveTeamCache));
      this.isExpandAll = true;
    },
    onCollapseAll(){
      let objActiveTeamCache = {};
      for(let i = 0; i < this.activeTeams.length; i++){
        this.activeTeams[i].open = false;
        objActiveTeamCache[this.activeTeams[i].name] = false;
      }
      localStorage.setItem(`activeTeamCache_${getUser('sessionUser').name}`, JSON.stringify(objActiveTeamCache));
      this.isExpandAll = false;
    },
    onExpandOrCollapseItem(item){
      let strActiveTeamCache = localStorage.getItem(`activeTeamCache_${getUser('sessionUser').name}`);
      let objActiveTeamCache = {};
      if(strActiveTeamCache != null && strActiveTeamCache != ""){
        objActiveTeamCache = JSON.parse(strActiveTeamCache);
      }
      objActiveTeamCache[item.name] = !item.open;
      localStorage.setItem(`activeTeamCache_${getUser('sessionUser').name}`, JSON.stringify(objActiveTeamCache));
      item.open = !item.open;
    },
    onLoadDataTeam(){
      teams.fetch()
    },
    onLoadUnreadNotification(){
      unreadNotifications.fetch()
    }
  },
}
</script>
