<template>
    <div class="w-full flex justify-between">
        <div class="flex items-center">
            <div class="text-1xl font-semibold mr-2">{{__('Attachments')}}</div>
            <div class="w-6 h-6 rounded-full p-2 bg-gray-200 text-sm flex justify-center items-center text-gray-800">{{numAttach}}</div>
        </div>
        <div class="flex items-center" v-if="!readOnly">
            <Button class="mr-2" :variant="'outline'" theme="red" size="sm" :loading="false" @click="onDeleteAll()" v-if="numAttach>0">{{__('Delete all')}}</Button>
            <Button :variant="'outline'" theme="gray" size="sm" :loading="false" @click="onAddAttachment()">{{__('New attachment')}}</Button>
            <input type="file" ref="fileInput" @change="handleFileChange" class="hidden" multiple>
        </div>
    </div>
    <div class="flex mt-1 flex-wrap" v-if="numAttach>0">
        <div class="w-56 shadow-gray-900 rounded-lg border mr-3 mt-2" style="height: 10.5rem;" v-for="attach in arrAttach">
            <div class="w-full h-28 group flex items-center justify-center relative">
                <svg xmlns="http://www.w3.org/2000/svg" fill="#FFF" stroke-miterlimit="10" stroke-width="2" viewBox="0 0 96 96" style="width: 95px;" v-if="attach.file_type=='DOCX'">
                    <path stroke="#979593" d="M67.1716 7H27c-1.1046 0-2 .8954-2 2v78c0 1.1046.8954 2 2 2h58c1.1046 0 2-.8954 2-2V26.8284c0-.5304-.2107-1.0391-.5858-1.4142L68.5858 7.5858C68.2107 7.2107 67.702 7 67.1716 7z"/>
                    <path fill="none" stroke="#979593" d="M67 7v18c0 1.1046.8954 2 2 2h18"/>
                    <path fill="#C8C6C4" d="M79 61H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1zm0-6H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1zm0-6H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1zm0-6H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1zm0 24H48v-2h31c.5523 0 1 .4477 1 1s-.4477 1-1 1z"/>
                    <path fill="#185ABD" d="M12 74h32c2.2091 0 4-1.7909 4-4V38c0-2.2091-1.7909-4-4-4H12c-2.2091 0-4 1.7909-4 4v32c0 2.2091 1.7909 4 4 4z"/>
                    <path d="M21.6245 60.6455c.0661.522.109.9769.1296 1.3657h.0762c.0306-.3685.0889-.8129.1751-1.3349.0862-.5211.1703-.961.2517-1.319L25.7911 44h4.5702l3.6562 15.1272c.183.7468.3353 1.6973.457 2.8532h.0608c.0508-.7979.1777-1.7184.3809-2.7615L37.8413 44H42l-5.1183 22h-4.86l-3.4885-14.5744c-.1016-.4197-.2158-.9663-.3428-1.6417-.127-.6745-.2057-1.1656-.236-1.4724h-.0608c-.0407.358-.1195.8896-.2364 1.595-.1169.7062-.211 1.2273-.2819 1.565L24.1 66h-4.9357L14 44h4.2349l3.1843 15.3882c.0709.3165.1392.7362.2053 1.2573z"/>
                </svg>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" fill="#FFF" stroke-miterlimit="10" stroke-width="2" style="width: 95px;" v-else-if="attach.file_type=='XLSX' || attach.file_type=='XLS'">
                    <path stroke="#979593" d="M67.1716,7H27c-1.1046,0-2,0.8954-2,2v78 c0,1.1046,0.8954,2,2,2h58c1.1046,0,2-0.8954,2-2V26.8284c0-0.5304-0.2107-1.0391-0.5858-1.4142L68.5858,7.5858 C68.2107,7.2107,67.702,7,67.1716,7z"/>
                    <path fill="none" stroke="#979593" d="M67,7v18c0,1.1046,0.8954,2,2,2h18"/>
                    <path fill="#C8C6C4" d="M51 61H41v-2h10c.5523 0 1 .4477 1 1l0 0C52 60.5523 51.5523 61 51 61zM51 55H41v-2h10c.5523 0 1 .4477 1 1l0 0C52 54.5523 51.5523 55 51 55zM51 49H41v-2h10c.5523 0 1 .4477 1 1l0 0C52 48.5523 51.5523 49 51 49zM51 43H41v-2h10c.5523 0 1 .4477 1 1l0 0C52 42.5523 51.5523 43 51 43zM51 67H41v-2h10c.5523 0 1 .4477 1 1l0 0C52 66.5523 51.5523 67 51 67zM79 61H69c-.5523 0-1-.4477-1-1l0 0c0-.5523.4477-1 1-1h10c.5523 0 1 .4477 1 1l0 0C80 60.5523 79.5523 61 79 61zM79 67H69c-.5523 0-1-.4477-1-1l0 0c0-.5523.4477-1 1-1h10c.5523 0 1 .4477 1 1l0 0C80 66.5523 79.5523 67 79 67zM79 55H69c-.5523 0-1-.4477-1-1l0 0c0-.5523.4477-1 1-1h10c.5523 0 1 .4477 1 1l0 0C80 54.5523 79.5523 55 79 55zM79 49H69c-.5523 0-1-.4477-1-1l0 0c0-.5523.4477-1 1-1h10c.5523 0 1 .4477 1 1l0 0C80 48.5523 79.5523 49 79 49zM79 43H69c-.5523 0-1-.4477-1-1l0 0c0-.5523.4477-1 1-1h10c.5523 0 1 .4477 1 1l0 0C80 42.5523 79.5523 43 79 43zM65 61H55c-.5523 0-1-.4477-1-1l0 0c0-.5523.4477-1 1-1h10c.5523 0 1 .4477 1 1l0 0C66 60.5523 65.5523 61 65 61zM65 67H55c-.5523 0-1-.4477-1-1l0 0c0-.5523.4477-1 1-1h10c.5523 0 1 .4477 1 1l0 0C66 66.5523 65.5523 67 65 67zM65 55H55c-.5523 0-1-.4477-1-1l0 0c0-.5523.4477-1 1-1h10c.5523 0 1 .4477 1 1l0 0C66 54.5523 65.5523 55 65 55zM65 49H55c-.5523 0-1-.4477-1-1l0 0c0-.5523.4477-1 1-1h10c.5523 0 1 .4477 1 1l0 0C66 48.5523 65.5523 49 65 49zM65 43H55c-.5523 0-1-.4477-1-1l0 0c0-.5523.4477-1 1-1h10c.5523 0 1 .4477 1 1l0 0C66 42.5523 65.5523 43 65 43z"/>
                    <path fill="#107C41" d="M12,74h32c2.2091,0,4-1.7909,4-4V38c0-2.2091-1.7909-4-4-4H12c-2.2091,0-4,1.7909-4,4v32 C8,72.2091,9.7909,74,12,74z"/>
                    <path d="M16.9492,66l7.8848-12.0337L17.6123,42h5.8115l3.9424,7.6486c0.3623,0.7252,0.6113,1.2668,0.7471,1.6236 h0.0508c0.2617-0.58,0.5332-1.1436,0.8164-1.69L33.1943,42h5.335l-7.4082,11.9L38.7168,66H33.041l-4.5537-8.4017 c-0.1924-0.3116-0.374-0.6858-0.5439-1.1215H27.876c-0.0791,0.2684-0.2549,0.631-0.5264,1.0878L22.6592,66H16.9492z"/>
                </svg>
                <svg xmlns="http://www.w3.org/2000/svg" width="75.320129mm" height="92.604164mm" viewBox="0 0 75.320129 92.604164" style="width: 65px;height: 80px;" v-else-if="attach.file_type=='PDF'">
                    <g transform="translate(53.548057 -183.975276) scale(1.4843)">
                        <path fill="#ff2116" d="M-29.632812 123.94727c-3.551967 0-6.44336 2.89347-6.44336 6.44531v49.49804c0 3.55185 2.891393 6.44532 6.44336 6.44532H8.2167969c3.5519661 0 6.4433591-2.89335 6.4433591-6.44532v-40.70117s.101353-1.19181-.416015-2.35156c-.484969-1.08711-1.275391-1.84375-1.275391-1.84375a1.0584391 1.0584391 0 0 0-.0059-.008l-9.3906254-9.21094a1.0584391 1.0584391 0 0 0-.015625-.0156s-.8017392-.76344-1.9902344-1.27344c-1.39939552-.6005-2.8417968-.53711-2.8417968-.53711l.021484-.002z" color="#000" font-family="sans-serif" overflow="visible" paint-order="markers fill stroke" style="line-height:normal;font-variant-ligatures:normal;font-variant-position:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-alternates:normal;font-feature-settings:normal;text-indent:0;text-align:start;text-decoration-line:none;text-decoration-style:solid;text-decoration-color:#000000;text-transform:none;text-orientation:mixed;white-space:normal;shape-padding:0;isolation:auto;mix-blend-mode:normal;solid-color:#000000;solid-opacity:1"/>
                        <path fill="#f5f5f5" d="M-29.632812 126.06445h28.3789058a1.0584391 1.0584391 0 0 0 .021484 0s1.13480448.011 1.96484378.36719c.79889772.34282 1.36536982.86176 1.36914062.86524.0000125.00001.00391.004.00391.004l9.3671868 9.18945s.564354.59582.837891 1.20899c.220779.49491.234375 1.40039.234375 1.40039a1.0584391 1.0584391 0 0 0-.002.0449v40.74609c0 2.41592-1.910258 4.32813-4.3261717 4.32813H-29.632812c-2.415914 0-4.326172-1.91209-4.326172-4.32813v-49.49804c0-2.41603 1.910258-4.32813 4.326172-4.32813z" color="#000" font-family="sans-serif" overflow="visible" paint-order="markers fill stroke" style="line-height:normal;font-variant-ligatures:normal;font-variant-position:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-alternates:normal;font-feature-settings:normal;text-indent:0;text-align:start;text-decoration-line:none;text-decoration-style:solid;text-decoration-color:#000000;text-transform:none;text-orientation:mixed;white-space:normal;shape-padding:0;isolation:auto;mix-blend-mode:normal;solid-color:#000000;solid-opacity:1"/>
                        <path fill="#ff2116" d="M-23.40766 161.09299c-1.45669-1.45669.11934-3.45839 4.39648-5.58397l2.69124-1.33743 1.04845-2.29399c.57665-1.26169 1.43729-3.32036 1.91254-4.5748l.8641-2.28082-.59546-1.68793c-.73217-2.07547-.99326-5.19438-.52872-6.31588.62923-1.51909 2.69029-1.36323 3.50626.26515.63727 1.27176.57212 3.57488-.18329 6.47946l-.6193 2.38125.5455.92604c.30003.50932 1.1764 1.71867 1.9475 2.68743l1.44924 1.80272 1.8033728-.23533c5.72900399-.74758 7.6912472.523 7.6912472 2.34476 0 2.29921-4.4984914 2.48899-8.2760865-.16423-.8499666-.59698-1.4336605-1.19001-1.4336605-1.19001s-2.3665326.48178-3.531704.79583c-1.202707.32417-1.80274.52719-3.564509 1.12186 0 0-.61814.89767-1.02094 1.55026-1.49858 2.4279-3.24833 4.43998-4.49793 5.1723-1.3991.81993-2.86584.87582-3.60433.13733zm2.28605-.81668c.81883-.50607 2.47616-2.46625 3.62341-4.28553l.46449-.73658-2.11497 1.06339c-3.26655 1.64239-4.76093 3.19033-3.98386 4.12664.43653.52598.95874.48237 2.01093-.16792zm21.21809-5.95578c.80089-.56097.68463-1.69142-.22082-2.1472-.70466-.35471-1.2726074-.42759-3.1031574-.40057-1.1249.0767-2.9337647.3034-3.2403347.37237 0 0 .993716.68678 1.434896.93922.58731.33544 2.0145161.95811 3.0565161 1.27706 1.02785.31461 1.6224.28144 2.0729-.0409zm-8.53152-3.54594c-.4847-.50952-1.30889-1.57296-1.83152-2.3632-.68353-.89643-1.02629-1.52887-1.02629-1.52887s-.4996 1.60694-.90948 2.57394l-1.27876 3.16076-.37075.71695s1.971043-.64627 2.97389-.90822c1.0621668-.27744 3.21787-.70134 3.21787-.70134zm-2.74938-11.02573c.12363-1.0375.1761-2.07346-.15724-2.59587-.9246-1.01077-2.04057-.16787-1.85154 2.23517.0636.8084.26443 2.19033.53292 3.04209l.48817 1.54863.34358-1.16638c.18897-.64151.47882-2.02015.64411-3.06364z"/>
                        <path fill="#2c2c2c" d="M-20.930423 167.83862h2.364986q1.133514 0 1.840213.2169.706698.20991 1.189489.9446.482795.72769.482795 1.75625 0 .94459-.391832 1.6233-.391833.67871-1.056548.97958-.65772.30087-2.02913.30087h-.818651v3.72941h-1.581322zm1.581322 1.22447v3.33058h.783664q1.049552 0 1.44838-.39184.405826-.39183.405826-1.27345 0-.65772-.265887-1.06355-.265884-.41282-.587747-.50378-.314866-.098-1.000572-.098zm5.50664-1.22447h2.148082q1.560333 0 2.4909318.55276.9375993.55276 1.4133973 1.6443.482791 1.09153.482791 2.42096 0 1.3994-.4338151 2.49793-.4268149 1.09153-1.3154348 1.76324-.8816233.67172-2.5189212.67172h-2.267031zm1.581326 1.26645v7.018h.657715q1.378411 0 2.001144-.9516.6227329-.95858.6227329-2.5539 0-3.5125-2.6238769-3.5125zm6.4722254-1.26645h5.30372941v1.26645H-4.2075842v2.85478h2.9807225v1.26646h-2.9807225v4.16322h-1.5813254z" font-family="Franklin Gothic Medium Cond" letter-spacing="0" style="line-height:125%;-inkscape-font-specification:'Franklin Gothic Medium Cond'" word-spacing="4.26000023"/>
                    </g>
                </svg>
                <img :src="attach.file_url" class="w-full h-full object-cover" v-else-if="attach.file_type=='PNG' || attach.file_type=='JPG' || attach.file_type=='SVG'">
                <svg width="800px" height="800px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="#000000" style="width: 90px;height: 90px;" v-else>
                    <g id="SVGRepo_bgCarrier" stroke-width="0"/>
                    <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"/>
                    <g id="SVGRepo_iconCarrier">
                    <path d="M3 23h18V6.709L15.29 1H3zM15 2h.2L20 6.8V7h-5zM4 2h10v6h6v14H4z"/>
                    <path fill="none" d="M0 0h24v24H0z"/>
                    </g>
                </svg>
                <div class="absolute top-1 right-1">
                    <Dropdown
                        :options="[
                            {
                                label: 'Download',
                                onClick: () => onDownload(attach),
                                icon: 'download'
                            },{
                                label: 'Delete',
                                onClick: () => onDelete(attach),
                                icon: 'trash',
                                condition: () => !readOnly
                            }
                        ]"
                        >
                        <Button>
                            <template #icon>
                                <FeatherIcon
                                    name="more-vertical"
                                    class="h-4 w-4"
                                />
                            </template>
                        </Button>
                    </Dropdown>
                </div>
                <div class="hidden group-hover:block absolute top-1/2 cursor-pointer" style="left: 45%;" v-if="attach.file_type=='PNG' || attach.file_type=='JPG'" @click="onFileImage(attach)">
                    <div class="w-6 h-6 rounded-full bg-white flex justify-center items-center">
                        <FeatherIcon
                            name="eye"
                            class="h-4 w-4"
                        />
                    </div>
                </div>
            </div>
            <div class="text-base font-medium ml-2 mt-2 w-10/12 truncate">{{attach.file_name}}</div>
            <div class="text-sm text-gray-500 ml-2 mt-1">{{formatTimeAgo(attach.creation)}}</div>
        </div>
    </div>
    <div v-if="previewVisible" class="preview-overlay cursor-pointer" @click="closePreview">
      <img :src="srcImage" alt="Preview" class="preview-image" />
    </div>
    <Dialog
        :options="{
            title: __('Delete all attachment?'),
            message: __('This action can not be undone'),
            size: 'xl',
            actions: [
                {
                    label: __('Delete'),
                    variant: 'solid',
                    theme: 'red',
                    onClick: () => onConfirmDeleteAttachments()
                }
            ],
        }"
        v-model="show_confirm_deleteing"
    />
    <Dialog
        :options="{
            title: __('Delete attachment?'),
            message: __('This action can not be undone'),
            size: 'xl',
            actions: [
                {
                    label: __('Delete'),
                    variant: 'solid',
                    theme: 'red',
                    onClick: () => onConfirmDeleteAttachment()
                }
            ],
        }"
        v-model="show_confirm_delete_attachment"
    />
