<script setup>
import QualifyingResult from './components/QualifyingResult.vue'
import TrackVis from './components/TrackVis.vue'
import SpeedVis from './components/SpeedVis.vue'
import RaceDropdown from './components/RaceDropdown.vue'
import { ref } from 'vue'
import InfoCard from './components/InfoCard.vue'
import GapVis from './components/GapVis.vue'
import QualifyingSelector from './components/QualifyingSelector.vue'

let quali = ref("Q1")
let distance = ref(1)

// Drivers is a list (max 2) of drivers that will be compared
let drivers = ref(["Carlos Sainz"])
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
      <InfoCard id="ic" :drivers=drivers />
      <QualifyingResult :qualifying=quali :circuit=round @EmitDriver="(n) => drivers = [n]" />
    </div>

    <div class="center">
      <TrackVis :drivers=drivers :circuit=round @EmitDistance="(n) => distance = n" :distance_highlight="distance" />
    </div>

    <div class="right">
      <SpeedVis :distance_highlight="distance" @DistanceChanged="(n) => distance = n" :circuit=round :drivers="drivers" />
      <GapVis :distance_highlight="distance" @DistanceChanged="(n) => distance = n" :circuit=round :drivers="drivers" />
    </div>
  </div>
  <div id="qs">
    <QualifyingSelector @QualiChanged="q => quali = q" />
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

#qs {
  text-align: center;
}

/* 
#quali {
  margin-top: 100px;
} */
</style>

