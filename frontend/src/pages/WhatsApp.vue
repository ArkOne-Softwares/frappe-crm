<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="WhatsApp" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="whatsappListView?.customListActions"
        :actions="whatsappListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        @click="
          () => {
            showContactModal = true;
            quickEntryContact = true;
          }
        "
      >
        <template #prefix>
          <FeatherIcon name="plus" class="h-4" />
        </template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="contacts_sorted_whatsapp"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Contact"
    :filters="{
      mobile_no: ['is', 'set'],
    }"
    url="crm.api.doc.get_whatsapp_contact_data"
    order_by="last_msg_whatsapp desc,first_name asc"
    :options="{
      hideColumnsButton: true,
      hideQuickFilter: true,
    }"
  />
  <div class="flex flex-row justify-around items-stretch h-full border-t">
    <div
      class="flex flex-col w-full max-w-[400px] h-full flex-1 items-stretch border-r bg-gray-50"
    >
      <h1 class="font-medium pl-8 mb-6 py-2 border-b-[1px] border-gray-300 text-gray-500">
        Your Contacts
      </h1>
      <WhatsappListView
        ref="whatsappListView"
        v-if="contacts_sorted_whatsapp.data && rows.length"
        v-model="contacts_sorted_whatsapp.data.page_length_count"
        v-model:list="contacts_sorted_whatsapp"
        :rows="rows"
        :options="{
          showTooltip: false,
          resizeColumn: false,
          rowCount: contacts_sorted_whatsapp.data.row_count,
          totalCount: contacts_sorted_whatsapp.data.total_count,
        }"
        @loadMore="() => loadMore++"
        @updatePageCount="(count) => (updatedPageCount = count)"
        @selectedContact="handleContactChange"
      />
      <div
        v-else-if="contacts_sorted_whatsapp.data"
        class="flex h-full items-center justify-center"
      >
        <div class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500">
          <ContactsIcon class="h-10 w-10" />
          <span>{{ __("No {0} Found", [__("Contacts")]) }}</span>
          <Button
            :label="__('Create')"
            @click="
              () => {
                showContactModal = true;
                quickEntryContact = null;
              }
            "
          >
            <template #prefix>
              <FeatherIcon name="plus" class="h-4" />
            </template>
          </Button>
        </div>
      </div>
    </div>
    <div class="flex w-full h-full flex-1 items-stretch">
      <Tabs
        v-if="selectedContact && contact.data"
        class="overflow-hidden"
        v-model="tabIndex"
        :tabs="tabs"
      >
        <template #tab="{ tab, selected }">
          <button
            class="group flex items-center gap-2 border-b border-transparent py-2.5 text-base text-gray-600 duration-300 ease-in-out hover:border-gray-400 hover:text-gray-900"
            :class="{ 'text-gray-900': selected }"
            @click="handleTabClick(tab.label)"
          >
            <component v-if="tab.icon" :is="tab.icon" class="h-5" />
            {{ __(tab.label) }}
          </button>
        </template>
        <template #default="{ tab }">
          <Activities
            v-if="tab.label === 'WhatsApp'"
            ref="activities"
            doctype="Contact"
            :title="tab.label"
            :header="contact.data.full_name"
            :tabs="tabs"
            v-model:tabIndex="tabIndex"
            v-model="contact"
            :key="contact.data.name"
            :unreadCount="contact.data.unread"
          />
          <Activities
            v-if="tab.label === 'Emails'"
            ref="activities"
            doctype="Contact"
            :title="tab.label"
            :tabs="tabs"
            v-model:tabIndex="tabIndex"
            v-model="contact"
            :key="contact.data.name"
          />
        </template>
      </Tabs>
      <div
        v-else
        class="flex flex-col items-center justify-center h-full w-full text-xl font-medium text-gray-500"
      >
        <ContactsIcon class="h-10 w-10" />
        <span>{{ __("Select a contact to view details") }}</span>
      </div>
    </div>
  </div>
  <ContactModal
    v-model="showContactModal"
    v-model:quickEntry="showQuickEntryModal"
    :contact="!quickEntryContact ? contact : {}"
    :options="{ detailMode, redirect: false, afterInsert: reloadContact }"
  />
  <QuickEntryModal
    v-if="showQuickEntryModal"
    v-model="showQuickEntryModal"
    doctype="Contact"
  />
</template>

<script setup>
import { ref, computed, h, watch, onMounted, onBeforeUnmount } from "vue";
import ViewBreadcrumbs from "@/components/ViewBreadcrumbs.vue";
import CustomActions from "@/components/CustomActions.vue";
import EditIcon from "@/components/Icons/EditIcon.vue";
import ContactsIcon from "@/components/Icons/ContactsIcon.vue";
import LayoutHeader from "@/components/LayoutHeader.vue";
import ContactModal from "@/components/Modals/ContactModal.vue";
import QuickEntryModal from "@/components/Settings/QuickEntryModal.vue";
import WhatsappListView from "@/components/ListViews/WhatsappListView.vue";
import ViewControls from "@/components/ViewControls.vue";
import Activities from "@/components/Activities/Activities.vue";
import { organizationsStore } from "@/stores/organizations.js";
import { dateFormat, dateTooltipFormat, timeAgo } from "@/utils";
import {
  Breadcrumbs,
  Avatar,
  FileUploader,
  Tooltip,
  Tabs,
  call,
  createResource,
  usePageMeta,
} from "frappe-ui";

