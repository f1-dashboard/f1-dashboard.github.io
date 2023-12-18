<template>
  <h2>Selected driver(s)</h2>

  <div class="card-content-box">
    <div class="card" id="first">
      <img :src="picture_url" style="width:100%">
      <h1 style="font-size: 10px">{{ this.drivers[0] }}</h1>
      <p class="title">{{ this.team }}</p>
    </div>

    <div class="parent-secondary-card">
      <div v-if="this.drivers[1]" class="card">
      <img :src="picture_url" style="width:100%">
      <h1 style="font-size: 10px">{{ this.drivers[1] }}</h1>
      <p class="title">{{ this.team }}</p>
      <button class="close-button" @click="$emit('emitDrivers', [this.drivers[0], undefined])">X</button>
    </div>
    <div v-else class="add-wrapper">
      <div class="add-driver" @click="open = !open">
        <span class="plus-symbol">+</span>
      </div>
    </div>
    <div class="items" :class="{ selectHide: !open }">
      <div
        v-for="(drvr, i) of availableDrivers"
        :key="i"
        @click="
          selected = drvr;
          open = false;
          $emit('emitDrivers', [this.drivers[0], drvr]);
        "
      >
        {{ drvr }}
      </div>
    </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['drivers'],
  data() {
    return {
      selected: undefined,
      open: false,
      picture_url: "../../data/Placeholder.jpg",
      team: "Driver team",
      availableDrivers: ["Carlos Sainz", "George Russell"]
    }
  },
  methods: {
    addDriver() {
    }
  },
  watch: {
    drivers: function (newVal, oldVal) {
      this.picture_url = "../../data/Placeholder.jpg"
      this.team = "Other team"
    }
  },
}
</script>


<style scope>
.selectHide {
  display: none;
}

.card-content-box {
  margin-bottom: 25px;
  margin-top: 25px;
}

.card {
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  width: 120px;
  height: 220px;
  margin: auto;
  text-align: center;
  display:inline-block;
  overflow: hidden;
}

.parent-secondary-card {
  display: inline-block;
  vertical-align: top;
}

.title {
  color: grey;
  font-size: 10px;
}

#first {
  margin-right: 50px;
}

.add-driver {
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  width: 120px;
  height: 220px;
  margin: auto;
  text-align: center;
  cursor: pointer;
  display: flex;
  align-items: center; 
  justify-content: center; 
}

.plus-symbol {
  display: flex;
  font-size: 64px;
  user-select: none;
  color: rgba(219, 217, 217, 0.7); 
}

.items {
  width: 120PX;
  color: #fff;
  border-radius: 0px 0px 6px 6px;
  overflow: hidden;
  border-right: 1px solid #ad8225;
  border-left: 1px solid #ad8225;
  border-bottom: 1px solid #ad8225;
  background-color: #d0d0d0;
  left: 0;
  right: 0;
  z-index: 1;
}

</style>