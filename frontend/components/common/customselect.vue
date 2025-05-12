<template>
  <v-select
    v-model="selectedItems"
    :items="items"
    outlined
    multiple
    :item-text="itemText"
    :item-value="itemValue"
    :dense="dense"
    hide-details="auto"
    :label="label"
    :value="value"
    @change="selectionChanged"
    @blur.prevent="onBlur"
    v-on="$listeners"
    :menu-props="{ offsetY: true }"
  >
    <template v-slot:selection="{ item, index }">
      <span v-if="index === 0">
        {{ item[itemText] }}
      </span>
      <span v-if="index === 1" class="text-caption pl-2">
        + {{ selectedItems.length - 1 }} Selected
      </span>
    </template>
    <template v-slot:prepend-item>
      <v-list-item>
        <v-text-field
          class="mb-2 pt-1"
          v-model="searchText"
          placeholder="Search here..."
          :disabled="items.length === 0"
          clearable
          hide-details
          prepend-inner-icon="mdi-magnify"
        ></v-text-field>
      </v-list-item>
      <v-list-item ripple @click="toggleSelectAll">
        <v-list-item-action>
          <v-icon :color="selectedItems > 0 ? 'indigo darken-4' : ''">
            {{ icon }}
          </v-icon>
        </v-list-item-action>
        <v-list-item-content>
          <v-list-item-title> Select All </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-divider class="mt-2"></v-divider>
    </template>
    <template v-slot:item="{ item }">
      <v-list-item ripple @click="selectItem(item)" v-show="search(item)">
        <v-list-item-action>
          <v-checkbox readonly :input-value="isSelected(item)"></v-checkbox>
        </v-list-item-action>
        <v-list-item-content>
          <v-list-item-title>
            {{ item[itemText] }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-select>
</template>

<script>
export default {
  props: {
    itemsList: {
      type: Array,
      required: true,
    },
    itemText: {
      type: String,
      default: "text",
    },
    itemValue: {
      type: String,
      default: "value",
    },
    returnObject: {
      type: Boolean,
      default: false,
    },
    label: {
      type: String,
      default: "Select Items",
    },
    dense: {
      type: Boolean,
      default: false,
    },
    value: {
      required: true,
    },
    isMounted: {
      type: Boolean,
      required: true,
    },
    showButtons: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  watch: {
    selectedItems(value) {
      this.selectionChanged(value);
    },
    isMounted(value) {
      if (value) {
        this.updateValue();
      }
    },
  },
  computed: {
    checkedAll() {
      if (Array.isArray(this.items) && Array.isArray(this.selectedItems)) {
        return this.items.length === this.selectedItems.length;
      } else {
        return false;
      }
    },
    checkedSome() {
      if (Array.isArray(this.items) && Array.isArray(this.selectedItems)) {
        return this.selectedItems.length > 0 && !this.checkedAll;
      } else {
        return false;
      }
    },
    icon() {
      if (this.checkedAll) return "mdi-checkbox-marked";
      if (this.checkedSome) return "mdi-minus-box";
      return "mdi-checkbox-blank-outline";
    },
    items() {
      return this.itemsList;
    },
  },
  data() {
    return {
      selectedItems: [],
      searchText: null,
    };
  },
  methods: {
    onBlur(value) {
      this.$emit("onBlur", this.selectedItems);
    },
    selectionChanged(val) {
      this.$emit("selectionChanged", val);
    },
    search(item) {
      if (this.searchText == null || this.searchText.trim().length == 0) {
        return true;
      } else {
        return item[this.itemText].toLowerCase().indexOf(this.searchText) > -1;
      }
    },
    isSelected(item) {
      let _item = this.selectedItems.find((i) => {
        if (this.returnObject) {
          return i[this.itemValue] == item[this.itemValue];
        } else {
          return i == item[this.itemValue];
        }
      });
      if (_item) {
        return true;
      } else {
        return false;
      }
    },
    toggleSelectAll() {
      if (this.selectedItems.length === this.itemsList.length) {
        this.selectedItems = [];
      } else {
        if (this.returnObject) {
          this.selectedItems = this.itemsList;
        } else {
          this.selectedItems = this.itemsList.map((item) => {
            return item[this.itemValue];
          });
        }
      }
    },
    selectItem(item) {
      if (this.returnObject) {
        let index = this.selectedItems.indexOf(item);
        index > -1
          ? this.selectedItems.splice(index, 1)
          : this.selectedItems.push(item);
      } else {
        let index = this.selectedItems.indexOf(item[this.itemValue]);
        index > -1
          ? this.selectedItems.splice(index, 1)
          : this.selectedItems.push(item[this.itemValue]);
      }
    },
    updateValue() {
      if (this.value) {
        this.selectedItems = this.value;
      } else {
        this.selectedItems = [];
      }
    },
  },
  mounted() {
    this.updateValue();
  },
};
</script>

<style>
</style>