<template>
    <div>
        <h2>Time gap between drivers</h2>
        <div id="container"></div>
    </div>
</template>

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

// Parse the duration string, e.g. "0 days 00:01:20.643000"
function parseTimeString(ts) {
    const durationArray = ts.split(" ");

    // Extract days, hours, minutes, seconds, and milliseconds
    const days = parseInt(durationArray[0]);
    const timeComponents = durationArray[2].split(":");
    const hours = parseInt(timeComponents[0]);
    const minutes = parseInt(timeComponents[1]);
    const secondsArray = timeComponents[2].split(".");
    const seconds = parseInt(secondsArray[0]);
    const milliseconds = parseInt(secondsArray[1]) / 1000;
    return {
        time: hours * 3600 + minutes * 60 + seconds + milliseconds / 1000,
        time_string: `${minutes}:${seconds}.${milliseconds}`,
    }
}


export default {
    emits: ['DistanceChanged'],
    props: {
        distance_highlight: {
            default: 0
        },
        drivers: {
            default: "Max Verstappen"
        },
        relative: {
            default: false
        },
        circuit: {
            default: 1
        }
    },
    watch: {
        distance_highlight: function (newVal, oldVal) {
            this.set_distance(newVal)
        },
        drivers: function (newVal, oldVal) {
            // Don't listen to driver updates if data hasn't been loaded
            if (!this.data) {
                return
            }
            this.set_drivers(newVal)
            this.set_distance(this.distance_highlight)
        },
        circuit: async function (newVal, oldVal) {
            await this.init()
            this.set_drivers(this.drivers)
            this.set_distance(this.distance_highlight)
        }
    },
    async mounted() {
        await this.init()
    },
    methods: {
        // Update the line + dots visualization based on x value
        set_distance(dist) {
            let clamped = Math.max(0, Math.min(dist, this.maxX))
            let xm = this.x(clamped)

            // Change line
            this.distance_line
                .attr('x1', xm)
                .attr('x2', xm)

            // Change dots
            const horizontal_distance = ([x, y]) => Math.abs(x - xm)
            this.dots.selectAll("circle").remove()
            this.dots.selectAll("text").remove()

            let y_positions = []
            for (const [driver_name, driver] of this.relative_data_px.entries()) {
                const [x, y] = d3.least(driver, horizontal_distance);

                this.dots.append("circle")
                    .attr("r", 4)
                    .attr("transform", `translate(${x},${y})`)
                    .attr("fill", colors[driver.team])

                // const textNode = this.dots.append("text")
                //     .text(driver.full_name)
                //     .attr("fill", colors[driver.team]);

                // y_positions.push([y, textNode])

                this.svg.property("value", driver.full_name).dispatch("input", { bubbles: true });
            }

            // Change y positions so names aren't overlapping
            const min_dist = 20;
            for (let i = 0; i < y_positions.length; i++) {
                let [y, node] = y_positions[i]
                node.attr("transform", `translate(${xm},${y})`)
                    .attr("y", 2);

                if (i % 2 === 0) {
                    node.attr("text-anchor", "start")
                        .attr("x", 8)
                } else {
                    node.attr("text-anchor", "end")
                        .attr("x", -8)
                }
            }
        },

        get_interpolated_time(driver, dist) {
            const data = this.data.get(driver)
            let i = 0;
            while (i < data.length && data[i][0] < dist) {
                i++;
            }

            if (i === 0) {
                return data[0][1];
            }
            if (i === data.length) {
                return data[data.length - 1][1];
            }
            const p0 = data[i - 1];
            const p1 = data[i];
            const t = (dist - p0[0]) / (p1[0] - p0[0]);
            return p0[1] + t * (p1[1] - p0[1]);
        },

        set_drivers(drivers) {
            // compute gap between drivers
            let maxGap = 0.1
            this.relative_data_px = new Map()
            for (let i = 0; i < drivers.length; i++) {
                if (this.data.get(drivers[i]) === undefined) {
                    console.warn(`Driver ${drivers[i]} not in data`)
                    continue
                }
                const gapData = this.data.get(drivers[i]).map(d => {
                    const gap = this.get_interpolated_time(drivers[0], d[0]) - d[1]

                    if (gap > maxGap) {
                        maxGap = gap
                    } else if (gap < -maxGap) {
                        maxGap = -gap
                    }

                    return [d[0], gap]
                })

                this.relative_data_px.set(drivers[i], gapData)
            }

            maxGap += 0.2
            this.y.domain([-maxGap, maxGap])

            // convert gap data to pixel space
            for (const driver of this.relative_data_px) {
                const gapPXdata = this.relative_data_px.get(driver[0]).map(([x, y]) => [this.x(x), this.y(y)])
                gapPXdata["full_name"] = driver[0]
                gapPXdata["team"] = this.data.get(driver[0]).team
                this.relative_data_px.set(driver[0], gapPXdata)
            }

            const t = this.svg.transition().duration(750)

            this.gy
                .transition(t)
                .call(d3.axisLeft(this.y));

            this.lines
                .selectAll("path")
                .data(this.relative_data_px.values())
                .join("path")
                .style("mix-blend-mode", "multiply")
                .transition(t)
                .attr("d", this.line)
                .style("stroke", d => colors[d.team])
        },

        async init() {
            // Clear existing SVG element (if any)
            d3.select('#container').selectAll('svg').remove();

            // Load data
            this.data_raw = await d3.csv("../data/" + this.circuit + "/fastest_laps.csv", d => {
                const time = parseTimeString(d.Time).time

                if (!time) {
                    return null
                }
                let driver = {
                    full_name: d.FullName,
                    team: d.TeamId,
                    dist: parseFloat(d.Distance),
                    time: time ? time : 0,
                };

                return driver
            });

            // Roll up data as a mapping between driver -> array of (dist, speed)
            // the array also contains properites full_name and team
            this.data = d3.rollup(this.data_raw, v => {
                const full_name = v[0].full_name
                const team = v[0].team
                return Object.assign(v.map(d => [d.dist, d.time]), { full_name, team })
            }, d => d.full_name)

            // Declare the chart dimensions and margins.
            const marginTop = 20;
            const marginRight = 20;
            const marginBottom = 40;
            const marginLeft = 40;
            const width = 640;
            const height = 250;

            this.maxX = d3.max(this.data_raw, d => d.dist)
            // Declare the scales
            this.x = d3.scaleLinear()
                .domain([0, this.maxX]).nice()
                .range([marginLeft, width - marginRight])

            this.y = d3.scaleLinear()
                .domain([-3, +3]).nice()
                .range([height - marginBottom, marginTop])

            // Create the SVG container.
            this.svg = d3.create("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("viewBox", [0, 0, width, height])
                .attr("style", "max-width: 100%; height: auto;overflow: visible; font: 10px sans-serif;")

            // Add the x-axis.
            this.svg.append("g")
                .attr("transform", `translate(0,${height - marginBottom})`)
                .call(d3.axisBottom(this.x));

            // Add the y-axis.
            this.gy = this.svg.append("g")
                .attr("transform", `translate(${marginLeft},0)`)
                .call(d3.axisLeft(this.y));

            // draw distance line highlight
            this.distance_line = this.svg
                .append('line')
                .attr("display", "none")
                .attr('x1', 300)
                .attr('y1', height - marginBottom)
                .attr('x2', 300)
                .attr('y2', 0 + marginTop)
                .style("stroke-width", 2)
                .style("stroke", "#ddd")
                .style("stroke-dasharray", "4")
                .style("fill", "none");

            // draw driver lines
            this.line = d3.line();
            this.lines = this.svg.append("g")
                .attr("fill", "none")
                .attr("stroke-width", 1.5)
                .attr("stroke-linejoin", "round")
                .attr("stroke-linecap", "round")

            // Axis Labels
            this.svg.append("text")
                .attr("class", "x label")
                .attr("text-anchor", "end")
                .attr("x", width - 10)
                .attr("y", height - 10)
                .text("distance along track (m)");

            this.svg.append("text")
                .attr("class", "y label")
                .attr("text-anchor", "end")
                .attr("y", 6)
                .attr("x", -10)
                .attr("transform", "rotate(-90)")
                .text("gap (s)");

            // Add an invisible layer for the interactive tip.
            this.dots = this.svg.append("g")
                .attr("display", "none");

            this.svg
                .on("pointermove", this.pointermoved)
                // .on("pointerenter", this.showDistanceLine)
                // .on("pointerleave", this.hideDistanceLine)
                .on("touchstart", event => event.preventDefault());

            this.showDistanceLine()

            container.append(this.svg.node())
        },

        // Update dots
        pointermoved(event) {
            const [xm, ym] = d3.pointer(event);

            this.$emit('DistanceChanged', this.x.invert(xm))
            this.set_distance(this.x.invert(xm))
        },

        showDistanceLine() {
            this.dots.attr("display", null);
            this.distance_line.attr("display", null)
        },

        hideDistanceLine() {
            this.dots.attr("display", "none");
            this.distance_line.attr("display", "none")

            this.svg.node().value = null;
            this.svg.dispatch("input", { bubbles: true });
        }
    }
};
</script>
