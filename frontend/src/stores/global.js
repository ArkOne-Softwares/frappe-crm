import { defineStore } from 'pinia'
import { getCurrentInstance, ref } from 'vue'

export const globalStore = defineStore('crm-global', () => {
  const app = getCurrentInstance()
  const { $dialog, $socket } = app.appContext.config.globalProperties

  let twilioEnabled = ref(false)
  let callMethod = () => {}

  // Define filters object
  let filters = ref({
    allFilters: [],
    allOrFilters: [],
    allSortOrder: ''
  })

  function setTwilioEnabled(value) {
    twilioEnabled.value = value
  }

  function setMakeCall(value) {
    callMethod = value
  }

  function makeCall(number) {
    callMethod(number)
  }

  // Functions to update filters
  function updateAllFilters(data) {
    console.log("Updating allFilters", data)
    filters.value.allFilters = data
  }

  function updateAllOrFilters(data) {
    console.log("Updating allOrFilters", data)
    filters.value.allOrFilters = data
  }

  function updateAllSortOrder(data) {
    console.log("Updating allSortOrder", data)
    filters.value.allSortOrder = data
  }

  // Function to return filters
  function getFilters() {
    return filters.value
  }

  return {
    $dialog,
    $socket,
    twilioEnabled,
    makeCall,
    setTwilioEnabled,
    setMakeCall,
    filters,
    updateAllFilters,
    updateAllOrFilters,
    updateAllSortOrder,
    getFilters
  }
})