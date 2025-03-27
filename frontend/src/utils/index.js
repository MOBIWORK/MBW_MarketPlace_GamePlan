import { dayjs } from 'frappe-ui'

export { default as dayjs } from './dayjs'
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

function prettyDate(date, mini) {
  if (!date) return ''

  // Thời gian ban đầu
  const d = dayjs(date)
  // Thời gian hiện tại
  const now = dayjs()

  // Tính khoảng cách thời gian ra giây
  const diff = now.diff(d, 'second')
  let day_diff = Math.floor(diff / 86400)
  if (isNaN(day_diff) || day_diff < 0) return ''

  if (mini) {
    // Return short format of time difference
    if (day_diff == 0) {
      if (diff < 60) {
        return __('now')
      } else if (diff < 3600) {
        return __('{0} m', [Math.floor(diff / 60)])
      } else if (diff < 86400) {
        return __('{0} h', [Math.floor(diff / 3600)])
      }
    } else {
      if (day_diff < 7) {
        return __('{0} d', [day_diff])
      } else if (day_diff < 31) {
        return __('{0} w', [Math.floor(day_diff / 7)])
      } else if (day_diff < 365) {
        return __('{0} M', [Math.floor(day_diff / 30)])
      } else {
        return __('{0} y', [Math.floor(day_diff / 365)])
      }
    }
  } else {
    // Return long format of time difference
    if (day_diff == 0) {
      if (diff < 60) {
        return __('just now')
      } else if (diff < 120) {
        return __('1 minute ago')
      } else if (diff < 3600) {
        return __('{0} minutes ago', [Math.floor(diff / 60)])
      } else if (diff < 7200) {
        return __('1 hour ago')
      } else if (diff < 86400) {
        return __('{0} hours ago', [Math.floor(diff / 3600)])
      }
    } else {
      if (day_diff == 1) {
        return __('yesterday')
      } else if (day_diff < 7) {
        return __('{0} days ago', [day_diff])
      } else if (day_diff < 14) {
        return __('1 week ago')
      } else if (day_diff < 31) {
        return __('{0} weeks ago', [Math.floor(day_diff / 7)])
      } else if (day_diff < 62) {
        return __('1 month ago')
      } else if (day_diff < 365) {
        return __('{0} months ago', [Math.floor(day_diff / 30)])
      } else if (day_diff < 730) {
        return __('1 year ago')
      } else {
        return __('{0} years ago', [Math.floor(day_diff / 365)])
      }
    }
  }
}

export function timeAgo(date) {
  return prettyDate(date)
}