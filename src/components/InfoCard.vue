<template>
  <h2>Selected driver(s)</h2>

  <div class="card-content-box">
    <div class="card" id="first">
      <img :src="this.firstUrl" style="width:100%">
      <h1 style="font-size: 10px">{{ this.drivers[0] }}</h1>
      <p class="title">{{ this.firstTeam }}</p>
    </div>

    <div class="parent-secondary-card">
      <div v-if="this.drivers[1]" class="card">
      <img :src="this.secondUrl" style="width:100%">
      <h1 style="font-size: 10px">{{ this.drivers[1] }}</h1>
      <p class="title">{{ this.secondTeam }}</p>
      <button class="close-button" @click="$emit('emitDrivers', [this.drivers[0]])">X</button>
    </div>

    <div v-else class="add-wrapper" ref="exceptionElement">
      <div class="add-driver" @click="console.log(open); open = !open">
        <span class="plus-symbol">+</span>
      </div>
    </div>

    <div class="items" :class="{ selectHide: !open }" ref="targetElement">
      <div
        v-for="(drvr, i) of availableDrivers"
        :key="i"
        @click="
          open = false;
          $emit('emitDrivers', [this.drivers[0], drvr.driverName]);
        "
      >
        {{ drvr.driverName }}
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  props: ['drivers'],
  data() {
    return {
      open: false,
      availableDrivers: [],
      firstTeam: "",
      secondTeam: "",
      firstUrl: "",
      secondUrl: ""
    }
  },
  async mounted() {
    document.addEventListener('click', this.handleClickOutside);
    await this.loadDrivers();
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    handleClickOutside(event) {
      const targetElement = this.$refs.targetElement;
      const exceptionElement = this.$refs.exceptionElement;

      if (!targetElement.contains(event.target)  && !exceptionElement.contains(event.target)) {
        this.open = false;
      }
    },
    async loadDrivers() {
      try {
        const data = await d3.csv("../data/data/driver_meta.csv");
        this.availableDrivers = data.map(row => ({
          driverName: row.driverName,
          driverTeam: row.driverTeam,
          driverUrl: row.driverPicture
        }));
      } catch (error) {
        console.error("Failed to load driver data:", error);
      }
    },
  },
  watch: {
    drivers: function (newVal, oldVal) {
      let newDriver;
      let type;

      console.log(newVal)
      console.log(oldVal)

      if (newVal.length == 2 && oldVal.length == 1) {
        newDriver = newVal[1]
        type = 1;
      } else if (newVal.length == 2 && oldVal.length == 2) {
        newDriver = newVal[0]
        type = 0;
      } else if (newVal.length == 1 && oldVal.length == 1) {
        newDriver = newVal[0]
        type = 0;
      } else if (newVal.length == 1 && oldVal.length == 2) {
        newDriver = undefined
        type = 2;
      }
      
      console.log(newDriver)

      let driverData = this.availableDrivers.filter(obj => {
        return obj.driverName === newDriver
      });

      console.log(driverData)

      if (type == 0) {
        this.firstTeam = driverData[0].driverTeam
        this.firstUrl = driverData[0].driverUrl
      } else if (type == 1) {
        this.secondTeam = driverData[0].driverTeam
        this.secondUrl = driverData[0].driverUrl
      } else if (type == 2) {
        this.secondTeam = ""
        this.secondUrl = ""
      }
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
  width: 120px;
  height: 180px;
  margin: auto;
  text-align: center;
  display:inline-block;
  overflow: hidden;
}

.parent-secondary-card {
  display: inline-block;
  vertical-align: top;
  position: relative;
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
  width: 120px;
  height: 180px;
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
  z-index: 3;
  max-height: 400px;
  position: absolute;
  overflow-y: auto;
}

.items > div:not(:last-child) {
  border-bottom: 1px solid black;
}

</style>