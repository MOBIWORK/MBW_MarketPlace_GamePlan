<template>
    <IconPicker
        v-model="emoji"
        v-slot="{ togglePopover }"
        @update:modelValue="
          () => onUpdateEmoji()
        "
      >
        <SmileIcon
          @click="togglePopover"
          class="flex size-4.5 cursor-pointer rounded-sm text-xl leading-none h-4 w-4"
        />
      </IconPicker>
</template>

<script>
import IconPicker from '@/components/IconPicker.vue'
import SmileIcon from '@/components/icons/SmileIcon.vue'


export default {
    name: "CommentReactionEditor",
    emits: ['selectEmoji'],
    components: { IconPicker, SmileIcon },
    data(){
        return {
            emoji: ''
        }
    },
    methods: {
        onUpdateEmoji(){
            this.$emit('selectEmoji', this.emoji)
        }
    },
    computed: {

    }
}
</script>

<style scoped>
</style>