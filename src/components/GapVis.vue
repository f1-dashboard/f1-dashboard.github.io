<template>
    <div>
        <h2>Gap</h2>
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
            validator(value) {
                // check between 0 and max distance
                return true
            }
        },
        drivers: {
            validator(value) {
                // check valid driver name
                return true
            }
        },
        relative: {
            default: false
        }
    },
    watch: {
        distance_highlight: function (newVal, oldVal) {
            this.set_distance(newVal)
        },
        drivers: function (newVal, oldVal) {
            this.set_drivers(newVal)
        }
    },
    async mounted() {
        await this.init()
        // this.drivers = ["Carlos Sainz", "Lance Stroll"]
        this.set_drivers(["Carlos Sainz", "Lance Stroll"])
    },
    methods: {
        set_relative_to(driver) {

        },

        // Update the line + dots visualization based on x value
        set_distance(dist, pixel_space = false) {
            let xm;
            if (!pixel_space) {
                xm = this.x(dist)
            } else {
                xm = dist
            }


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
            if (!this.data) {
                return
            }
            // compute gap
            let maxGap = 0.1

            this.relative_data_px = new Map()
            for (let i = 0; i < drivers.length; i++) {
                const this_max_dist = d3.max(this.data.get(drivers[i]).map(d => d[0]))

                const relativeSpeedCurve = this.data.get(drivers[i]).map(d => {
                    const gap = this.get_interpolated_time(drivers[0], d[0]) - d[1]

                    if (gap > maxGap) {
                        maxGap = gap
                    } else if (gap < -maxGap) {
                        maxGap = -gap
                    }

                    // convert to pixel space
                    return [this.x(d[0]), this.y(gap)]
                })

                relativeSpeedCurve["full_name"] = drivers[i]
                relativeSpeedCurve["team"] = this.data.get(drivers[i]).team

                this.relative_data_px.set(drivers[i], relativeSpeedCurve)
            }

            this.y.domain([-maxGap, maxGap])

            this.gy.call(d3.axisLeft(this.y));

            this.lines
                .selectAll("path")
                .data(this.relative_data_px.values())
                .join("path")
                .style("mix-blend-mode", "multiply")
                .attr("d", this.line)
                .style("stroke", d => colors[d.team])
        },

        async init() {
            // Load data
            this.data_raw = await d3.csv("../data/monza_2023_fastest_laps.csv", d => {
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
            const marginBottom = 30;
            const marginLeft = 30;
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
            this.set_distance(xm, true)
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
