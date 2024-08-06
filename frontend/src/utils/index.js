export { default as dayjs } from './dayjs'
import { toast } from 'frappe-ui'
import { useDateFormat, useTimeAgo } from '@vueuse/core'
import { getUser } from '@/data/users'

export function createToast(options) {
  toast({
    position: 'bottom-right',
    ...options,
  })
}

export function dateFormat(date, format) {
  const _format = format || 'DD-MM-YYYY HH:mm:ss'
  return useDateFormat(date, _format).value
}

export const dateTooltipFormat = 'ddd, MMM D, YYYY h:mm A'

export function timeAgo(date) {
  if(date == null || date == "") return "";
  let valueTimeAgo = useTimeAgo(date).value;
  const regex = /(\d+)?\s*(\w+\s\w+|\w+)/;
  const match = valueTimeAgo.match(regex);
  let number = match[1] || '';
  let word = match[2] || '';
  if (number != null && number != "") return `${number} ${__(word)}`;
  return `${__(word)}`;
}

export function getImgDimensions(imgSrc) {
  return new Promise((resolve) => {
    let img = new Image()
    img.onload = function () {
      let { width, height } = img
      resolve({ width, height, ratio: width / height })
    }
    img.src = imgSrc
  })
}

export function htmlToText(html) {
  let tmp = document.createElement('div')
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ''
}

export function copyToClipboard(text) {
  let textField = document.createElement('textarea')
  textField.value = text
  document.body.appendChild(textField)
  textField.select()
  document.execCommand('copy')
  textField.remove()
  createToast({
    title: __('Sao chép thành công'),
    icon: 'check',
    iconClasses: 'text-green-600',
  })
}

export function getScrollParent(node) {
  if (node == null) {
    return null
  }

  if (node.scrollHeight > node.clientHeight) {
    return node
  } else {
    return getScrollParent(node.parentNode)
  }
}

export function getRandomNumber(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

export function getPlatform() {
  let ua = navigator.userAgent.toLowerCase()
  if (ua.indexOf('win') > -1) {
    return 'win'
  } else if (ua.indexOf('mac') > -1) {
    return 'mac'
  } else if (ua.indexOf('x11') > -1 || ua.indexOf('linux') > -1) {
    return 'linux'
  }
}

export function getRoleByUser(teamInfo=null, projectInfo=null){
  let userSession = getUser('sessionUser')
  if(userSession.role == "Gameplan Admin"){
    return "admin"
  }
  if(userSession.role == "Gameplan Member"){
    if(teamInfo != null){
      let members = teamInfo.members
      for(let i = 0; i < members.length; i++){
        if(members[i].user == userSession.name) return members[i].role
      }
    }
    if(projectInfo != null){
      if(projectInfo.is_private == 0) return "manager"
      return null
    }
    return "member"
  }
  if(userSession.role == "Gameplan Guest"){
    return "guest"
  }
}

export function isTouchScreenDevice() {
	return "ontouchstart" in document.documentElement;
}

