<template>
    <div>
        <h2>{{ drivers[0] }}'s fastest lap</h2>
        <div id="trackvis"></div>
        <input type="checkbox" id="brakingCheckbox">
        <label for="brakingCheckbox"> Show Braking</label>
    </div>
</template>

<script>
import * as d3 from "d3";

export default {
    props: ['drivers', 'circuit', 'distance_highlight'],

    watch: {
        drivers: function (newVal, oldVal) {
            console.log('drivers changed: ', newVal, ' | was: ', oldVal);
            this.visualizeTrack();
            const checkbox = document.getElementById('brakingCheckbox');
            if (checkbox.checked) {
                this.drawBrakingLines()
            }
        },
        circuit: function (newVal, oldVal) {
            console.log('Circuit changed: ', newVal, ' | was: ', oldVal);
            this.init();
        },
        distance_highlight: function (newVal, oldVal) {
            this.updateDistancePoint(newVal)
        }
    },

    async mounted() {
        await this.init()
        this.visualizeTrack()
    },
    methods: {
        calculateDistance(point1, point2) {
            const dx = point1.x - point2.x;
            const dy = point1.y - point2.y;
            // return Math.sqrt(dx * dx + dy * dy);
            return dx * dx + dy * dy
        },
        calculateDx(startX, startY, endX, endY) {
            const dx = (endX - startX) / (Math.sqrt((endX - startX) ** 2 + (endY - startY) ** 2))
            return dx
        },
        calculateDy(startX, startY, endX, endY) {
            const dy = (endY - startY) / (Math.sqrt((endX - startX) ** 2 + (endY - startY) ** 2))
            return dy
        },

        updateDistancePoint(distance) {
            this.circle.selectAll().remove()

            const closest = d3.least(this.data, d => Math.abs(distance - d.dist))

            this.circle
                .selectAll("circle")
                .data([closest])
                .join("circle")
                .attr("cx", d => this.x(d.x))
                .attr("cy", d => this.y(d.y))
                .attr("r", 5);
        },

        distanceEvent(point) {
            const closest = d3.least(this.data, d => this.calculateDistance(point, d))
            this.$emit('EmitDistance', closest.dist)
        },
        async visualizeTrack() {
            const telemetry_data = await d3.csv("./data/data/" + this.circuit + "/fastest_laps.csv", d => { if (d.FullName == this.drivers[0]) return d })
            const speed_domain = d3.extent(telemetry_data, d => +d.Speed)

            // define color range
            var color = d3.scaleLinear()
                .domain(speed_domain)
                .range(["red", "#eac0a0"]);

            this.speedLine.selectAll('line').remove()
            this.speedLine.selectAll('text').remove()

            this.speedLine.selectAll('line')
                .data(telemetry_data).enter()
                .append("svg:line")
                .attr("x1", (d) => this.x(d.X))
                .attr("x2", (d, i) => telemetry_data[i + 1] ? this.x(telemetry_data[i + 1].X) : this.x(d.X))
                .attr("y1", (d) => this.y(d.Y))
                .attr("y2", (d, i) => telemetry_data[i + 1] ? this.y(telemetry_data[i + 1].Y) : this.y(d.Y))
                .attr("fill", "none")
                .attr("stroke", function (d) { return color(d.Speed) })
                .attr("stroke-width", 5)
                .attr("stroke-linecap", "round")

            // Create legend
            //Append a defs (for definition) element to  SVG
            var defs = this.speedLine.append("defs");

            //Append a linearGradient element to the defs and give it a unique id
            var linearGradient = defs.append("linearGradient")
                .attr("id", "linear-gradient");

            //Horizontal gradient
            linearGradient
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "0%");

            //Set the color for the start (0%)
            linearGradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "red"); //red

            //Set the color for the end (100%)
            linearGradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "#eac0a0"); //off-white

            const legend = this.speedLine.append("g")
                .attr("class", "legend")
                .attr("transform", `translate(${+this.svg.attr("width") - 150 - 75},${+this.svg.attr("height") - 20 - 20})`)

            //Draw the rectangle and fill with gradient
            legend.append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", 150)
                .attr("height", 20)
                .style("fill", "url(#linear-gradient)");

            // Add text for speed range
            const speedRangeText = legend.append("text")
                .attr("x", 0)
                .attr("y", 30) // Adjust the vertical position as needed
                .attr("font-size", "12px") // Set the font size
                .attr("fill", "black"); // Set the text color

            // Update the text content to display the speed range
            speedRangeText.text(`Speed Range: ${Math.round(+speed_domain[0])} - ${Math.round(+speed_domain[1])}`);
        },

        async drawBrakingLines() {
            const telemetry_data = await d3.csv("./data/data/" + this.circuit + "/fastest_laps.csv", d => {
                if (d.FullName == this.drivers[0])
                    return d
            })

            this.svg.selectAll('.braking-line').remove();

            telemetry_data.forEach((data, index) => {
                if (data.Brake == 'True') {
                    this.brakeLine.append("line")
                        .attr("class", "braking-line")
                        .attr("x1", this.x(data.X))
                        .attr("y1", this.y(data.Y))
                        .attr("x2", telemetry_data[index + 1] ? this.x(telemetry_data[index + 1].X) : this.x(data.X))
                        .attr("y2", telemetry_data[index + 1] ? this.y(telemetry_data[index + 1].Y) : this.y(data.Y))
                        .attr("stroke", "#ffa600")
                        .attr("stroke-width", 15)
                        .attr("stroke-linecap", "square")
                        .attr("opacity", 1)
                }
            });

            if (this.drivers.length == 2) {
                const telemetry_data_2 = await d3.csv("./data/data/" + this.circuit + "/fastest_laps.csv", d => {
                    if (d.FullName == this.drivers[1])
                        return d
                });
                telemetry_data_2.forEach((data, index) => {
                    if (data.Brake == 'True') {
                        this.brakeLine.append("line")
                            .attr("class", "braking-line")
                            .attr("x1", this.x(data.X))
                            .attr("y1", this.y(data.Y))
                            .attr("x2", telemetry_data_2[index + 1] ? this.x(telemetry_data_2[index + 1].X) : this.x(data.X))
                            .attr("y2", telemetry_data_2[index + 1] ? this.y(telemetry_data_2[index + 1].Y) : this.y(data.Y))
                            .attr("stroke", "green")
                            .attr("stroke-width", 10)
                            .attr("stroke-linecap", "square")
                            .attr("opacity", 1)
                    }
                });
            }
        },

        async init() {
            // Clear existing SVG element (if any)
            d3.select('#trackvis').selectAll('svg').remove();

            // Load data
            this.data = await d3.csv("../data/data/" + this.circuit + "/circuit.csv", d => {
                return { x: parseFloat(d.X), y: parseFloat(d.Y), dist: parseFloat(d.Distance) }
            });

            const extent_x = d3.extent(this.data, d => d.x)
            const extent_y = d3.extent(this.data, d => d.y)

            // Declare the chart dimensions and margins.
            const marginTop = 20;
            const marginRight = 100;
            const marginBottom = 50;
            const marginLeft = 100;
            const width = 640;
            const height = width * (extent_y[1] - extent_y[0]) / (extent_x[1] - extent_x[0]);

            // Declare the x (horizontal position) scale.
            this.x = d3.scaleLinear()
                .domain([extent_x[0] - 5, extent_x[1] + 5]).nice()
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

                    const point = { x, y }
                    const closest = d3.least(this.data, d => this.calculateDistance(point, d))

                    const distance = Math.sqrt(this.calculateDistance(point, closest));

                    if (distance < 1000) {
                        // calls updateDistancePoint
                        this.distanceEvent({ x: x, y: y })
                    }
                })

            const checkbox = document.getElementById('brakingCheckbox');
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    this.drawBrakingLines(this.driver);
                } else {
                    // If checkbox is unchecked, remove braking lines
                    this.svg.selectAll('.braking-line').remove();
                }
            });


            const length = (path) => d3.create("svg:path").attr("d", path).node().getTotalLength()
            const l = length(this.track(this.data));

            this.svg.append("path")
                .datum(this.data)
                .attr("fill", "none")
                .attr("stroke", "black")
                .attr("stroke-width", 5)
                .attr("stroke-linejoin", "round")
                .attr("stroke-linecap", "round")
                .attr("stroke-dasharray", `0,${l}`)
                .attr("d", this.track)
                .transition()
                .duration(500)
                .ease(d3.easeLinear)
                .attr("stroke-dasharray", `${l},${l}`);

            this.brakeLine = this.svg.append("g")

            // draw speed 
            this.speedLine = this.svg.append("g")

            this.circle = this.svg.append("g")
                .attr("fill", "white")
                .attr("stroke", "black")
                .attr("stroke-width", 2)

            trackvis.append(this.svg.node())
        },
    }
};
</script>
