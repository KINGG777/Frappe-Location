<template>
  <div class="flex h-full flex-col overflow-y-hidden max-w-screen-md mx-auto w-full">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" class="-ml-[2px]" />
      </template>
      <template #right-header>
        <Button
          :label="__('Delete')"
          theme="red"
          variant="subtle"
          @click="handleDelete"
        />
      </template>
    </LayoutHeader>

    <div v-if="location.doc" class="overflow-y-auto p-5">
      <DynamicDoctypeForm
        doctype="Location"
        :model-value="location.doc"
        @commit="handleCommit"
      />
    </div>
    <div v-else-if="location.loading" class="flex flex-1 items-center justify-center">
      <LoadingIndicator class="size-6 text-ink-gray-5" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { LayoutHeader } from "@/components";
import DynamicDoctypeForm from "@/components/DynamicDoctypeForm.vue";
import { __ } from "@/translation";
import { getErrorMessage } from "@/utils";
import {
  Breadcrumbs,
  Button,
  LoadingIndicator,
  createDocumentResource,
  toast,
} from "frappe-ui";
import { computed } from "vue";
import { useRouter } from "vue-router";

const props = defineProps<{ id: string }>();
const router = useRouter();

const location = createDocumentResource({
  doctype: "Location",
  name: props.id,
  setValue: {
    onSuccess: () => toast.success(__("Saved")),
    onError: (error: unknown) => getErrorMessage(error, true),
  },
});

function handleCommit(fieldname: string, value: any) {
  location.setValue.submit({ [fieldname]: value });
}

function handleDelete() {
  location.delete.submit(null, {
    onSuccess: () => {
      toast.success(__("Location deleted"));
      router.push({ name: "LocationList" });
    },
    onError: (error: unknown) => getErrorMessage(error, true),
  });
}

const breadcrumbs = computed(() => [
  { label: __("Locations"), route: { name: "LocationList" } },
  { label: location.doc?.location_name || props.id },
]);
</script>
