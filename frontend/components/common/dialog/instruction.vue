<template>
  <v-dialog v-model="openDialog.dialog" persistent max-width="500px">
    <v-card class="pa-4">
      <v-card-title>
        <span
          class="
            text-lg-subtitle-1 text-xl-h6 text-uppercase
            font-weight-black
            primary--text
          "
        >
          Instruction
        </span>
        <v-spacer></v-spacer>
        <v-btn depressed fab class="mt-n3" small @click="closeDialog">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pt-3">
        <div v-if="openDialog.RequestType == 'Orders Update'">
          <h4 class="text-lg-Subtitle-1">Note</h4>
          <h4 class="text-lg-caption mb-4">
            The header given in your excel must be same as below Mandatory
            Fields. For reference download sample excel file.
          </h4>
          <h4 class="text-lg-Subtitle-1">Mandatory Fields are :</h4>
          <h4 class="text-lg-caption">
            SO Number,<br />
            Delivery Date,<br />
          </h4>
        </div>
        <div v-if="openDialog.RequestType == 'Orders'">
          <h4 class="text-lg-Subtitle-1">Note</h4>
          <h4 class="text-lg-caption mb-4">
            The header given in your excel must be same as below Mandatory
            Fields. For reference download sample excel file.
          </h4>
          <h4 class="text-lg-Subtitle-1">Mandatory Fields are :</h4>
          <h4 class="text-lg-caption">
            Item No,<br />
            SO Number,<br />
            Customer Code, <br />
            Delivery Date, <br />
            Quantity <br />
          </h4>
        </div>
        <div v-if="openDialog.RequestType == 'B2C Orders'">
          <h4 class="text-lg-Subtitle-1">Note</h4>
          <h4 class="text-lg-caption mb-4">
            The header given in your excel must be same as below Mandatory
            Fields. For reference download sample excel file.
          </h4>
          <h4 class="text-lg-Subtitle-1">Mandatory Fields are :</h4>
          <h4 class="text-lg-caption">
            Item No,<br />
            SO Number,<br />
            Delivery Date, <br />
            Quantity <br />
            Customer Number, <br />
            Customer Name, <br />
            Customer Type, <br />
            Project Id, <br />
            Addresss, <br />
            Latitude, <br />
            Longitude, <br />
            From Time, <br />
            To Time, <br />


          </h4>
        </div>
        <div v-else-if="openDialog.RequestType == 'Customer Addresses'">
          <h4 class="text-lg-Subtitle-1">Note</h4>
          <h4 class="text-lg-caption mb-4">
            The header given in your excel must be same as below Mandatory
            Fields. For reference download sample excel file.
          </h4>
          <h4 class="text-lg-Subtitle-1">Mandatory Fields are :</h4>
          <h4 class="text-lg-caption">
            Customer Code <br />
            Customer Name<br />
            Customer Type<br />
            Contact Email<br />
            Project Id<br />
            Address<br />
          </h4>
        </div>
        <div v-else-if="openDialog.RequestType == 'Items'">
          <h4 class="text-lg-Subtitle-1">Note</h4>
          <h4 class="text-lg-caption mb-4">
            The header given in your excel must be same as below Mandatory
            Fields. For reference download sample excel file.
          </h4>
          <h4 class="text-lg-Subtitle-1">Mandatory Fields are :</h4>
          <h4 class="text-lg-caption">
            Item name<br />
            item No<br />
            Storage Type<br />
            Unit<br />
            Length<br />
            Width<br />
            Height<br />
            Volume (CBM)<br />
            Weight<br />
          </h4>
        </div>
        <div v-else-if="openDialog.RequestType == 'Drivers'">
          <h4 class="text-lg-Subtitle-1">Note</h4>
          <h4 class="text-lg-caption mb-4">
            The header given in your excel must be same as below Mandatory
            Fields. For reference download sample excel file.
          </h4>
          <h4 class="text-lg-Subtitle-1">Mandatory Fields are :</h4>
          <h4 class="text-lg-caption">
            First Name<br />
            Last Name<br />
            User Name<br />
            Password<br />
            Contact Number<br />
            Project id<br />
            Shift Start<br />
            Shift End<br />
            <!-- Status<br /> -->
            License Number<br />
            License Expiry<br />
            National Id Expiry<br />
            <!-- Service Type<br /> -->
            <!-- Nationality<br /> -->
             Vehicle Assigned<br />
          </h4>
        </div>
        <div v-else-if="openDialog.RequestType == 'Vehicles'">
          <h4 class="text-lg-Subtitle-1">Note</h4>
          <h4 class="text-lg-caption mb-4">
            The header given in your excel must be same as below Mandatory
            Fields. For reference download sample excel file.
          </h4>
          <h4 class="text-lg-Subtitle-1">Mandatory Fields are :</h4>
          <h4 class="text-lg-caption">
            Licence Plate No<br />
            Project Id<br />
            Fuel Type<br />
            Tonnage Capacity<br />
            CBM Capacity<br />
            Permits<br />
            Insurance Policy Number<br />
            Fuel Type<br />
            RC Number<br />
            RC Expiry Date<br />
            Vehicle Make<br />
            Vehicle Model<br />
            Vehicle Year<br />
            Vehicle Cost<br />
            Odometer reading<br />
            <!-- Status<br /> -->
            Storages<br />
            Sensor id<br />
            Tags<br />

          </h4>
        </div>
        <div v-else-if="openDialog.RequestType == 'temperaturesheet'">
          <h4 class="text-lg-Subtitle-1">Note</h4>
          <h4 class="text-lg-caption mb-4">
            Only supports Excel files <br />
            Files with the same names are not allowed<br />
            You can select multiple files from the directory(Folder)<br />
          </h4>
        </div>
      </v-card-text>
      <v-card-actions class="d-flex justify-end">
        <!-- <v-btn color="primary" @click="closeDialog"> Close </v-btn> -->
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script>
export default {
  props: {
    openDialog: Object,
  },
  methods: {
    closeDialog() {
      this.$emit("closeDialogBox", false);
    },
  },
};
</script>
