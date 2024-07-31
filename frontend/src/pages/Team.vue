<template>
  <div class="pb-20">
    <header class="sticky top-0 z-10 border-b bg-white px-5 py-2.5">
      <div class="flex items-center justify-between" @mouseenter="onMouseEnterNameTeam()" @mouseleave="onMouseLeaveNameTeam()">
        <div class="flex items-center" v-if="!showLayoutInputNameTeam">
          <Breadcrumbs
            class="h-7"
            :items="[
              {
                label: team.doc.title,
                route: { name: 'Team', params: { teamId: team.doc.name } },
              },
            ]"
          >
            <template #prefix>
              <IconPicker
                v-model="team.doc.icon"
                @update:modelValue="
                  team.setValueDebounced.submit({ icon: team.doc.icon })
                "
                v-slot="{ isOpen }"
              >
                <button
                  class="mr-2 flex rounded-sm text-2xl leading-none"
                  :class="isOpen ? 'bg-gray-200' : 'hover:bg-gray-100'"
                >
                  {{ team.doc.icon }}
                </button>
              </IconPicker>
            </template>
          </Breadcrumbs>
          <span class="ml-2 cursor-pointer" @click="handleEditNameProject()" v-if="showControlEditNameTeam">
            <LucideEdit2 class="w-4" />
          </span>
        </div>
        <div class="flex items-center" v-if="showLayoutInputNameTeam">
          <TextInput
            :type="'text'"
            size="sm"
            variant="outline"
            :disabled="false"
            v-model="nameTeamNew"
          />
          <Button class="ml-2" @click="() => onSaveNameTeam()">
            <template #prefix><LucideSave class="w-4" /></template>
            {{__('Save')}}
          </Button>
          <Button class="ml-3" @click="() => onDiscardEditNameTeam()">
            <template #prefix><LucideRotateCcw class="w-4" /></template>
            {{__('Discard')}}
          </Button>
        </div>
        <div class="flex items-center space-x-2">
          <TeamMembers :team="team" />
          <Dropdown
            v-if="!team.doc.archived_at && !readOnlyByRole()"
            placement="left"
            :options="[
              {
                label: __('Set cover image'),
                icon: 'image',
                condition: () => !team.doc.cover_image,
                onClick: () => (showCoverImage = true),
              },
              {
                label: __('Archive'),
                icon: 'trash-2',
                onClick: () => archiveTeam(),
              },
            ]"
            :button="{
              label: __('Options'),
              variant: 'ghost',
              icon: 'more-horizontal',
            }"
          />
        </div>
      </div>
    </header>
    <CoverImage
      v-if="showCoverImage"
      :imageUrl="team.doc.cover_image"
      :imagePosition="team.doc.cover_image_position"
      :editable="true"
      @change="
        ({ imageUrl, imagePosition }) => {
          team.setValue.submit({
            cover_image: imageUrl,
            cover_image_position: imagePosition,
          })
        }
      "
    />
    <Dialog
      :options="{
        title: __('Archive Team'),
        message: __('Are you sure you want to archive the team?'),
        actions: [
          {
            label: __('Archive'),
            variant: 'solid',
            onClick: ({ close }) => {
              return this.team.archive.submit(null, {
                onSuccess: () => {
                  this.$router.replace({ name: 'Home' })
                  showArchiveDialog = false
                },
              })
            },
          },
        ],
      }"
      v-model="showArchiveDialog"
    />
    <router-view class="mx-auto px-5" :team="team" />
  </div>
</template>
<script>
import { Breadcrumbs, Dropdown, Badge, Tooltip,Dialog } from 'frappe-ui'
import IconPicker from '@/components/IconPicker.vue'
import Tabs from '@/components/Tabs.vue'
import { createToast } from '@/utils'

export default {
  name: 'Team',
  props: ['team'],
  components: {
    Breadcrumbs,
    Dropdown,
    IconPicker,
    Tabs,
    Tooltip,
    Badge,
  },
  data() {
    return {
      showCoverImage: Boolean(this.team.doc.cover_image),
      showArchiveDialog: false,
      showControlEditNameTeam: false,
      showLayoutInputNameTeam: false,
      nameTeamNew: ""
    }
  },
  methods: {
    updateTeamIcon(icon) {
      this.team.setValue.submit({ icon })
    },
    archiveTeam() {
      this.showArchiveDialog = true;
    },
    handleEditNameProject() {
      this.nameTeamNew = this.team.doc.title;
      this.showLayoutInputNameTeam = true;
    },
    onMouseEnterNameTeam() {
      this.showControlEditNameTeam = true;
    },
    onMouseLeaveNameTeam(){
      this.showControlEditNameTeam = false;
    },
    onDiscardEditNameTeam(){
      this.showLayoutInputNameTeam = false;
    },
    onSaveNameTeam(){
      if(this.nameTeamNew == null || this.nameTeamNew == ""){
        createToast({
          title: __('Team name is not empty or null'),
          icon: 'x',
          iconClasses: 'text-red-600',
        })
        return;
      }
      this.team.setValue.submit({ title:  this.nameTeamNew});
      this.showLayoutInputNameTeam = false;
    },
    readOnlyByRole(){
      let role = this.$getRoleByUser(this.team.doc, null);
      if (role == "member" || role == "guest") return true
      return false
    }
  },
}
</script>
