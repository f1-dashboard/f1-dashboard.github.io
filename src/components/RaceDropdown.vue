<template>
  <div class="dropdown">
    <select v-model="selected" @change="emitRoundNumber">
      <option v-for="event in events" :key="event.RoundNumber" :value="event.RoundNumber">
        {{ event.EventName }} 
      </option>
    </select>
  </div>
</template>
  
<script>
import * as d3 from "d3";

export default {
  data() {
    return {
      events: [],
      selected: null,
    };
  },
  mounted() {
    this.loadEvents();
  },
  methods: {
    async loadEvents() {
      try {
        const data = await d3.csv("../data/data/meta.csv");
        this.events = data.map(row => ({
          EventName: row.EventName,
          RoundNumber: row.RoundNumber
        }));
        this.selected = 1;
        this.emitRoundNumber();
      } catch (error) {
        console.error("Failed to load events data:", error);
      }
    },
    emitRoundNumber() {
      // Emit the RoundNumber of the selected event
      this.$emit('round-selected', this.selected);
    },
  },
};
</script>

<style scoped>
.dropdown {
  text-align: center;
  font-weight: bold;
  font-family: formula1wide;
  /* Align text for the select box */
}

.dropdown select {
  width: 100%;
  padding: 8px;
  border-radius: 4px;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  text-align-last: center;
}

.dropdown option {
  text-align: center;
}
</style>
