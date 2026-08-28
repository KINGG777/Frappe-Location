<template>
  <Dialog
    v-model:open="open"
    :title="__('Create Location')"
    size="md"
    @after-leave="reset"
  >
    <template #default>
      <DynamicDoctypeForm
        doctype="Location"
        :model-value="formValues"
        @commit="handleCommit"
      />
    </template>

    <template #actions>
      <div class="flex justify-end gap-2">
        <Button
          :label="__('Create')"
          theme="gray"
          variant="solid"
          :loading="locationResource.loading"
          @click="addLocation"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import DynamicDoctypeForm from "@/components/DynamicDoctypeForm.vue";
import { getMeta } from "@/stores/meta";
import { __ } from "@/translation";
import { getErrorMessage } from "@/utils";
import { createResource, toast } from "frappe-ui";
import { reactive } from "vue";
import { useRouter } from "vue-router";

const open = defineModel<boolean>({ default: false });
const router = useRouter();

const formValues = reactive<Record<string, any>>({});
const { getFields } = getMeta("Location");

function handleCommit(fieldname: string, value: any) {
  formValues[fieldname] = value;
}

const locationResource = createResource({
  url: "frappe.client.insert",
  onSuccess: (doc: { name: string }) => {
    toast.success(__("Location created"));
    open.value = false;
    router.push({ name: "Location", params: { id: doc.name } });
  },
  onError: (error: unknown) => {
    getErrorMessage(error, true);
  },
});

function addLocation() {
  // Generically validate every mandatory field from the doctype's own
  // metadata, so this stays correct even as fields are added/removed.
  const missing = getFields().find(
    (f: any) => f.reqd && !f.hidden && !f.read_only && !formValues[f.fieldname]
  );
  if (missing) {
    toast.error(__("{0} is required", [missing.label]));
    return;
  }

  locationResource.submit({
    doc: {
      doctype: "Location",
      ...formValues,
    },
  });
}

function reset() {
  Object.keys(formValues).forEach((k) => delete formValues[k]);
}
</script>