import Email2Icon from "@/components/Icons/Email2Icon.vue";
import DealsIcon from "@/components/Icons/DealsIcon.vue";
import WhatsAppIcon from "@/components/Icons/WhatsAppIcon.vue";
import { globalStore } from "@/stores/global";

const { $socket } = globalStore();

const { getOrganization } = organizationsStore();

const showContactModal = ref(false);
const showQuickEntryModal = ref(false);
const detailMode = ref(false);
const previousTabIndex = ref(0);
const whatsappListView = ref(null);
const quickEntryContact = ref(false);

// contacts_sorted_whatsapp data is loaded in the ViewControls component
const contacts_sorted_whatsapp = ref({});
const loadMore = ref(1);
const triggerResize = ref(1);
const updatedPageCount = ref(20);
const viewControls = ref(null);

onMounted(() => {
  if (!localStorage.getItem("notificationUrl")) {
    localStorage.setItem("notificationUrl", window.location.href);
  }
});

const savedUrl = localStorage.getItem("notificationUrl");
const channel = new BroadcastChannel('notification_channel');

const rows = computed(() => {
  if (
    !contacts_sorted_whatsapp.value?.data?.data ||
    !["list", "group_by"].includes(contacts_sorted_whatsapp.value.data.view_type)
  )
    return [];
  return contacts_sorted_whatsapp.value?.data.data.map((contact) => {
    let _rows = {};
    contacts_sorted_whatsapp.value?.data.rows.forEach((row) => {
      _rows[row] = contact[row];
      if (row == "full_name") {
        _rows[row] = {
          label: contact.full_name,
          image_label: contact.full_name,
          image: contact.image,
        };
      } else if (row == "company_name") {
        _rows[row] = {
          label: contact.company_name,
          logo: getOrganization(contact.company_name)?.organization_logo,
        };
      } else if (["modified", "creation"].includes(row)) {
        _rows[row] = {
          label: dateFormat(contact[row], dateTooltipFormat),
          timeAgo: __(timeAgo(contact[row])),
        };
      }
      _rows["last_message"] = contact.last_message ? contact.last_message : "";
      _rows["unread"] = contact.unread ? contact.unread : 0;
    });
    return _rows;
  });
});

const selectedContact = ref();
const contact = createResource({
  url: "crm.api.contact.get_contact",
  cache: ["contact", selectedContact.value],
  params: {
    name: selectedContact.value,
  },
  auto: true,
  transform: (data) => {
    return {
      ...data,
      actual_mobile_no: data.mobile_no,
      mobile_no: data.mobile_no,
    };
  },
});

watch(selectedContact, (newContact) => {
  if (newContact && selectedContact.value) {
    if (!contact.params) {
      contact.params = {};
    }
    contact.params.name = newContact;
    contact.fetch();
  }
});

onBeforeUnmount(() => {
  $socket.off("whatsapp_message");
});

onMounted(() => {
  $socket.on("whatsapp_message", (data) => {
    if (data.reference_name !== selectedContact.value) {
      reloadViewControls();
      if (Notification.permission === "granted") {
        const notification = new Notification(
          "Whatsapp Message received from contact " +
            data.reference_name +
            " : " +
            data.message
        );
        notification.onclick = () => {
          channel.postMessage('focus');
        };
      } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then((permission) => {
          if (permission === "granted") {
            const notification = new Notification(
              "Whatsapp Message received from contact " +
                data.reference_name +
                " : " +
                data.message
            );
            notification.onclick = () => {
              channel.postMessage('focus');
            };
          }
        });
      }
    }
  });

  channel.onmessage = (event) => {
    if (event.data === 'focus') {
      if (document.visibilityState === 'visible') {
        window.focus();
      } else {
        window.open(savedUrl, '_blank');
      }
    }
  };

  $socket.on("updated_mark_as_read", () => {
    reloadViewControls();
  });
});

const handleContactChange = (event) => {
  if (event && selectedContact.value !== event) {
    selectedContact.value = event;
  }
};

const reloadViewControls = () => {
  if (viewControls.value) {
    reloadContact();
  }
};

const reloadContact = () => {
  contacts_sorted_whatsapp.value.reload();
};

const tabIndex = ref(0);
const tabs = [
  {
    label: "WhatsApp",
    icon: h(WhatsAppIcon, { class: "h-4 w-4" }),
  },
  {
    label: "Emails",
    icon: h(Email2Icon, { class: "h-4 w-4" }),
  },
  {
    label: "Profile",
    icon: h(EditIcon, { class: "h-4 w-4" }),
  },
];

const handleTabClick = (label) => {
  if (label === "Profile") {
    previousTabIndex.value = tabIndex.value;
    detailMode.value = true;
    showContactModal.value = true;
    quickEntryContact.value = false;
  } else {
    tabIndex.value = tabs.findIndex((tab) => tab.label === label);
  }
};

watch(showContactModal, (newValue) => {
  console.log("showContactModal", newValue);
  if (!newValue) {
    tabIndex.value = previousTabIndex.value;
  }
});
</script>
