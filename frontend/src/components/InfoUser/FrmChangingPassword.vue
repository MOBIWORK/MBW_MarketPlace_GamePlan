<template>
    <div class="w-full">
        <div class="w-full mb-3 flex relative">
            <FormControl
                :type="showPassword? 'text' : 'password'"
                size="sm"
                variant="subtle"
                :placeholder="__('Enter a new password')"
                :disabled="false"
                :label="__('New password')"
                v-model="txtPassword"
                class="w-full"
            />
            <FeatherIcon
                :name="showPassword? 'eye-off' : 'eye'"
                class="h-4 w-4 absolute right-1 bottom-1 cursor-pointer"
                @click="onTogglePassword()"
            />
        </div>
        <div class="w-full flex relative">
            <FormControl
                :type="showReEnterPassword? 'text' : 'password'"
                size="sm"
                variant="subtle"
                :placeholder="__('Re-enter the password')"
                :disabled="false"
                :label="__('Re-enter password')"
                v-model="txtPasswordReEnter"
                class="w-full"
            />
            <FeatherIcon
                :name="showReEnterPassword? 'eye-off' : 'eye'"
                class="h-4 w-4 absolute right-1 bottom-1 cursor-pointer"
                @click="onToggleReEnterPassword()"
            />
        </div>
    </div>
</template>
<script>
import {FormControl, FeatherIcon} from 'frappe-ui'

export default {
    name: "FrmChangingPassword",
    components: {FormControl, FeatherIcon},
    emits: ['update:password'],
    data(){
        return {
            txtPassword: '',
            txtPasswordReEnter: '',
            showPassword: false,
            showReEnterPassword: false
        }
    },
    watch: {
        txtPassword(newPass, oldPass) {
            if(this.txtPassword == this.txtPasswordReEnter && this.txtPassword != ""){
                let dataEmit = {
                    'enable_btn': true,
                    'newPass': this.txtPassword
                }
                this.$emit('update:password', dataEmit)
            }else{
                let dataEmit = {
                    'enable_btn': false
                }
                this.$emit('update:password', dataEmit)
            }
        },
        txtPasswordReEnter(newPass, oldPass){
            if(this.txtPassword == this.txtPasswordReEnter && this.txtPasswordReEnter != ""){
                let dataEmit = {
                    'enable_btn': true,
                    'newPass': this.txtPassword
                }
                this.$emit('update:password', dataEmit)
            }else{
                let dataEmit = {
                    'enable_btn': false
                }
                this.$emit('update:password', dataEmit)
            }
        }
    },
    methods: {
        onTogglePassword(){
            this.showPassword = !this.showPassword
        },
        onToggleReEnterPassword(){
            this.showReEnterPassword = !this.showReEnterPassword
        }
    }

}
</script>