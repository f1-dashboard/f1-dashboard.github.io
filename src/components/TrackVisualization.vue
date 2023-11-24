<template>
    <div>
        <h2>Monza 2019 {{ driver }}</h2>
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

            // @TODO: Add different line elements to get different colors, see example: 
            // https://stackoverflow.com/questions/21219557/drawing-different-colored-strokes-between-center-and-different-nodes-in-a-d3-j


            // // add color
            // var color = d3.scaleLinear()
            //     .domain([min_speed, max_speed])
            //     .range(["red", "blue"])

            // Add the line
            svg.append('path')
                .datum(telemetry_data)
                .attr('fill', 'none')
                .attr('stroke', 'red') // Set the stroke color
                .attr('stroke-width', 10) 
                .attr('d', d3.line()
                    .x(function(d) { return x(d.X); }) // Use the 'x' scale for 'X' coordinates
                    .y(function(d) { return y(d.Y); }) // Use the 'y' scale for 'Y' coordinates
                );

        },
    }
};
</script>

<style></style>