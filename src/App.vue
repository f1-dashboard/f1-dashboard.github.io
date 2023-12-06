<script setup>
import HelloWorld from './components/HelloWorld.vue'
import TheWelcome from './components/TheWelcome.vue'
import QualifyingResult from './components/QualifyingResult.vue'
import TrackVis from './components/TrackVis.vue'
import DropDown from './components/simple/DropDown.vue'
import TrackSpeedVis from './components/TrackSpeedVis.vue'
import { ref } from 'vue'
import InfoCard from './components/InfoCard.vue'

let category = ref("Q1")

let distance = ref(1)
let driver = ref("Carlos Sainz")
</script>

<template>
  <header>
    <!-- <img alt="Vue logo" class="logo" src="./assets/logo.svg" width="125" height="125" />

    <div class="wrapper">
      <HelloWorld msg="You did it!" />
    </div> -->
    <DropDown :items="['Q1', 'Q2', 'Q3']" @clicked="(n) => category = n" />
    <QualifyingResult :qualifying=category @EmitDriver="(n) => driver = n" />
  </header>

  <main>
    <TrackSpeedVis :distance_highlight="distance" />
    <!-- <TrackSpeedVis :distance_highlight="distance" :relative="true" /> -->

    <TrackVis :driver=driver @EmitDistance="(n) => distance = n" />
    <InfoCard :driver=driver />
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
