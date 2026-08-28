<template>
  <div class="flex flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="text-lg-medium text-ink-gray-9">
          {{ __("Locations") }}
        </div>
      </template>
      <template #right-header>
        <Button
          :label="__('Create')"
          theme="gray"
          variant="solid"
          @click="showNewLocationModal = true"
        >
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>
    <ListViewBuilder ref="listViewRef" :options="options" />
    <NewLocationDialog v-model="showNewLocationModal" />
  </div>
</template>
<script setup lang="ts">
import { LayoutHeader, ListViewBuilder } from "@/components";
import NewLocationDialog from "@/components/location/NewLocationDialog.vue";
import { __ } from "@/translation";
import { usePageMeta } from "frappe-ui";
import { computed, h, ref } from "vue";
import LucideMapPin from "~icons/lucide/map-pin";

const showNewLocationModal = ref(false);
const listViewRef = ref(null);

const hasActiveFilters = computed(
  () => Object.keys(listViewRef.value?.list?.params?.filters || {}).length > 0
);

const options = computed(() => ({
  doctype: "Location",
  selectable: true,
  showSelectBanner: true,
  emptyState: {
    title: "No locations found",
    icon: h(LucideMapPin, { class: "h-10 w-10" }),
    description: hasActiveFilters.value
      ? __(
          "No locations found for the applied filters. Try adjusting or clearing your filters."
        )
      : undefined,
  },
  rowRoute: {
    name: "Location",
    prop: "id",
  },
}));

usePageMeta(() => ({ title: "Locations" }));
</script>
