<template>
    <div class="w-full">
        <div class="flex justify-between p-1 rounded-md items-center" style="background-color: #F1F1F1;">
            <div class="font-semibold pl-2">{{title}}</div>
            <div class="pr-2 text-sm cursor-pointer" v-if="expanded" @click="onCollapseAndExpand()">Collapse</div>
            <div class="pr-2 text-sm cursor-pointer" v-if="!expanded" @click="onCollapseAndExpand()">Expand</div>
        </div>
        <div class="px-8 py-3" v-if="expanded">
            <div class="flex items-center justify-between my-2" v-for="permission in arr_permission">
                <div class="text-sm text-gray-900">{{permission.title}}</div>
                <div class="flex items-center">
                    <Checkbox size="sm" v-model="permission.email" label="Email" @update:modelValue="onChangeCheckBox(permission, 'email')"/>
                    <Checkbox class="ml-5" size="sm" v-model="permission.browser" label="Browser" @update:modelValue="onChangeCheckBox(permission, 'browser')"/>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { Checkbox, createResource } from 'frappe-ui'
import { createToast } from '@/utils'

export default {
    name: 'NotificationSettingItem',
    components: { Checkbox },
    props: {
        id: {
            type: String
        },
        title: {
            type: String
        },
        arr_permission: {
            type: Array
        }
    },
    data() {
        return {
            expanded: true
        }
    },
    methods: {
        onCollapseAndExpand(){
            this.expanded = !this.expanded;
        },
        onChangeCheckBox(item, type_notify){
            let changeConfigNotification = createResource({
                url: "gameplan.api.change_config_notification",
                method: "GET",
                params: {
                    id_config: item['id'],
                    type_notify: type_notify,
                    value_notify: type_notify=="email"? item['email'] : item['browser']
                },
                onSuccess(data){
                    console.log(data)
                    if(data == "ok"){
                        console.log("vào đây")
                        createToast({
                            title: __('Đã lưu thành công'),
                            icon: 'check',
                            iconClasses: 'text-green-600',
                        })
                    }else{
                        createToast({
                            title: __('Lưu thất bại'),
                            icon: 'x',
                            iconClasses: 'text-red-600',
                        })
                    }
                }
            })
            changeConfigNotification.fetch();
        }
    },
}

</script>