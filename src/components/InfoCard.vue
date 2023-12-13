<template>
  <div class="card">
    <img class="card-image" :src="picture_url" style="width:100%">
    <h1 style="font-size: 10px">{{ this.driver }}</h1>
    <p class="title">{{ this.team }}</p>
  </div>
  </template>
  
  <script>
  export default {
      props: ['driver'],
      data() {
      return {
        picture_url: "../../data/Placeholder.jpg",
        team: "Driver team"
      }},
      watch: {driver: function (newVal, oldVal) {
              this.picture_url = "../../data/Placeholder.jpg"
              this.team = "Other team"
          }},
  }
  </script>
  
  
  <style scope>
  .card {
      box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
      max-width: 100px;
      margin: auto;
      text-align: center;
      border-radius: 10%;
    }

    .card-image {
      box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
      max-width: 100px;
      margin: auto;
      text-align: center;
      border-radius: 10%;
    }
    
    .title {
      color: grey;
      font-size: 10px;
    }
  </style>
    