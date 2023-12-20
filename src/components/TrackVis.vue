<template>
    <div>
        <h2>{{ drivers[0] }}'s fastest lap in {{ qualifying }}</h2>
        <div id="trackvis"></div>
        <input type="checkbox" id="brakingCheckbox">
        <label for="brakingCheckbox"> Show Braking</label>
    </div>
</template>

<style scoped>
/* #trackvis {
    background-color: aliceblue;
    border-radius: 5px;
    padding: 5px 0;
    border-style: solid;
    border-color: rgba(0, 0, 0, 0.5);
} */
</style>

<script>
import * as d3 from "d3";

const colors = {
    red_bull: "#3671c6",
    mercedes: "#6cd3bf",
    ferrari: "#f91536",
    mclaren: "#f58020",
    aston_martin: "#358c75",
    alpine: "#2293d1",
    williams: "#37bedd",
    alphatauri: "#5e8faa",
    alfa: "#c92d4b",
    haas: "#b6babd",
}

export default {
    props: ['drivers', 'circuit', 'distance_highlight', 'qualifying'],

    watch: {
        drivers: function (newVal, oldVal) {
            if (!this.mounted) {
                return
            }
            this.visualizeTrack();
            const checkbox = document.getElementById('brakingCheckbox');
            if (checkbox.checked) {
                this.drawBrakingLines()
            }
        },
        circuit: async function (newVal, oldVal) {
            await this.init();
        },
        distance_highlight: function (newVal, oldVal) {
            this.updateDistancePoint(newVal)
        },
        qualifying: function (newVal, oldVal) {
            if (!this.mounted) {
                return
            }
            this.visualizeTrack();
            const checkbox = document.getElementById('brakingCheckbox');
            if (checkbox.checked) {
                this.drawBrakingLines()
            }
        }
    },

    async mounted() {
        await this.init()
        this.visualizeTrack()
        this.mounted = true
    },
    methods: {
        calculateDistance(point1, point2) {
            const dx = point1.X - point2.X;
            const dy = point1.Y - point2.Y;
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

            const closest = d3.least(this.circuit_data, d => Math.abs(distance - d.Distance))

            this.circle
                .selectAll("circle")
                .data([closest])
                .join("circle")
                .attr("cx", d => this.x(d.X))
                .attr("cy", d => this.y(d.Y))
                .attr("r", 5);
        },

        distanceEvent(point) {
            const closest = d3.least(this.circuit_data, d => this.calculateDistance(point, d))
            this.$emit('EmitDistance', closest.Distance)
        },

        visualizeTrack() {
            console.log(this.driver_data[this.qualifying], this.drivers)
            const telemetry_data = d3.filter(this.driver_data[this.qualifying], d => d.FullName == this.drivers[0])
            console.log(telemetry_data)
            const [minSpeed, maxSpeed] = d3.extent(telemetry_data, d => +d.Speed)

            // define color range
            // var color = d3.scaleLinear()
            //     .domain(speed_domain)
            //     .range(["red", "#eac0a0"]);


            // https://d3js.org/d3-scale-chromatic/sequential
            // const colorMap = d3.interpolateInferno
            const colorMap = d3.interpolateRdPu
            // const colorMap = d3.interpolateReds
            const color = d3.scaleSequential((speed) => colorMap((speed - minSpeed) / (maxSpeed - minSpeed)));

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
            const legendWidth = 150
            const legendHeight = 20

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

            for (let i = 0; i <= 100; i += 10) {
                //Set the color for the start (0%)
                linearGradient.append("stop")
                    .attr("offset", `${i}%`)
                    .attr("stop-color", colorMap(i / 100));
            }


            const legendSpeed = this.speedLine.append("g")
                .attr("class", "legend")
                .attr("transform", `translate(${+this.svg.attr("width") - legendWidth - 75},${+this.svg.attr("height") - 50})`)

            // // Legend border
            const borderWidth = 2
            legendSpeed.append("rect")
                .attr("x", -borderWidth)
                .attr("y", -borderWidth)
                .attr("width", legendWidth + 2 * borderWidth)
                .attr("height", legendHeight + 2 * borderWidth)
                .style("fill", "black");

            //Draw the rectangle and fill with gradient
            legendSpeed.append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", legendWidth)
                .attr("height", legendHeight)
                .style("fill", "url(#linear-gradient)");

            // Add text for speed range
            legendSpeed.append("text")
                .attr("x", 0)
                .attr("y", legendHeight + 15)
                .attr("font-size", "12px")
                .attr("fill", "black")
                .text(`${Math.round(minSpeed)}`);

            legendSpeed.append("text")
                .attr("x", legendWidth / 2)
                .attr("y", legendHeight + 15)
                .attr("font-size", "12px")
                .attr("fill", "black")
                .attr("text-anchor", "middle")
                .text("speed (km/h)");

            legendSpeed.append("text")
                .attr("x", legendWidth)
                .attr("y", legendHeight + 15)
                .attr("font-size", "12px")
                .attr("fill", "black")
                .attr("text-anchor", "end")
                .text(`${Math.round(maxSpeed)}`);

        },

        drawBrakingLines() {
            // Minimum distance between two braking poitns to be considered different lines
            const min_break_distance = 50

            this.svg.selectAll('.braking-line').remove();
            this.svg.selectAll('.legend-braking-line').remove();

            const drawBrakingLine = (driverName, stroke_width, legend_y, color = undefined) => {
                const telemetry_data = d3.filter(this.driver_data[this.qualifying], d => d.FullName === driverName && d.Brake === 'True')
                if (telemetry_data.length === 0) {
                    return
                }
                if (!color) {
                    color = colors[telemetry_data[0].TeamId]
                }

                const grouped_data = []
                let current_break_section = []
                telemetry_data.forEach((data, index) => {
                    let this_distance = data.Distance
                    // this logic is false but it doesn't matter cause nobody is braking at the finish
                    let next_distance = telemetry_data[index + 1] ? telemetry_data[index + 1].Distance : telemetry_data[0].Distance

                    if (next_distance - this_distance < min_break_distance) {
                        current_break_section.push(data)
                    } else {
                        grouped_data.push(current_break_section)
                        current_break_section = []
                    }
                })
                if (current_break_section.length > 0) {
                    grouped_data.push(current_break_section)
                }

                const brakePath = d3.line()
                    .curve(d3.curveBasisOpen)
                    .x(d => this.x(d.X)).y(d => this.y(d.Y))

                for (const driver_data of grouped_data) {
                    const length = (path) => d3.create("svg:path").attr("d", path).node().getTotalLength()
                    const l = length(this.track(driver_data));

                    this.brakeLine.append("path")
                        .datum(driver_data)
                        .attr("class", "braking-line")
                        .attr("fill", "none")
                        .attr("stroke", color)
                        .attr("stroke-width", stroke_width)
                        .attr("stroke-linejoin", "miter-clip")
                        .attr("stroke-linecap", "butt")
                        .attr("d", brakePath)
                        .attr("stroke-dasharray", `${l},${l}`);
                }

                legendDrivers.append("rect")
                    .attr("x", 0)
                    .attr("y", legend_y)
                    .attr("width", 20)
                    .attr("height", 20)
                    .style("fill", color);

                const LegendDriversText1 = legendDrivers.append("text")
                    .attr("x", 35)
                    .attr("y", 15 + legend_y) // relative to legend
                    .attr("font-size", "12px")
                    .attr("fill", "black");

                LegendDriversText1.text(driverName);
            }

            // const driverColor1 = "#E01A4F"
            // const driverColor2 = "#53B3CB"
            // undefined colors means the driver's team color will be selected
            const driverColor1 = undefined
            const driverColor2 = undefined
            // const driverColor2 = "limegreen"

            const legendDrivers = this.speedLine.append("g")
                .attr("class", "legend-braking-line")
                .attr("transform", `translate(${0 + 75},${+this.svg.attr("height") - 50})`)

            drawBrakingLine(this.drivers[0], 25, 0, driverColor1)
            if (this.drivers.length == 2) {
                drawBrakingLine(this.drivers[1], 18, 30, driverColor2)
            }
        },

        async init() {
            // Clear existing SVG element (if any)
            d3.select('#trackvis').selectAll('svg').remove();

            // Load data
            this.circuit_data = await d3.csv("../data/" + this.circuit + "/circuit.csv", d => {
                return { X: +d.X, Y: +d.Y, Distance: +d.Distance }
            });

            // Load data
            this.driver_data = {}
            for (const q of ['Q1', 'Q2', 'Q3']) {
                this.driver_data[q] = await d3.csv(`../data/${this.circuit}/fastest_laps_${q.toLowerCase()}.csv`);
            }

            const extent_x = d3.extent(this.circuit_data, d => d.X)
            const extent_y = d3.extent(this.circuit_data, d => d.Y)

            // Declare the chart dimensions and margins.
            const marginTop = 20;
            const marginRight = 100;
            const marginBottom = 50;
            const marginLeft = 100;
            const width = 700;
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
                .x(d => this.x(d.X)).y(d => this.y(d.Y))

            // Create the SVG container.
            this.svg = d3.create("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("viewBox", [0, 0, width, height])
                .attr("style", "max-width: 100%; height: auto;")
                .on("mousemove", event => {
                    let [X, Y] = d3.pointer(event)
                    X = this.x.invert(X)
                    Y = this.y.invert(Y)

                    const point = { X, Y }
                    const closest = d3.least(this.circuit_data, d => this.calculateDistance(point, d))

                    const distance = Math.sqrt(this.calculateDistance(point, closest));

                    if (distance < 1000) {
                        // calls updateDistancePoint
                        this.distanceEvent({ X, Y })
                    }
                })

            const checkbox = document.getElementById('brakingCheckbox');
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    this.drawBrakingLines();
                } else {
                    // If checkbox is unchecked, remove braking lines
                    this.svg.selectAll('.braking-line').remove();
                    this.svg.selectAll('.legend-braking-line').remove();
                }
            });


            const length = (path) => d3.create("svg:path").attr("d", path).node().getTotalLength()
            const l = length(this.track(this.circuit_data));

            this.brakeLine = this.svg.append("g")

            this.svg.append("path")
                .datum(this.circuit_data)
                .attr("fill", "none")
                .attr("stroke", "black")
                .attr("stroke-width", 9)
                .attr("stroke-linejoin", "round")
                .attr("stroke-linecap", "round")
                .attr("stroke-dasharray", `0,${l}`)
                .attr("d", this.track)
                .transition()
                .duration(500)
                .ease(d3.easeLinear)
                .attr("stroke-dasharray", `${l},${l}`);


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
