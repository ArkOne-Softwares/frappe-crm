<template>
  <NestedPopover>
    <template #target>
      <Button :label="buttonLabel" :class="buttonClass">
        <template v-if="hideLabel">
          <FileSpreadsheetIcon class="h-4" />
        </template>
        <template v-if="!hideLabel" #prefix>
          <FileSpreadsheetIcon class="h-4" />
        </template>
      </Button>
    </template>
    <template #body="{ close }">
      <div class="my-2 rounded-lg border border-gray-100 bg-white p-1.5 shadow-xl">
        <div>
          <Button class="w-full !justify-start" variant="ghost" @click="filter('new', 'New')" :label="__('New')">
          </Button>
          <Button class="w-full !justify-start" variant="ghost" @click="filter('today', 'Today')" :label="__('Today')">
          </Button>
          <Button class="w-full !justify-start" variant="ghost" @click="filter('todat&beyond', 'Today & Beyond')" :label="__('Today & Beyond')">
          </Button>
          <Button class="w-full !justify-start" variant="ghost" @click="filter('newToday', 'New & Today')" :label="__('New & Today')">
          </Button>
          <Button class="w-full !justify-start" variant="ghost" @click="filter('all', 'All')" :label="__('All')">
          </Button>
          <Button
              v-if="!is_default"
              class="w-full !justify-start !text-gray-600"
              variant="ghost"
              @click="resetToDefault()"
              :label="__('Reset to Default')"
            >
              <template #prefix>
                <ReloadIcon class="h-4" />
              </template>
            </Button>
        </div>
      </div>
    </template>
  </NestedPopover>
</template>

<script setup>
import FileSpreadsheetIcon from '@/components/Icons/FileSpreadsheetIcon.vue'
import NestedPopover from '@/components/NestedPopover.vue'
import { computed, ref } from 'vue'
import { watchOnce } from '@vueuse/core'

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  hideLabel: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update'])
const selectedFilter = ref('')
const selectedFilterLabel = ref('')

const oldValues = ref({
  columns: [],
  rows: [],
  isDefault: false,
})

const list = defineModel()

function filter(val, label) {
  if (!val) return
  selectedFilter.value = val
  selectedFilterLabel.value = label
  if (val == "new") { }
  else if (val == "today") { }
  else if (val == "newToday") { }
  else if (val == "all") { }

  emit('update', val)
}

const resetToDefault = () => {
  selectedFilter.value = '';
  selectedFilterLabel.value = '';
  emit('update', '');
}

const buttonLabel = computed(() => {
  return selectedFilter.value
    ? `Quick Filter : ${selectedFilterLabel.value}`
    : 'Quick Filter';
})

const buttonClass = computed(() => {
  return selectedFilter.value
    ? 'bg-black text-white'
    : '';
})

watchOnce(
  () => list.value.data,
  (val) => {
    if (!val) return
    oldValues.value.columns = JSON.parse(JSON.stringify(val.columns))
    oldValues.value.rows = JSON.parse(JSON.stringify(val.rows))
    oldValues.value.isDefault = val.is_default
  }
)
</script>

<style scoped>
.bg-black {
  background-color: black;
}

.text-white {
  color: white;
}
</style>
