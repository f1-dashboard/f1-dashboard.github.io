<script setup>
import QualifyingResult from './components/QualifyingResult.vue'
import TrackVis from './components/TrackVis.vue'
import SpeedVis from './components/SpeedVis.vue'
import RaceDropdown from './components/RaceDropdown.vue'
import { ref } from 'vue'
import InfoCard from './components/InfoCard.vue'
import GapVis from './components/GapVis.vue'
import QualifyingSelector from './components/QualifyingSelector.vue'
import Introduction from './components/Introduction.vue'

let quali = ref("Q1")
let distance = ref(1)

// Drivers is a list (max 2) of drivers that will be compared
let drivers = ref(["Max Verstappen"])
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
      <div id="ic">
        <InfoCard @emitDrivers="(n) => drivers = n" :drivers=drivers />
      </div>
      <QualifyingResult :qualifying=quali :circuit=round :setDrivers=drivers @EmitDriver="(n) => drivers = n" />
    </div>

    <div class="center">
      <div id="track">
        <TrackVis :drivers=drivers :circuit=round @EmitDistance="(n) => distance = n" :distance_highlight="distance"
          :qualifying="quali" />
      </div>
      <div id="qs">
        <QualifyingSelector @QualiChanged="q => quali = q" />
      </div>
    </div>

    <div class="right">
      <SpeedVis :distance_highlight="distance" @DistanceChanged="(n) => distance = n" :circuit=round :drivers="drivers"
        :qualifying="quali" />
      <GapVis :distance_highlight="distance" @DistanceChanged="(n) => distance = n" :circuit=round :drivers="drivers"
        :qualifying="quali" />
      <Introduction />
    </div>
  </div>
</template>

<style scoped>
.header {
  text-align: center;
  font-size: 1.7em;
  text-align: center;
}

.center {
  display: flex;
  position: relative;
  margin-top: 0px;
  align-items: center;
  justify-content: center;
}

.content {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1fr;
  gap: 3px;
}

.content>div {
  text-align: center;
  overflow: auto;
}

.left {
  margin-top: -30px;
}

#ic {
  margin-bottom: 30px;
}

#track {
  margin-bottom: 40px;
}

#qs {
  text-align: center;
  position: absolute;
  bottom: 0;
  margin-left: auto;
  margin-right: auto;
  left: 0;
  right: 0;
  margin-bottom: 40px;
}
</style>

