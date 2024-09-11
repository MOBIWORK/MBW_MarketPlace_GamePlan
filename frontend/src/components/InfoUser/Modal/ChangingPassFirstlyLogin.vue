<template>
    <Dialog v-model="isShowDialog">
        <template #body-title>
            <h3>{{__('Changing Password')}}</h3>
        </template>
      <template #body-content>
        <div class="w-full">
            <div class="text-base mb-2">{{__('You need to change your password for the first time you log in')}}</div>
            <FrmChangingPassword @update:password="(evt) => onChangePasswordEvent(evt)"></FrmChangingPassword>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end">
            <Button
                @click="isShowDialog = false"
                >
                {{__('Cancel')}}
            </Button>
            <Button variant="solid" :disabled="disabledSave" class="ml-2" @click="onSavePassword()" :loading="loadingSave">
                {{__('Save')}}
            </Button>
        </div>
      </template>
    </Dialog>
  </template>
  <script>
  import { ref } from 'vue'
  import { Dialog } from 'frappe-ui'
  import FrmChangingPassword from '../FrmChangingPassword.vue'
  import { createToast } from '@/utils'
  
  let isShowDialog = ref(false)
  
  export function showChangingPasswordFirstlyLoginDialog() {
    isShowDialog.value = true
  }
  
  export default {
    name: 'ChangingPasswordFirstlyLoginDialog',
    components: {
      Dialog,
    },
    setup() {
      return { isShowDialog }
    },
    data(){
        return {
            disabledSave: true,
            newPassWord: '',
            loadingSave: false
        }
    },
    resources:{
        change_password(){
            return {
                url: "gameplan.api.change_password",
                method: "POST",
                auto: false,
                onSuccess(data){
                    if(data.status == "ok"){
                        createToast({
                            title: __('Change password successfully'),
                            icon: 'check',
                            iconClasses: 'text-green-600',
                        })
                        isShowDialog.value = false
                        this.newPassWord = ""
                        this.loadingSave = false
                        this.disabledSave = true
                    }else{
                        createToast({
                            title: data.message,
                            icon: 'x',
                            iconClasses: 'text-red-600',
                        })
                        this.loadingSave = false
                    }
                }
            }
        }
    },
    methods:{
        onSavePassword(){
            this.loadingSave = true
            let dataPost = {
                'new_pass': this.newPassWord
            }
            this.$resources.change_password.submit(dataPost)
        },
        onChangePasswordEvent(data){
            if(!data.enable_btn) {
                this.disabledSave = true
                this.newPassWord = ""
            }else{
                this.disabledSave = false
                this.newPassWord = data.newPass
            }
        }
    }
  }
  </script>
  