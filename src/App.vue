<script setup>
import QualifyingResult from './components/QualifyingResult.vue'
import TrackVis from './components/TrackVis.vue'
import DropDown from './components/simple/DropDown.vue'
import TrackSpeedVis from './components/TrackSpeedVis.vue'
import RaceDropdown from './components/RaceDropdown.vue'
import { ref } from 'vue'
import InfoCard from './components/InfoCard.vue'

let category = ref("Q1")
let distance = ref(1)
let driver = ref("Carlos Sainz")
let round = "..."
</script>

<template>
  <div class="header">
    <RaceDropdown @round-selected="roundSelected"></RaceDropdown>
  </div>
  
  <div class="content">
    <div class="left">
      left
    </div>

    <div class="center">
      center
    </div>

    <div class="right">
      right
    </div>
  </div>
</template>

<style scoped>
.header {
  text-align: center;
  font-size: 1.7em;
  text-align: center;
}

.content {
  display: grid; 
  grid-template-columns: 1fr 1fr 1fr; 
  gap: 3px; 
}

.content > div {
  text-align: center;
}
</style>

