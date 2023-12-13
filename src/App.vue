<script setup>
import QualifyingResult from './components/QualifyingResult.vue'
import TrackVis from './components/TrackVis.vue'
import SpeedVis from './components/SpeedVis.vue'
import RaceDropdown from './components/RaceDropdown.vue'
import { ref } from 'vue'
import InfoCard from './components/InfoCard.vue'
import GapVis from './components/GapVis.vue'

let category = ref("Q1")
let distance = ref(1)
let driver = ref("Carlos Sainz")
let round = ref(1)

const updateRound = (newRound) => {
  round.value = newRound;
  console.log("set new round:", newRound)
}
</script>

<template>
  <div class="header">
    <RaceDropdown @round-selected="updateRound"></RaceDropdown>
  </div>

  <div class="content">
    <div class="left">
      <QualifyingResult :qualifying=category :circuit=round @EmitDriver="(n) => driver = n" />
      <InfoCard id="ic" :driver=driver />
    </div>

    <div class="center">
      <TrackVis :driver=driver :circuit=round @EmitDistance="(n) => distance = n" />
    </div>

    <div class="right">
      <SpeedVis :distance_highlight="distance" :circuit=round />
      <GapVis :distance_highlight="distance" />
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

.content>div {
  text-align: center;
  overflow: auto;
}

#ic {
  margin-top: 20px;
}
</style>

