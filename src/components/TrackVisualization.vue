<template>
    <div>
        <h2>Track Monza 2019 {{ driver }}</h2>
        <div id="container"></div>
    </div>
</template>

<script>
import * as d3 from "d3";

export default {
    props: ['driver'],

    async mounted() {
        this.render(this.driver)
    },
    methods: {
        async render(q) {
            const telemetry_data = await d3.csv("./data/telemetry_monza.csv")

            // Max value observed:
            const max_x = d3.max(telemetry_data, function(d) { return +d.X; })
            const max_y = d3.max(telemetry_data, function(d) { return +d.Y; })
            const max_speed = d3.max(telemetry_data, function(d) { return +d.Speed; })

            // Min value observed:
            const min_x = d3.min(telemetry_data, function(d) { return +d.X; })
            const min_y = d3.min(telemetry_data, function(d) { return +d.Y; })
            const min_speed = d3.min(telemetry_data, function(d) { return +d.Speed; })     

            // set the dimensions and margins of the graph
            var margin = {top: 10, right: 30, bottom: 30, left: 60},
                width = 460 - margin.left - margin.right,
                height = 400 - margin.top - margin.bottom;

            // append the svg object to the body of the page
            var svg = d3.select("#container")
            .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
            .append("g")
                .attr("transform",
                    "translate(" + margin.left + "," + margin.top + ")");

            // Add X axis
            var x = d3.scaleLinear()
                .domain([min_x, max_x])
                .range([ 0, width ]);
            // svg.append("g")
            //     .call(d3.axisBottom(x));

            // Add Y axis
            var y = d3.scaleLinear()
                .domain([min_y, max_y])
                .range([ height, 0 ]);
            // svg.append("g")
            //     .call(d3.axisLeft(y));

            // define color range
            var color = d3.scaleLinear()
                .domain([min_speed, max_speed])
                .range(["red", "blue"]);

            svg.selectAll('line')
                .data(telemetry_data).enter()
                .append("svg:line")
                .attr("x1", function(d) { return x(d.X)})
                .attr("x2", function(d, i) { return telemetry_data[i+1] ? x(telemetry_data[i+1].X) : x(d.X)})
                .attr("y1", function(d) { return y(d.Y)})
                .attr("y2", function(d, i) { return telemetry_data[i+1] ? y(telemetry_data[i+1].Y) : y(d.Y)})
                .attr("fill", "none")
                .attr("stroke", function(d) { return color(d.Speed) })
                .attr("stroke-width", 15)
        },
    }
};
</script>

<style></style>