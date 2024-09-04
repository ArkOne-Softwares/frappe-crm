<template>
  <ListView
    :class="$attrs.class"
    :columns="[
      {
        label: 'Name',
        key: 'name',
      },
    ]"
    :rows="rows"
    :options="{
      onRowClick: (row) => {
        console.log(row);
        selected = row.name;
        emit('selectedContact', row.name);
      },
      selectable: false,
      showTooltip: options.showTooltip,
      resizeColumn: options.resizeColumn,
    }"
    row-key="name"
  >
    <ListRows class="mx-3 sm:mx-5" id="list-rows">
      <ListRow
        v-for="row in rows"
        :key="row.name"
        :row="row"
        :class="selected === row.name ? 'bg-gray-100 rounded-md' : ''"
        class="py-4"
      >
        <div class="flex flex-row justify-between items-center">
          <div class="flex flex-row gap-3 justify-start items-center">
            <Avatar
              class="flex items-center"
              :image="row.image"
              :label="row.full_name.label ? row.full_name.label : row.mobile_no"
              size="sm"
            />
            <div v-if="row.full_name.label">{{ row.full_name.label }}</div>
            <div v-else>{{ row.mobile_no }}</div>
          </div>
          <div v-if="row.unread && row.unread > 0">
            <div class="flex flex-row gap-3 justify-end items-center">
              <div
                class="w-4 h-4 rounded-full bg-green-600 flex items-center justify-center text-white text-xs"
              >
                {{ row.unread }}
              </div>
            </div>
          </div>
        </div>
        <div
          v-if="row.last_message && row.last_message !== ''"
          class="text-xs text-gray-500 mt-1 truncate pl-8"
        >
          {{ truncateMessage(row.last_message) }}
        </div>
      </ListRow>
    </ListRows>
  </ListView>
  <ListFooter
    v-if="pageLengthCount"
    class="border-t px-3 py-2 sm:px-5"
    v-model="pageLengthCount"
    :options="{
      rowCount: options.rowCount,
      totalCount: options.totalCount,
    }"
    @loadMore="emit('loadMore')"
  />
  <ListBulkActions
    ref="listBulkActionsRef"
    v-model="list"
    doctype="Contact"
    :options="{
      hideAssign: true,
    }"
  />
</template>
<script setup>
import HeartIcon from "@/components/Icons/HeartIcon.vue";
import PhoneIcon from "@/components/Icons/PhoneIcon.vue";
import ListBulkActions from "@/components/ListBulkActions.vue";
import {
  Avatar,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListRows,
  ListRow,
  ListSelectBanner,
  ListRowItem,
  ListFooter,
  Tooltip,
  Dropdown,
} from "frappe-ui";
import { sessionStore } from "@/stores/session";
import { ref, computed, watch } from "vue";
import { useRoute } from "vue-router";

const props = defineProps({
  rows: {
    type: Array,
    required: true,
  },
  options: {
    type: Object,
    default: () => ({
      selectable: true,
      showTooltip: true,
      resizeColumn: false,
      totalCount: 0,
      rowCount: 0,
    }),
  },
});

const emit = defineEmits([
  "loadMore",
  "updatePageCount",
  "columnWidthUpdated",
  "applyFilter",
  "applyLikeFilter",
  "likeDoc",
  "selectedContact",
]);

const route = useRoute();

const pageLengthCount = defineModel();
const list = defineModel("list");

const isLikeFilterApplied = computed(() => {
  return list.value.params?.filters?._liked_by ? true : false;
});

const { user } = sessionStore();

function isLiked(item) {
  if (item) {
    let likedByMe = JSON.parse(item);
    return likedByMe.includes(user);
  }
}

watch(pageLengthCount, (val, old_value) => {
  if (val === old_value) return;
  emit("updatePageCount", val);
});

const listBulkActionsRef = ref(null);
const selected = ref();

defineExpose({
  customListActions: computed(() => listBulkActionsRef.value?.customListActions),
});

const truncateMessage = (message) => {
  return message.length > 30 ? message.substring(0, 30) + "..." : message;
};
</script>
<style>
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.h-full {
    height: 100%;
  }
</style>
