<template>
    <div class="pb-3 transition-shadow" :class="{ ring: highlight }">
      <div class="mb-2 flex items-center text-base text-gray-900">
        <UserInfo :email="_poll.owner" v-slot="{ user }">
          <UserProfileLink class="mr-3" :user="user.name">
            <UserAvatar :user="user.name" size="xl" />
          </UserProfileLink>
          <div class="md:flex md:items-center">
            <UserProfileLink
              class="font-medium hover:text-blue-600"
              :user="user.name"
            >
              {{ user.full_name }}
              <span class="hidden md:inline">&nbsp;&middot;&nbsp;</span>
            </UserProfileLink>
            <div>
              <time
                class="text-gray-600"
                :datetime="_poll.creation"
                :title="$dayjs(_poll.creation)"
              >
                {{ $dayjs(_poll.creation).fromNow() }}
              </time>
            </div>
          </div>
        </UserInfo>
        <div class="ml-auto flex items-center space-x-2">
          <Button
            v-if="!isStopped && $isSessionUser(_poll.owner)"
            variant="ghost"
            @click="stopPoll"
          >
            <template #prefix><LucideMinusCircle class="w-4" /></template>
            {{__('Stop Poll')}}
          </Button>
          <Tooltip v-else text="This is a poll">
            <LucideBarChart2 class="h-4 w-4 -rotate-90" />
          </Tooltip>
          <Dropdown
            placement="right"
            :button="{
              icon: 'more-horizontal',
              variant: 'ghost',
              label: __('Poll Options'),
            }"
            :options="dropdownOptions"
          />
        </div>
      </div>
      <div class="text-base font-semibold">{{ _poll.title }}</div>
      <div class="mt-1 text-sm text-gray-600">
        <span v-if="_poll.multiple_answers"> {{__('Multiple answers')}} &middot; </span>
        <span v-if="_poll.anonymous"> {{__('Anonymous')}} &middot; </span>
        <span>
          {{ _poll.total_votes }} {{ _poll.total_votes === 1 ? __('vote') : __('votes') }}
        </span>
        <span v-if="_poll.stopped_at"> &middot; {{ stopTime }} </span>
      </div>
      <div class="my-4 space-y-2">
        <button
          class="group flex items-center text-gray-900"
          v-for="option in _poll.options"
          :key="option.idx"
          @click="submitVote(option)"
          :disabled="
            participated || isStopped || $resources.pollDoc.submitVote.loading
          "
        >
          <div
            class="mr-2 h-4 w-4 rounded-full border-2 text-sm"
            :class="
              isVotedByUser(option.title)
                ? 'border-gray-900 bg-gray-900'
                : participated || isStopped
                ? 'border-gray-300'
                : 'border-gray-300 group-hover:border-gray-400'
            "
          >
            <LucideCheck
              v-if="isVotedByUser(option.title)"
              class="h-3 w-3 text-white"
              :stroke-width="2.5"
            />
          </div>
          <div class="flex items-baseline">
            <div class="text-base">{{ option.title }}</div>
            <div class="ml-1 text-base text-gray-600" v-if="participated">
              ({{ option.percentage }}%)
            </div>
          </div>
        </button>
      </div>
      <div class="mt-3">
        <Reactions
          doctype="GP Poll"
          :name="poll.name"
          :reactions="_poll.reactions"
        />
      </div>
      <Dialog
        :options="{ title: __('Poll results') }"
        v-model="showDialog"
        v-if="pollResults"
      >
        <template #body-content>
          <h2 class="text-lg font-semibold">{{ _poll.title }}</h2>
          <div class="mt-2 space-y-4">
            <div v-for="option in pollResults" :key="option.title">
              <div class="flex items-center">
                <h3 class="text-base font-medium">{{ option.title }}</h3>
  
                <div class="mx-2 flex-1 border-b"></div>
                <div class="text-base text-gray-600">
                  {{ option.votes }} {{ option.votes === 1 ? __('vote') : __('votes') }}
                </div>
                <div class="ml-1 text-base text-gray-600">
                  ({{ option.percentage }}%)
                </div>
              </div>
              <div class="py-2" v-for="user in option.voters" :key="user">
                <UserInfo :email="user" v-slot="{ user: _user }">
                  <UserProfileLink :user="_user.name">
                    <div class="flex items-center space-x-2">
                      <UserAvatar size="sm" :user="_user.name" />
                      <span class="text-base">{{ _user.full_name }}</span>
                    </div>
                  </UserProfileLink>
                </UserInfo>
              </div>
            </div>
          </div>
        </template>
      </Dialog>
      <Dialog 
        :options="{
          title: __('Anonymous poll'),
          message: __('This poll is anonymous. Once you vote, you cannot retract your vote. You are voting for {0}. Continue?', [optionVote.title]),
          actions: [
            {
              label: __('Vote for {0}', [optionVote.title]),
              variant: 'solid',
              onClick: ({ close }) => {
                this.$resources.pollDoc.submitVote
                    .submit({ option: optionVote.title })
                    .then(() => { showAnonymousPollDialog = false })
              },
            },
          ],
        }"
        v-model="showAnonymousPollDialog"
      />
      <Dialog 
        :options="{
          title: __('Stop poll'),
          message: __('After the poll is stopped, no one will be able to vote on it. Continue?'),
          actions: [
            {
              label: __('Stop'),
              variant: 'solid',
              theme: 'red',
              onClick: ({ close }) =>
                this.$resources.pollDoc.stopPoll.submit().then(() => { showStopPollDialog = false }),
            },
          ],
        }"
        v-model="showStopPollDialog"
      />
      <Dialog 
        :options="{
          title: __('Retract vote'),
          message: __('Are you sure you want to retract your vote?'),
          actions: [
            {
              label: __('Retract vote'),
              variant: 'solid',
              theme: 'red',
              onClick: ({ close }) =>
                this.$resources.pollDoc.retractVote.submit().then(() => { showRetractVoteDialog = false }),
              },
          ],
        }"
        v-model="showRetractVoteDialog"
      />
      <Dialog 
        :options="{
          title: __('Delete poll'),
          message: __('Are you sure you want to delete this poll?'),
          actions: [
            {
              label: __('Delete'),
              variant: 'solid',
              theme: 'red',
              onClick: ({ close }) =>
                this.$resources.pollDoc.delete.submit().then(() => { showDeletePollDialog = false }),
            },
          ],
        }"
        v-model="showDeletePollDialog"
      />
    </div>
  </template>
  <script>
  import { Dropdown, Dialog, Tooltip } from 'frappe-ui'
  import UserAvatar from '@/components/UserAvatar.vue'
  import UserProfileLink from '@/components/UserProfileLink.vue'
  import { copyToClipboard } from '@/utils'
  import Reactions from '@/components/Reactions.vue'
  
  export default {
    name: 'PollDiscussion',
    props: {
      poll: {
        type: Object,
        required: true,
      },
      highlight: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['vote'],
    components: {
      UserProfileLink,
      UserAvatar,
      Dropdown,
      Tooltip,
      Reactions,
      Dialog,
    },
    data() {
      return {
        showDialog: false,
        showAnonymousPollDialog: false,
        optionVote: {},
        showStopPollDialog: false,
        showRetractVoteDialog: false,
        showDeletePollDialog: false
      }
    },
    resources: {
      pollDoc() {
        return {
          type: 'document',
          doctype: 'GP Poll',
          name: this.poll.name,
          auto: false,
          realtime: true,
          whitelistedMethods: {
            submitVote: 'submit_vote',
            stopPoll: 'stop_poll',
            retractVote: 'retract_vote',
          },
        }
      },
    },
    methods: {
      submitVote(option) {
        if (this._poll.anonymous) {
          this.optionVote = option;
          this.showAnonymousPollDialog = true;
        } else {
          if (this.$resources.pollDoc.doc) {
            this.$resources.pollDoc.submitVote.submit({ option: option.title })
          } else {
            this.$resources.pollDoc.get.fetch().then(() => {
              this.$resources.pollDoc.submitVote.submit({ option: option.title })
            })
          }
        }
      },
      stopPoll() {
        this.showStopPollDialog = true;
      },
      isVotedByUser(option) {
        return this._poll.votes.find(
          (vote) => vote.option === option && vote.user === this.$user().name
        )
      },
      copyLink() {
        let location = window.location
        let url = `${location.origin}${location.pathname}?poll=${this.poll.name}`
        copyToClipboard(url)
      },
    },
    computed: {
      participated() {
        return this._poll.votes.some((d) => d.user === this.$user().name) ?? false
      },
      pollResults() {
        if (!this.$resources.pollDoc.doc || this._poll.anonymous) return null
        return this._poll.options.map((option) => {
          return {
            title: option.title,
            votes: option.votes,
            percentage: option.percentage,
            voters: this._poll.votes
              .filter((vote) => vote.option === option.title)
              .map((vote) => vote.user),
          }
        })
      },
      dropdownOptions() {
        return [
          {
            label: __('Show results'),
            icon: 'bar-chart-2',
            condition: () => this.pollResults,
            onClick: () => {
              this.showDialog = true
            },
          },
          {
            label: __('Retract vote'),
            icon: 'corner-up-left',
            condition: () =>
              !this._poll.anonymous &&
              this.participated &&
              (!this._poll.stopped_at ||
                this.$dayjs().isBefore(this._poll.stopped_at)),
            onClick: () => {
              this.showRetractVoteDialog = true;
            },
          },
          {
            label: __('Copy link'),
            icon: 'link',
            onClick: this.copyLink,
          },
          {
            label: __('Delete'),
            icon: 'trash',
            condition: () => this.$isSessionUser(this._poll.owner),
            onClick: () => {
              this.showDeletePollDialog = true;
            },
          },
        ]
      },
      isStopped() {
        return (
          this._poll.stopped_at && this.$dayjs().isAfter(this._poll.stopped_at)
        )
      },
      stopTime() {
        let timestamp = this._poll.stopped_at
        if (this.$dayjs().diff(timestamp, 'day') < 7) {
          return `${__('Ended')} ${this.$dayjs(timestamp).fromNow()}`
        }
        if (this.$dayjs().diff(timestamp, 'year') < 1) {
          return `${__('Ended at')} ${this.$dayjs(timestamp).format('D MMM, h:mm A')}`
        }
        return `${__('Ended at')} ${this.$dayjs(timestamp).format('D MMM YYYY, h:mm A')}`
      },
      _poll() {
        return this.$resources.pollDoc.doc || this.poll
      },
    },
  }
  </script>
  