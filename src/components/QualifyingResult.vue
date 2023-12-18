<template>
    <div>
        <div id="qual"></div>
    </div>
</template>

<script>
import * as d3 from "d3";

const qualis = ['Q1', 'Q2', 'Q3']

function parseTimeString(ts) {
    const durationArray = ts.split(" ");

    // Extract days, hours, minutes, seconds, and milliseconds
    const days = parseInt(durationArray[0]);
    const timeComponents = durationArray[2].split(":");
    const hours = parseInt(timeComponents[0]);
    const minutes = parseInt(timeComponents[1]);
    const secondsArray = timeComponents[2].split(".");
    const seconds = parseInt(secondsArray[0]);
    let milliseconds = 0;
    if (secondsArray[1]) {
        milliseconds = parseInt(secondsArray[1]) / 1000;
    }

    return {
        lap_time: hours * 3600 + minutes * 60 + seconds + milliseconds / 1000,
        time_string: `${minutes}:${seconds}.${milliseconds}`,
    }
}


export default {
    props: {
        qualifying: {
            validator(value) {
                return qualis.includes(value)
            }
        },
        circuit: {
            default: 1
        },
        setDrivers: {
            default: []
        }
    },
    watch: {
        qualifying: function (newVal, oldVal) {
            this.update(null)
            console.log('Prop changed: ', newVal, ' | was: ', oldVal)
        },
        circuit: async function (newVal, oldVal) {
            await this.init()
            this.update(null)
            console.log('Prop changed: ', newVal, ' | was: ', oldVal)
        }
    },
    async mounted() {
        await this.init()
        this.update(null)
    },
    methods: {
        update(relativeTo) {
            const drivers = this.getDriverData(this.qualifying, relativeTo)
            const format = d3.format("+.3")
            const eps = 0.0000001

        if (!relativeTo) {
            relativeTo = drivers[0].full_name
            }
            // ensure other components are loaded before emitting driver event
            setTimeout(() => {
                if (this.setDrivers != undefined) {
                    this.$emit('EmitDriver', [relativeTo, this.setDrivers[1]]);
                } else {
                    this.$emit('EmitDriver', [relativeTo, undefined]);
                }
            }, 100)
            // This is temporary to see two drivers, should be removed when you can select two drivers
            

            // Update axis domains
            this.x.domain(d3.extent(drivers, d => d.delta))
            this.y.domain(drivers.map(d => d.full_name))

            const t = this.svg.transition().duration(750)

            let bars = this.svg.selectAll("rect")
                .data(drivers)
            bars.enter()
                .append("rect")
                .on("click", (d, i) => this.update(i.full_name))
                .merge(bars)
                .transition(t)
                .attr("class", d => d.team)
                .attr("x", d => this.x(Math.min(d.delta, 0)))
                .attr("y", d => this.y(d.full_name))
                .attr("width", d => Math.abs(this.x(d.delta) - this.x(0)))
                .attr("height", this.y.bandwidth())

            bars.exit().remove()

            let timing_labels = this.svg.selectAll(".delta")
                .data(drivers)
            timing_labels.enter()
                .append("text")
                .merge(timing_labels)
                .attr("fill", "white")
                .classed("delta", true)
                .transition(t)
                .attr("text-anchor", d => d.delta > 0 ? "end" : "start")
                .attr("x", d => this.x(d.delta))
                .attr("y", d => this.y(d.full_name) + this.y.bandwidth() / 2)
                .attr("dy", "0.35em")
                .attr("dx", d => -Math.sign(d.delta) * 4)
                .text(d => {
                    if (d.delta < eps && d.delta > -eps) {
                        return d[this.qualifying].time_string
                    }
                    return format(d.delta)
                }
                )
                .call(text => text.filter(d => Math.abs(this.x(d.delta) - this.x(0)) < 40) // short bars
                    .attr("dx", d => Math.sign(d.delta + eps) * 4)
                    .attr("fill", "black")
                    .attr("text-anchor", d => d.delta < 0 ? "end" : "start"))


            timing_labels.exit().remove()

            // transitions
            this.gx.transition(t)
                .call(d3.axisBottom(this.x))
            this.gy.transition(t)
                .attr("transform", `translate(${this.x(0)},0)`)
                .call(d3.axisLeft(this.y).tickSize(0))
                .call(g => g.selectAll(".tick text").filter((d, i) => drivers[i]?.delta < 0)
                    .attr("text-anchor", "start")
                    .attr("x", 6))
                .call(g => g.selectAll(".tick text").filter((d, i) => drivers[i]?.delta >= 0)
                    .attr("text-anchor", "end"));
        },

        async init() {
            // Clear existing SVG element (if any)
            d3.select('#qual').selectAll('svg').remove();

            // Load data
            const data = d3.csv("./data/data/" + this.circuit + "/qual_results.csv", (d) => {
                let driver = {
                    full_name: d.FullName,
                    team: d.TeamId
                };

                for (let q of qualis) {
                    // Parse the duration string, e.g. "0 days 00:01:20.643000"

                    try {
                        driver[q] = parseTimeString(d[q])
                    } catch {
                        continue;
                    }

                }

                return driver
            });

            // Declare the chart dimensions and margins.
            const barHeight = 25;
            const marginTop = 20;
            const marginRight = 100;
            const marginBottom = 30;
            const marginLeft = 100;
            const width = 640;
            const height = 500;

            // Declare the x (horizontal position) scale.
            this.x = d3.scaleLinear()
                .rangeRound([marginLeft, width - marginRight]);

            // Declare the y (vertical position) scale.
            this.y = d3.scaleBand()
                .rangeRound([marginTop, height - marginBottom])
                .padding(0.1);

            // Create the SVG container.
            this.svg = d3.create("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("viewBox", [0, 0, width, height])
                .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;");

            // Create the bar for each driver
            this.bars = this.svg.append("g")

            // Add the timing label 00:00.000
            this.timing_labels = this.svg.append("g")

            // Add the x-axis.
            this.gx = this.svg.append("g")
                .attr("transform", `translate(0,${height - marginBottom})`)
                .call(d3.axisBottom(this.x));

            // Add the y-axis.
            this.gy = this.svg.append("g")
                .attr("transform", `translate(${this.x(0)},0)`)
                .call(d3.axisLeft(this.y).tickSize(0));

            // Append the SVG element. 
            qual.append(this.svg.node())

            this.drivers = await data;
        },

        getDriverData(quali, relativeTo) {
            const driversInQuali = d3.filter(this.drivers, d => d[quali])

            let relativeTime;
            if (relativeTo && d3.filter(driversInQuali, d => d.full_name === relativeTo).length > 0) {
                relativeTime = d3.filter(driversInQuali, d => d.full_name === relativeTo)[0][quali].lap_time
            } else {
                relativeTime = d3.min(driversInQuali, d => d[quali].lap_time)
            }
            driversInQuali.forEach(d => d.delta = (d[quali].lap_time - relativeTime))
            console.log(driversInQuali)
            return d3.sort(driversInQuali, d => d.delta)
        }
    }
};
</script>
