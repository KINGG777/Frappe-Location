<template>
  <div class="flex flex-col gap-4">
    <template v-for="field in fields" :key="field.fieldname">
      <div v-if="field.fieldtype === 'Link'" class="space-y-1.5">
        <Link
          :doctype="field.options"
          :label="field.label"
          :required="!!field.reqd"
          :disabled="isDisabled(field)"
          :placeholder="__('Select {0}', [field.label])"
          :filters="linkFilters?.[field.fieldname]"
          :model-value="local[field.fieldname]"
          @update:model-value="(val: string) => commit(field.fieldname, val)"
        />
      </div>

      <div v-else-if="field.fieldtype === 'Select'" class="space-y-1.5">
        <FormControl
          type="select"
          size="sm"
          :label="field.label"
          :required="!!field.reqd"
          :disabled="isDisabled(field)"
          :options="selectOptions(field)"
          v-model="local[field.fieldname]"
          @change="commit(field.fieldname, local[field.fieldname])"
        />
      </div>

      <div v-else-if="field.fieldtype === 'Check'" class="space-y-1.5">
        <FormControl
          type="checkbox"
          :label="field.label"
          :disabled="isDisabled(field)"
          v-model="local[field.fieldname]"
          @change="commit(field.fieldname, local[field.fieldname] ? 1 : 0)"
        />
      </div>

      <div
        v-else-if="['Int', 'Float', 'Currency'].includes(field.fieldtype)"
        class="space-y-1.5"
      >
        <FormControl
          type="number"
          size="sm"
          :label="field.label"
          :required="!!field.reqd"
          :disabled="isDisabled(field)"
          v-model="local[field.fieldname]"
          @change="commit(field.fieldname, local[field.fieldname])"
        />
      </div>

      <div
        v-else-if="['Small Text', 'Text', 'Long Text'].includes(field.fieldtype)"
        class="space-y-1.5"
      >
        <FormControl
          type="textarea"
          size="sm"
          :label="field.label"
          :required="!!field.reqd"
          :disabled="isDisabled(field)"
          v-model="local[field.fieldname]"
          @change="commit(field.fieldname, local[field.fieldname])"
        />
      </div>

      <div v-else-if="field.fieldtype === 'Date'" class="space-y-1.5">
        <FormControl
          type="date"
          size="sm"
          :label="field.label"
          :required="!!field.reqd"
          :disabled="isDisabled(field)"
          v-model="local[field.fieldname]"
          @change="commit(field.fieldname, local[field.fieldname])"
        />
      </div>

      <!-- Default: Data and anything else text-like -->
      <div v-else class="space-y-1.5">
        <FormControl
          type="text"
          size="sm"
          :label="field.label"
          :required="!!field.reqd"
          :disabled="isDisabled(field)"
          v-model="local[field.fieldname]"
          @change="commit(field.fieldname, local[field.fieldname])"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { getMeta } from "@/stores/meta";
import { __ } from "@/translation";
import { FormControl } from "frappe-ui";
import { computed, reactive, watch } from "vue";
import Link from "./frappe-ui/Link.vue";

/**
 * Renders a form for any doctype driven entirely by its live metadata —
 * add/remove/reorder fields in the DocType builder and this form picks
 * them up automatically, no code changes needed.
 *
 * Emits `commit(fieldname, value)` whenever a field's value settles
 * (on change/blur for text-like fields, immediately for Link/Select/Check).
 * The parent decides what to do with each commit — accumulate into a
 * payload for a Create flow, or auto-save immediately for an Edit flow.
 */

const props = defineProps<{
  doctype: string;
  /** Current field values, e.g. an existing doc, or {} for a new record */
  modelValue: Record<string, any>;
  /** Fieldnames to always skip (e.g. ones rendered elsewhere in a custom layout) */
  exclude?: string[];
  /**
   * Per-fieldname Link filters, e.g. { location: { company: 'Acme' } }
   * to filter the Location link's options down to a chosen customer.
   */
  linkFilters?: Record<string, Record<string, any>>;
}>();

const emit = defineEmits<{
  (e: "commit", fieldname: string, value: any): void;
}>();

const EXCLUDED_FIELDTYPES = new Set([
  "Section Break",
  "Column Break",
  "Tab Break",
  "HTML",
  "Button",
  "Table",
  "Table MultiSelect",
  "Attach",
  "Attach Image",
  "Read Only",
  "Heading",
  "Geolocation",
]);

const { getFields } = getMeta(props.doctype);

const fields = computed(() =>
  getFields().filter(
    (f: any) =>
      !EXCLUDED_FIELDTYPES.has(f.fieldtype) &&
      !f.hidden &&
      !f.read_only &&
      !(props.exclude || []).includes(f.fieldname)
  )
);

// Local editable copy, seeded from the incoming doc/payload and
// resynced whenever the parent swaps in a different object (e.g. a
// freshly-loaded doc, or a dialog reset).
const local = reactive<Record<string, any>>({ ...props.modelValue });
watch(
  () => props.modelValue,
  (val) => {
    Object.keys(local).forEach((k) => delete local[k]);
    Object.assign(local, val || {});
  }
);

function isDisabled(field: any) {
  // A field stays disabled until every earlier *mandatory* field has a
  // value — enforces filling the form top-to-bottom, e.g. Customer
  // before Location, purely from field order + the Mandatory flag.
  const idx = fields.value.findIndex((f: any) => f.fieldname === field.fieldname);
  for (let i = 0; i < idx; i++) {
    const earlier = fields.value[i];
    if (earlier.reqd && !local[earlier.fieldname]) {
      return true;
    }
  }
  return false;
}

function selectOptions(field: any) {
  return (field.options || "")
    .split("\n")
    .map((o: string) => o.trim())
    .filter(Boolean)
    .map((o: string) => ({ label: o, value: o }));
}

function commit(fieldname: string, value: any) {
  local[fieldname] = value;
  emit("commit", fieldname, value);
}
</script>
