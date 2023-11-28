<template>
    <div>
        <h2>Monza 2019: Track Position</h2>
        <div id="container"></div>
    </div>
</template>

<script>
import * as d3 from "d3";

export default {
    mounted() {
        this.init();
    },
    methods: {
        init() {
            Promise.all([
                d3.csv('data/lec_monzaq_laps.csv'),
                d3.csv('data/ver_monzaq_laps.csv')
            ]).then(files => {
                this.createGraph(files);
            });
        },

        createGraph(files) {
            const marginTop = 20;
            const marginRight = 100;
            const marginBottom = 30;
            const marginLeft = 100;
            const width = 640;
            const height = width;

            const data = files.map(file => file.map(d => ({
                driver: d.Driver,
                lap: +d.LapNumber,
                position: +d.Position
            })).filter(d => !isNaN(d.lap) && !isNaN(d.position)));

            this.svg = d3.select("#container")
                .append("svg")
                .attr("width", width + marginLeft + marginRight)
                .attr("height", height + marginTop + marginBottom)
                .append("g")
                .attr("transform", `translate(${marginLeft},${marginTop})`);

            // Add X axis
            const x = d3.scaleLinear()
                .domain(d3.extent(data[0], d => d.lap))
                .range([0, width]);
            this.svg.append("g")
                .attr("transform", `translate(0,${height})`)
                .call(d3.axisBottom(x));

            // Add Y axis
            const y = d3.scaleLinear()
                .domain([1, 22]) //22 F1 drivers
                .range([0, height]);
            this.svg.append("g")
                .call(d3.axisLeft(y));

            const line = d3.line()
                .x(d => x(d.lap))
                .y(d => y(d.position));

            
            data.forEach((driverData) => {
                // Draw the lines
                this.svg.append("path")
                    .datum(driverData)
                    .attr("fill", "none")
                    .attr("stroke", "red")
                    .attr("stroke-width", 1.5)
                    .attr("d", line); 

                // Add driver name
                const lastPoint = driverData[driverData.length - 1];
                this.svg.append("text")
                    .attr("x", x(lastPoint.lap) + 5)
                    .attr("y", y(lastPoint.position))
                    .text(lastPoint.driver)
                    .attr("font-size", "10px")
                    .attr("fill", "red");
            });
        }
    }
};
</script>

<style>
#container {
    width: 100%;
    height: 100%;
}
</style>
