<template>
  <div class="flex min-h-0 flex-col">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-semibold leading-none">{{__('Members')}}</h2>
      <div class="flex items-center gap-4">
        <FormControl
          :placeholder="__('Search')"
          @input="search = $event.target.value"
          :debounce="300"
        >
          <template #prefix>
            <LucideSearch class="h-4 w-4 text-gray-500" />
          </template>
        </FormControl>
      </div>
    </div>
    <ul class="mt-6 divide-y overflow-auto pb-16">
      <li
        class="flex items-center justify-between p-2"
        v-for="user in filteredUsers"
        :key="user.name"
      >
        <div class="flex w-4/5 items-center">
          <UserAvatar :user="user.name" size="xl" />
          <div class="ml-3">
            <div class="text-base text-gray-900">
              {{ user.full_name }}
            </div>
            <div class="mt-1 text-base text-gray-700">
              {{ user.email }}
            </div>
          </div>
        </div>
        <div class="flex w-1/5">
          <Dropdown
            :options="getDropdownOptions(user)"
            :button="{
              label: getUserRole(user),
              iconRight: 'chevron-down',
              variant: 'ghost',
            }"
            placement="right"
          ></Dropdown>
        </div>
      </li>
    </ul>
  </div>
  <Dialog
    :options="changeRoleDialogOptions"
    v-model="showChangeUserRoleDialog"
  />
  <Dialog
    :options="removeUserDialogOption"
    v-model="showRemoveUserDialog"
  />
</template>
<script>
import { h, computed } from 'vue'
import { Dropdown, Dialog } from 'frappe-ui'
import { users, activeUsers } from '@/data/users'
import LucideCheck from '~icons/lucide/check'

export default {
  name: 'Members',
  components: { Dropdown },
  resources: {
    changeUserRole() {
      return {
        url: 'gameplan.api.change_user_role',
        onSuccess(user) {
          users.setData((data) => {
            return data.map((_user) => {
              if (_user.name === user.name) {
                return user
              }
              return _user
            })
          })
        },
      }
    },
    removeUser() {
      return {
        url: 'gameplan.api.remove_user',
        onSuccess(user) {
          users.setData((data) => data.filter((_user) => _user.name !== user))
        },
      }
    },
  },
  data() {
    return {
      search: '',
      userChange: {},
      roleChange: "",
      showChangeUserRoleDialog: false,
      userRemove: {},
      showRemoveUserDialog: false
    }
  },
  computed: {
    filteredUsers() {
      if (!this.search) {
        return activeUsers.value
      }
      return activeUsers.value.filter((user) => {
        let term = this.search.toLowerCase()
        return (
          user.name.toLowerCase().includes(term) ||
          user.full_name.toLowerCase().includes(term)
        )
      })
    },
    changeRoleDialogOptions() {
      const error = this.$resources.changeUserRole.error;
      return {
        title: __('Change Role'),
        message: __('Are you sure you want to change role of {0} to {1}?', [this.userChange.full_name, this.roleChange]),
        error: error,
        actions: [
          {
            label: __('Change Role'),
            variant: 'solid',
            onClick: ({ close }) => {
              return this.$resources.changeUserRole.submit(
                { user: this.userChange.name, role: this.roleChange },
                { onSuccess: () => { this.showChangeUserRoleDialog = false } }
              )
            },
          },
          {
            label: __('Cancel'),
          }
        ],
      };
    },
    removeUserDialogOption() {
      const errorRemoveUser = this.$resources.removeUser.error;
      return{
        title: __('Remove User'),
        message: __('Are you sure you want to remove {0} ({1})?', [this.userRemove.full_name, this.userRemove.email]),
        error: errorRemoveUser,
        actions: [
          {
            label: __('Remove User'),
            variant: 'solid',
            theme: 'red',
            onClick: ({ close }) => {
              return this.$resources.removeUser.submit(
                { user: this.userRemove.name },
                { onSuccess: () => { this.showRemoveUserDialog = false } }
              )
            },
          },
          {
            label: __('Cancel'),
          },
        ],
      }
    }
  },
  methods: {
    changeUserRole({ user, role }) {
      this.userChange = user;
      this.roleChange = role;
      this.showChangeUserRoleDialog = true;
    },
    removeUser(user) {
      this.userRemove = user;
      this.showRemoveUserDialog = true;
    },
    getUserRole(user) {
      return (user.role || '').replace('Gameplan', '')
    },
    getDropdownOptions(user) {
      return [
        {
          label: __('Admin'),
          component: (props) =>
            RoleOption({
              role: 'Admin',
              active: props.active,
              selected: user.role === 'Gameplan Admin',
              onClick: () =>
                this.changeUserRole({
                  user: user,
                  role: 'Gameplan Admin',
                }),
            }),
        },
        {
          label: __('Member'),
          component: (props) =>
            RoleOption({
              role: 'Member',
              active: props.active,
              selected: user.role === 'Gameplan Member',
              onClick: () =>
                this.changeUserRole({
                  user: user,
                  role: 'Gameplan Member',
                }),
            }),
        },
        {
          label: __('Guest'),
          component: (props) =>
            RoleOption({
              role: 'Guest',
              active: props.active,
              selected: user.role === 'Gameplan Guest',
              onClick: () =>
                this.changeUserRole({
                  user: user,
                  role: 'Gameplan Guest',
                }),
            }),
        },
        {
          label: __('Remove'),
          component: (props) =>
            h(
              'button',
              {
                class: [
                  props.active ? 'bg-gray-100' : '',
                  'group flex w-full items-center text-red-500 rounded-md px-2 py-2 text-sm',
                ],
                onClick: () => this.removeUser(user),
              },
              'Remove'
            ),
        },
      ]
    },
  },
}

function RoleOption({ active, role, onClick, selected }) {
  return h(
    'button',
    {
      class: [
        active ? 'bg-gray-100' : 'text-gray-900',
        'group flex w-full justify-between items-center rounded-md px-2 py-2 text-sm',
      ],
      onClick: !selected ? onClick : null,
    },
    [
      h('span', { class: 'whitespace-nowrap' }, role),
      selected
        ? h(LucideCheck, {
            class: ['h-4 w-4 shrink-0 text-gray-700'],
            'aria-hidden': true,
          })
        : null,
    ]
  )
}
</script>
