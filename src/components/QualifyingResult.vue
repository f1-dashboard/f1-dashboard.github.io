<template>
    <div id="container">
        <h2>Monza 2019 Q1 Results</h2>
    </div>
</template>

<script>
import * as d3 from "d3";
export default {
    data() {
        return {};
    },
    async mounted() {
        // Example taken from:
        // https://observablehq.com/@d3/horizontal-bar-chart/2?intent=fork
        // Improvements: use relative timings. e.g. delta from first
        // a cool idea would be to be able to click on someone and see their delta from others (turns into diverging bar chart)
        // https://observablehq.com/@d3/diverging-bar-chart/2?intent=fork
        const drivers = await d3.csv("./data/monza_qualifying.csv", (d) => {
            // Parse the duration string, e.g. "0 days 00:01:20.643000"
            const durationArray = d.Q1.split(" ");
            
            try {
                // Extract days, hours, minutes, seconds, and milliseconds
                const days = parseInt(durationArray[0]);
                const timeComponents = durationArray[2].split(":");
                const hours = parseInt(timeComponents[0]);
                const minutes = parseInt(timeComponents[1]);
                const secondsArray = timeComponents[2].split(".");
                const seconds = parseInt(secondsArray[0]);
                const milliseconds = parseInt(secondsArray[1]);
                return {
                    full_name: d.FullName,
                    q1_lap_time: hours * 3600 + minutes * 60 + seconds + milliseconds / 1000000,
                    time_string: `${minutes}:${seconds}.${milliseconds}`
                }
            } catch {
                return {
                    full_name: d.FullName,
                    q1_lap_time: 0,
                    time_string: "00:00:00.00"
                }
            }
            
        });
        console.log(drivers)

        // Declare the chart dimensions and margins.
        const barHeight = 25;
        const marginTop = 20;
        const marginRight = 20;
        const marginBottom = 30;
        const marginLeft = 100;
        const width = 640;
        const height = Math.ceil((drivers.length + 0.1) * barHeight) + marginTop + marginBottom;


        // Declare the x (horizontal position) scale.
        const x = d3.scaleLinear()
            .domain([0, d3.max(drivers, d => d.q1_lap_time)])
            .range([marginLeft, width - marginRight]);

        // Declare the y (vertical position) scale.
        const y = d3.scaleBand()
            .domain(d3.sort(drivers, d => d.q1_lap_time).map(d => d.full_name))
            .rangeRound([marginTop, height - marginBottom])
            .padding(0.1);

        // Create the SVG container.
        const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height])
            .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;");

        // Create the bar for each driver
        svg.append("g")
            .attr("fill", "steelblue")
            .selectAll()
            .data(drivers)
            .join("rect")
                .attr("x", x(0))
                .attr("y", (d) => y(d.full_name))
                .attr("width", (d) => x(d.q1_lap_time) - x(0))
                .attr("height", y.bandwidth())

        // Add the timing label 00:00.000
        svg.append("g")
            .attr("fill", "white")
            .attr("text-anchor", "end")
            .selectAll()
            .data(drivers)
            .join("text")
                .attr("x", d => x(d.q1_lap_time))
                .attr("y", d => y(d.full_name) + y.bandwidth() / 2)
                .attr("dy", "0.35em")
                .attr("dx", -4)
                .text(d => d.time_string)

        // Add the x-axis.
        svg.append("g")
            .attr("transform", `translate(0,${height - marginBottom})`)
            .call(d3.axisBottom(x));

        // Add the y-axis.
        svg.append("g")
            .attr("transform", `translate(${marginLeft},0)`)
            .call(d3.axisLeft(y));

        // Append the SVG element.
        container.append(svg.node());
    },
};
</script>

<style>
</style>