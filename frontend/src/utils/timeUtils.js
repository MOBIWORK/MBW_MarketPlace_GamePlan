import dayjs from 'dayjs'
import 'dayjs/locale/vi'
import 'dayjs/locale/en'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

// Hàm chuyển đổi hiển thị thời gian theo ngôn ngữ
export function formatTimeAgo(time, locale = 'vi') {
  dayjs.locale(locale)
  return dayjs(time).fromNow()
}

// Hàm đổi định dạng thời gian cụ thể
export function formatDate(time, locale = 'vi') {
  dayjs.locale(locale) // Đặt ngôn ngữ
  return dayjs(time).format('dddd, D MMMM YYYY HH:mm')
}