</template>
<script>
import { Button, Dialog, FeatherIcon, Dropdown } from 'frappe-ui'
import { createToast, timeAgo } from '@/utils'

export default{
    name: 'Attachment',
    props: {
        reference_doctype: {
            type: String
        },
        reference_name: {
            type: String
        },
        readOnly:{
            type: Boolean
        }
    },
    data(){
        return {
            arrAttach: [],
            numAttach: 0,
            show_confirm_deleteing: false,
            show_confirm_delete_attachment: false,
            name_attachment_delete: "",
            csrf_token: "",
            previewVisible: false,
            srcImage: ""
        }
    },
    components: {
        Button,
        Dialog,
        FeatherIcon,
        Dropdown
    },
    resources:{
        doc_info(){
            return {
                url: "gameplan.api.get_attachments",
                method: "POST",
                params: {
                    doctype: this.reference_doctype,
                    name: this.reference_name
                },
                auto: true,
                onSuccess(data){
                    this.arrAttach = data
                    this.numAttach = data.length
                }
            }
        },
        delete_attachment(){
            return {
                url: "frappe.desk.form.utils.remove_attach",
                method: "DELETE",
                auto: false,
                onSuccess(data){
                    this.$resources.doc_info.fetch()
                    this.name_attachment_delete = ""
                    this.show_confirm_delete_attachment = false
                    createToast({
                        title: __('Delete successfully attachment'),
                        icon: 'check',
                        iconClasses: 'text-green-600'
                    })
                }
            }
        },
        delete_attachments(){
            return {
                url: "gameplan.api.delete_attachments",
                method: "POST",
                params: {
                    doctype: this.reference_doctype,
                    name: this.reference_name
                },
                auto: false,
                onSuccess(data){
                    if(data == "ok"){
                        createToast({
                            title: __('Delete successfully attachment'),
                            icon: 'check',
                            iconClasses: 'text-green-600'
                        })
                        this.arrAttach = []
                        this.numAttach = 0
                        this.show_confirm_deleteing = false
                    }else{
                        createToast({
                            title: __('Delete failed attachment'),
                            icon: 'x',
                            iconClasses: 'text-red-600',
                        })
                    }
                }
            }
        },
        get_csrf_token(){
            return {
                url: "gameplan.api.get_token",
                method: "GET",
                auto: true,
                onSuccess(data){
                    this.csrf_token = data
                }
            }
        }
    },
    methods: {
        onFileImage(attach){
            this.previewVisible = true
            this.srcImage = attach.file_url
        },
        onDeleteAll(){
            this.show_confirm_deleteing = true
        },
        onConfirmDeleteAttachments(){
            this.$resources.delete_attachments.fetch()
        },
        onAddAttachment(){
            this.$refs.fileInput.click();
        },
        handleFileChange(evt){
            for(let i = 0; i < evt.target.files.length; i++){
                this.readFileAsBinary(evt.target.files[i]);
            }
        },
        readFileAsBinary(file) {
            const reader = new FileReader()
            reader.onload = (e) => {
                const binaryData = e.target.result
                this.postFile(binaryData, file.name)
            };
            reader.readAsArrayBuffer(file);
        },
        async postFile(binaryData, fileName){
            const formData = new FormData();
            formData.append('file', new Blob([binaryData]), fileName);
            formData.append('is_private', 0)
            formData.append('folder', "Home/Attachments")
            formData.append('doctype', this.reference_doctype)
            formData.append('docname', this.reference_name)
            const response = await fetch('/api/method/upload_file', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Frappe-CSRF-Token': this.csrf_token
                }
            });
            const responseData = await response.json();
            if(responseData.message != null && responseData.message.name != null) this.$resources.doc_info.fetch()
        },
        formatTimeAgo(creationTime){
            return timeAgo(creationTime)
        },
        onDownload(attachment){
            const a = document.createElement('a')
            a.href = attachment.file_url
            a.download = attachment.file_name
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        },
        onDelete(attachment){
            this.name_attachment_delete = attachment.name
            this.show_confirm_delete_attachment = true
        },
        onConfirmDeleteAttachment(){
            this.$resources.delete_attachment.submit({
                'fid': this.name_attachment_delete,
                'dt': this.reference_doctype,
                'dn': this.reference_name
            })
        },
        closePreview(){
            this.previewVisible = false;
            this.srcImage = ""
        }
    }
}
</script>
<style scoped>
.preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.preview-image {
  max-width: 90%;
  max-height: 90%;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
}
</style>