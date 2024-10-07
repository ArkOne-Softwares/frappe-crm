<template>
  <Dialog v-model="show" :options="{ size: '3xl' }">
    <template #body>
      <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-gray-900">
              {{ __("Create Lead") }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button
              v-if="isManager()"
              variant="ghost"
              class="w-7"
              @click="openQuickEntryModal"
            >
              <EditIcon class="h-4 w-4" />
            </Button>
            <Button variant="ghost" class="w-7" @click="show = false">
              <FeatherIcon name="x" class="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div>
          <Fields v-if="sections.data" :sections="sections.data" :data="lead" />
          <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isLeadCreating"
            @click="createNewLead"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import EditIcon from "@/components/Icons/EditIcon.vue";
import Fields from "@/components/Fields.vue";
import { usersStore } from "@/stores/users";
import { statusesStore } from "@/stores/statuses";
import { capture } from "@/telemetry";
import { createResource } from "frappe-ui";
import { computed, onMounted, ref, nextTick } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
  defaults: Object,
});

const { getUser, isManager } = usersStore();
const { getLeadStatus, statusOptions } = statusesStore();

const show = defineModel();
const router = useRouter();
const error = ref(null);
const isLeadCreating = ref(false);
const showQuickEntryModal = defineModel("quickEntry");

const lead = ref({
  status: "",
});

const sections = createResource({
  url: "crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout",
  cache: ["quickEntryFields", "CRM Lead"],
  params: { doctype: "CRM Lead", type: "Quick Entry" },
  auto: true,
  transform: (data) => {
    return data.forEach((section) => {
      section.fields.forEach((field) => {
        if (field.name == "status") {
          field.type = "Select";
          field.options = leadStatuses.value;
          field.prefix = getLeadStatus(lead.value.status).iconColorClass;
        } else if (field.name == "lead_owner") {
          field.type = "User";
        }
        console.log(field);
        if (!lead.value.hasOwnProperty(field.name)) {
          lead.value[field.name] = field.placeholder || "";
        }
      });
    });
  },
});

const createLead = createResource({
  url: "frappe.client.insert",
  makeParams(values) {
    return {
      doc: {
        doctype: "CRM Lead",
        ...values,
      },
    };
  },
});

const leadStatuses = computed(() => {
  let statuses = statusOptions("lead");
  if (!lead.value.status) {
    lead.value.status = statuses[0].value;
  }
  return statuses;
});

function createNewLead() {
  if (lead.value.website && !lead.value.website.startsWith("http")) {
    lead.value.website = "https://" + lead.value.website;
  }

  createLead.submit(lead.value, {
    validate() {
      error.value = null;
      if (!lead.value.lead_name) {
        lead.value.lead_name = "EMPTY";
        return "Your have not provided a name for the lead. We have set it to 'EMPTY'. Click on 'Create' again to proceed.";
      }
      if (lead.value.mobile_no && isNaN(lead.value.mobile_no.replace(/[-+() ]/g, ""))) {
        error.value = __("Mobile No should be a number");
        return error.value;
      }
      if (lead.value.email && !lead.value.email.includes("@")) {
        error.value = __("Invalid Email");
        return error.value;
      }
      if (!lead.value.status) {
        error.value = __("Status is required");
        return error.value;
      }
      isLeadCreating.value = true;
    },
    onSuccess(data) {
      capture("lead_created");
      isLeadCreating.value = false;
      show.value = false;
      router.push({ name: "Lead", params: { leadId: data.name } });
    },
    onError(err) {
      isLeadCreating.value = false;
      if (!err.messages) {
        error.value = err.message;
        return;
      }
      error.value = err.messages.join("\n");
    },
  });
}

function openQuickEntryModal() {
  showQuickEntryModal.value = true;
  nextTick(() => {
    show.value = false;
  });
}

onMounted(() => {
  Object.assign(lead.value, props.defaults);
  if (!lead.value.lead_owner) {
    lead.value.lead_owner = getUser().name;
  }
  if (!lead.value.status && leadStatuses.value[0].value) {
    lead.value.status = leadStatuses.value[0].value;
  }
});
</script>
