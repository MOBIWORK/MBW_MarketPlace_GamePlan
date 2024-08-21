<template>
    <div class="flex items-center relative">
        <template v-for="assign in arr_user">
            <UserAvatar :user="assign.user" :check_user="assign.is_check" :active_check="true" size="md" @activeUserEvent="(evt) =>onActiveUser(evt)" @deactiveUserEvent="(evt) => onDeactiveUser(evt)"/>
        </template>
        <div id="user_list" v-show="sub_count_user > 0" class="w-7 h-7 rounded-full p-2 bg-gray-100	text-sm flex justify-center items-center text-gray-700 cursor-pointer" @click="onMoreAssignTask()">
          +{{sub_count_user}}
        </div>
        <div v-show="showSelectAssignTask" ref="target" class="absolute bg-white p-2 rounded-lg shadow-lg top-full mt-2 left-0 right-0 z-10 w-fit">
            <div class="flex items-center mb-2" v-for="user_check in arr_user_check">
                <Checkbox
                    size="md"
                    v-model="user_check.is_check"
                    class="mr-1"
                    @update:modelValue="onChangeCheck(user_check)"
                />
                <UserAvatar :user="user_check.user" size="md"/>
                <div class="ml-2 text-base font-medium text-gray-900">
                    {{ $user(user_check.user).full_name }}
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { onClickOutside } from '@vueuse/core'
import { ref } from 'vue'
import { Checkbox } from 'frappe-ui'

export default {
    name: "FilterAssignTask",
    props: {
        arrAssign: {
            type: Array
        }
    },
    components: {
        Checkbox
    },
    emits: ['filter_assign'],
    data(){
        return {
            arr_user_active: [],
            showSelectAssignTask: false,
            target: null
        }
    },
    methods: {
        onActiveUser(data){
            if(this.arr_user_active.indexOf(data) < 0) this.arr_user_active.push(data)
            this.$emit('filter_assign', this.arr_user_active)
        },
        onDeactiveUser(data){
            if(this.arr_user_active.indexOf(data) >= 0){
                let index = this.arr_user_active.indexOf(data)
                this.arr_user_active.splice(index, 1)
            }
            this.$emit('filter_assign', this.arr_user_active)
        },
        onMoreAssignTask(){
            this.showSelectAssignTask = true
        },
        onChangeCheck(user_check){
            if(user_check.is_check){
                if(this.arr_user_active.indexOf(user_check.user) == -1) this.arr_user_active.push(user_check.user)
            }else{
                let index = this.arr_user_active.indexOf(user_check.user)
                if(index > -1) this.arr_user_active.splice(index, 1)
            }
            this.$emit('filter_assign', this.arr_user_active)
        }
    },
    computed: {
        arr_user(){
            let users = []
            if(this.arrAssign.length > 5){
                users = this.arrAssign.slice(0,5)
            }else{
                users = this.arrAssign
            }
            return users.map(user => ({
                user,
                is_check: this.arr_user_active.includes(user)
            }));
        },
        sub_count_user(){
            if(this.arrAssign.length <= 5) return 0
            return this.arrAssign.length -5
        },
        arr_user_check(){
            let arr_user_check = []
            for(let i = 0; i < this.arrAssign.length; i++){
                let user_check = {
                    is_check: false,
                    user: this.arrAssign[i]
                }
                if(this.arr_user_active.indexOf(this.arrAssign[i]) > -1) user_check.is_check = true
                arr_user_check.push(user_check)
            }
            return arr_user_check
        }
    },
    mounted(){
        const closePanel = () => {
            this.showSelectAssignTask = false
        }
        onClickOutside(this.$refs.target, closePanel, { ignore: ['#user_list'] })
    }

}
</script>