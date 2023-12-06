<template>
    <div>
        <h2>Monza Circuit</h2>
        <div id="container"></div>
    </div>
</template>

<script>
import * as d3 from "d3";

export default {
    props: ['driver'],

    watch: {driver: function (newVal, oldVal) {
            this.init(newVal)
            console.log('Prop changed: ', newVal, ' | was: ', oldVal)
        }},

    async mounted() {
        await this.init(this.driver)
        console.log(this.driver)
        this.update(null)
    },
    methods: {
        calculateDistance(point1, point2) {
            const dx = point1.x - point2.x;
            const dy = point1.y - point2.y;
            // return Math.sqrt(dx * dx + dy * dy);
            return dx * dx + dy * dy
        },
        update(point) {
            this.circle.selectAll().remove()

            if (point) {
                // This could be sped up using precomputed voronoi/delauney, or Newton's method
                // Then again usually data is <1000 points, so it's pretty fast anyway.
                const closest = d3.least(this.data, d => this.calculateDistance(point, d))

                const distance = Math.sqrt(this.calculateDistance(point, closest));
       
                if (distance < 2000) {
                    this.circle
                        .selectAll("circle")
                        .data([closest])
                        .join("circle")
                        .attr("cx", d => this.x(d.x))
                        .attr("cy", d => this.y(d.y))
                        .attr("r", 3);
                }
            }
        },
        distanceEvent(point) {
            const closest = d3.least(this.data, d => this.calculateDistance(point, d))
            this.$emit('EmitDistance', closest.dist)
        },

        async init(driver) {
            // https://d3js.org/d3-shape/line

            // Load data
            this.data = await d3.csv("../data/monza_circuit.csv", d => {
                return { x: parseFloat(d.X), y: parseFloat(d.Y), dist: parseFloat(d.Distance) }
            });

            const telemetry_data = await d3.csv("./data/monza_2023_fastest_laps.csv", d => {if (d.FullName == driver)
        return d})

            const extent_x = d3.extent(this.data, d => d.x)
            const extent_y = d3.extent(this.data, d => d.y)

            // Declare the chart dimensions and margins.
            const marginTop = 20;
            const marginRight = 100;
            const marginBottom = 30;
            const marginLeft = 100;
            const width = 640;
            const height = width * (extent_y[1]-extent_y[0]) / (extent_x[1]-extent_x[0]);

            // Declare the x (horizontal position) scale.
            this.x = d3.scaleLinear()
                .domain(extent_x).nice()
                .range([marginLeft, width - marginRight])

            // Declare the y (vertical position) scale.
            this.y = d3.scaleLinear()
                .domain(extent_y).nice()
                .range([height - marginBottom, marginTop])

            // track line
            this.track = d3.line()
                .curve(d3.curveCatmullRomClosed)
                .x(d => this.x(d.x))
                .y(d => this.y(d.y))

            // Create the SVG container.
            this.svg = d3.create("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("viewBox", [0, 0, width, height])
                .attr("style", "max-width: 100%; height: auto;")
                .on("mousemove", event => {
                    let [x, y] = d3.pointer(event)
                    x = this.x.invert(x)
                    y = this.y.invert(y)
                    this.update({ x: x, y: y })
                })
                .on("click", event => {
                    let [x, y] = d3.pointer(event)
                    x = this.x.invert(x)
                    y = this.y.invert(y)
                    this.distanceEvent({ x: x, y: y })
                    });

            const length = (path) => d3.create("svg:path").attr("d", path).node().getTotalLength()
            const l = length(this.track(this.data));

            this.svg.append("path")
                .datum(this.data)
                .attr("fill", "none")
                .attr("stroke", "black")
                .attr("stroke-width", 2.5)
                .attr("stroke-linejoin", "round")
                .attr("stroke-linecap", "round")
                .attr("stroke-dasharray", `0,${l}`)
                .attr("d", this.track)
                .transition()
                .duration(500)
                .ease(d3.easeLinear)
                .attr("stroke-dasharray", `${l},${l}`);

            // define color range
            var color = d3.scaleLinear()
                .domain(d3.extent(telemetry_data, d => +d.Speed))
                .range(["red", "blue"]);

            this.svg.selectAll('line')
                .data(telemetry_data).enter()
                .append("svg:line")
                .attr("x1", (d) => this.x(d.X))
                .attr("x2", (d, i) => telemetry_data[i+1] ? this.x(telemetry_data[i+1].X) : this.x(d.X))
                .attr("y1", (d) => this.y(d.Y))
                .attr("y2", (d, i) => telemetry_data[i+1] ? this.y(telemetry_data[i+1].Y) : this.y(d.Y))
                .attr("fill", "none")
                .attr("stroke", function(d) { return color(d.Speed) })
                .attr("stroke-width", 5)
                .attr("stroke-linecap", "round")
              


            this.circle = this.svg.append("g")
                .attr("fill", "white")
                .attr("stroke", "black")
                .attr("stroke-width", 2)

            container.append(this.svg.node())
        },
    }
};
</script>
