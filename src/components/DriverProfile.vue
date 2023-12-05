<template>
    <div class="profile">
        <h2 class="name">{{ driver }}</h2>
        <div>
            <img :src="headshotUrl" alt="" srcset="">
        </div>
        <table>
            <tr>
                <td class="left-column">Team</td>
                <td class="right-column">{{ team }}</td>
            </tr>
            <tr>
                <td class="left-column">Points</td>
                <td class="right-column">{{ points }}</td>
            </tr>
            <tr>
                <td class="left-column">Standing</td>
                <td class="right-column">1st</td>
            </tr>
        </table>
    </div>
</template>

<script>
import * as d3 from "d3";

// todo: cache headshot url
export default {
    props: {
        driver: {
            validator(value) {
                return true
            }
        },
    },
    data() {
        return {
            headshotUrl: "https://www.formula1.com/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png.transform/1col/image.png",
            team: "???",
            points: "???"
        }
    },
    watch: {
        driver: function (newVal, oldVal) {
            const driver = this.drivers.find(d => d.FullName === newVal)
            this.headshotUrl = driver.HeadshotUrl
            this.team = driver.TeamName
            console.log('Prop changed: ', newVal, ' | was: ', oldVal)
        }
    },
    async mounted() {
        // Load data
        this.drivers = (await d3.csv("../data/driver_info.csv"));
        const driver = this.drivers.find(d => d.FullName === this.driver)
        this.headshotUrl = driver.HeadshotUrl
        this.team = driver.TeamName
    },
};
</script>

<style scoped>
.profile {
    background-color: lightgray;
    width: 250px;
    border-radius: 10px;
    text-align: center;
}

.profile img {
    background-color: antiquewhite;
    border-radius: 10px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

td {
    padding: 4px;
    padding-left: 8px;
    padding-right: 8px;
    border: none;
}

.left-column {
    text-align: left;
}

.right-column {
    text-align: right;
}
</style>