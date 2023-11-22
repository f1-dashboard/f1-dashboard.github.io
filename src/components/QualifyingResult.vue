<template>
    <div>
        <h2>Monza 2023 {{ qualifying }} Results</h2>
        <div id="container"></div>
    </div>
</template>

<script>
import * as d3 from "d3";
import { watch } from "vue";

export default {
    // TODO: must be one of 'Q1', 'Q2', ...
    props: ['qualifying'],
    watch: {
        qualifying: function (newVal, oldVal) {
            this.update(newVal)
            console.log('Prop changed: ', newVal, ' | was: ', oldVal)
        }
    },
    data() {
        return {};
    },
    setup(props) {
        console.log(props.qualifying)
    },

    async mounted() {
        this.render(this.qualifying)
    },
    methods: {
        async update(q) {
            const drivers = await this.getDriverData(q)

            console.log(this.x)
            // Update axis domains
            this.x.domain([0, d3.max(drivers, d => d.delta)])
            this.y.domain(d3.sort(drivers, d => d.delta).map(d => d.full_name))
            // this.y.domain(d3.sort(drivers, d => d.delta).filter(d => !d.dnq).map(d => d.full_name))

            const t = this.svg.transition().duration(750)
            // transitions
            this.gx.transition(t)
                .call(d3.axisBottom(this.x))
            this.gy.transition(t)
                .call(d3.axisLeft(this.y))

            let bars = this.svg.selectAll("rect")
                .data(drivers)
            bars.enter()
                .append("rect")
                .merge(bars)
                .transition(t)
                .attr("class", d => d.team)
                .attr("x", this.x(0))
                .attr("y", (d) => this.y(d.full_name))
                .attr("width", (d) => this.x(d.delta) - this.x(0))
                .attr("height", this.y.bandwidth())
            bars.exit().remove()

            let timing_labels = this.svg.selectAll(".delta")
                .data(drivers)
            timing_labels.enter()
                .append("text")
                .merge(timing_labels)
                .attr("fill", "white")
                .attr("text-anchor", "end")
                .classed("delta", true)
                .transition(t)
                .attr("x", d => this.x(d.delta))
                .attr("y", d => this.y(d.full_name) + this.y.bandwidth() / 2)
                .attr("dy", "0.35em")
                .attr("dx", -4)
                .text(d => {
                    if (d.delta < 0.0000001) {
                        return d.time_string
                    }
                    return (d.delta < 0 ? "" : "+") + d.delta
                }
                )
                .call(text => text.filter(d => this.x(d.delta) - this.x(0) < 50) // short bars
                    .attr("dx", +4)
                    .attr("fill", "black")
                    .attr("text-anchor", "start"))

            timing_labels.exit().remove()
        },

        async render(q) {
            // Example taken from:
            // https://observablehq.com/@d3/horizontal-bar-chart/2?intent=fork
            // Improvements: use relative timings. e.g. delta from first
            // a cool idea would be to be able to click on someone and see their delta from others (turns into diverging bar chart)
            // https://observablehq.com/@d3/diverging-bar-chart/2?intent=fork
            const drivers = await this.getDriverData(q)

            // Declare the chart dimensions and margins.
            const barHeight = 25;
            const marginTop = 20;
            const marginRight = 20;
            const marginBottom = 30;
            const marginLeft = 100;
            const width = 640;
            const height = 500;

            // Declare the x (horizontal position) scale.
            const x = d3.scaleLinear()
                .domain([0, d3.max(drivers, d => d.delta)])
                .range([marginLeft, width - marginRight]);

            // Declare the y (vertical position) scale.
            const y = d3.scaleBand()
                .domain(d3.sort(drivers, d => d.delta).map(d => d.full_name))
                .rangeRound([marginTop, height - marginBottom])
                .padding(0.1);

            // Create the SVG container.
            const svg = d3.create("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("viewBox", [0, 0, width, height])
                .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;");

            // Create the bar for each driver
            this.bars = svg.append("g")
                .selectAll()
                .data(drivers)
                .join("rect")
                .attr("class", d => d.team)
                .attr("x", x(0))
                .attr("y", (d) => y(d.full_name))
                .attr("width", (d) => x(d.delta) - x(0))
                .attr("height", y.bandwidth())

            // Add the timing label 00:00.000
            this.timing_labels = svg.append("g")
                .attr("fill", "white")
                .attr("text-anchor", "end")
                .selectAll()
                .data(drivers)
                .join("text")
                .classed("delta", true)
                .attr("x", d => x(d.delta))
                .attr("y", d => y(d.full_name) + y.bandwidth() / 2)
                .attr("dy", "0.35em")
                .attr("dx", -4)
                .text(d => {
                    if (d.delta < 0.0000001) {
                        return d.time_string
                    }
                    return (d.delta < 0 ? "" : "+") + d.delta
                }
                )
                .call(text => text.filter(d => x(d.delta) - x(0) < 50) // short bars
                    .attr("dx", +4)
                    .attr("fill", "black")
                    .attr("text-anchor", "start"))

            // Add the x-axis.
            this.gx = svg.append("g")
                .attr("transform", `translate(0,${height - marginBottom})`)
                .call(d3.axisBottom(x));

            // Add the y-axis.
            this.gy = svg.append("g")
                .attr("transform", `translate(${marginLeft},0)`)
                .call(d3.axisLeft(y));

            this.x = x;
            this.y = y;
            this.svg = svg;

            // Append the SVG element. 
            if (container.childNodes.length > 0) {
                container.replaceChild(svg.node(), container.childNodes[0]);
            } else {
                container.append(svg.node())
            }
        },

        async getDriverData(q) {
            const drivers = await d3.csv("./data/monza_qualifying_2023.csv", (d) => {
                // Parse the duration string, e.g. "0 days 00:01:20.643000"
                // const durationArray = d.Q1.split(" ");
                const durationArray = d[q].split(" ");

                try {
                    // Extract days, hours, minutes, seconds, and milliseconds
                    const days = parseInt(durationArray[0]);
                    const timeComponents = durationArray[2].split(":");
                    const hours = parseInt(timeComponents[0]);
                    const minutes = parseInt(timeComponents[1]);
                    const secondsArray = timeComponents[2].split(".");
                    const seconds = parseInt(secondsArray[0]);
                    const milliseconds = parseInt(secondsArray[1]) / 1000;
                    return {
                        full_name: d.FullName,
                        q1_lap_time: hours * 3600 + minutes * 60 + seconds + milliseconds / 1000,
                        time_string: `${minutes}:${seconds}.${milliseconds}`,
                        dnq: false,
                        team: d.TeamId
                    }
                } catch {
                    // Don't include drivers without lap times
                    return {
                        full_name: d.FullName,
                        q1_lap_time: 0,
                        time_string: `DNQ`,
                        dnq: true,
                        team: d.TeamId
                    }
                }

            });
            console.log(drivers)

            // Choose the fastest time to calculate the delta
            const driversWithTimes = d3.filter(drivers, d => !d.dnq)
            const relativeTime = d3.min(driversWithTimes, d => d.q1_lap_time)
            drivers.forEach(d => d.delta = (d.q1_lap_time - relativeTime).toFixed(3))
            return d3.filter(drivers, d => !d.dnq)
        }
    }
};
</script>

<style>
/* rect {
    fill: steelblue
} */
</style>