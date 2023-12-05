<template>
    <div>
        <h2>Monza Circuit</h2>
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

function linearInterpolate(x, p0, p1) {
    const t = (x - p0[4]) / (p1[4] - p0[4]);
    return p0[5] + t * (p1[5] - p0[5]);
}

function cubicBezierInterpolation(x, p0, p1, p2, p3) {
    const t = (x - p0[4]) / (p3[4] - p0[4]);
    const u = 1 - t;
    const tt = t * t;
    const uu = u * u;
    const uuu = uu * u;
    const ttt = tt * t;

    const p = [];
    p[4] = uuu * p0[4] + 3 * uu * t * p1[4] + 3 * u * tt * p2[4] + ttt * p3[4];
    p[5] = uuu * p0[5] + 3 * uu * t * p1[5] + 3 * u * tt * p2[5] + ttt * p3[5];

    return p[5];
}


export default {
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
            this.set_drivers(neVal)
        }
    },
    async mounted() {
        await this.init()
        this.set_drivers(["Lewis Hamilton"])
        this.set_drivers(["Carlos Sainz", "Max Verstappen"])
        if (this.relative) {
            this.set_relative_to("Carlos Sainz")
        }
    },
    methods: {
        set_relative_to(driver) {
            this.y.domain([-20, 20]).nice()
            this.gy.call(d3.axisLeft(this.y))

            let relative_data = new Map()
            for (const [name, driver_data] of this.filtered_data) {
                let data = new Array()
                for (const point of driver_data) {
                    const [x, y, name, team, dist, speed] = point
                    // get the interpolated dist, speed from the relative drive
                    const relativeSpeed = this.get_interpolated_speed(driver, dist) - speed
                    data.push([x, this.y(relativeSpeed)])
                }
                data["full_name"] = name
                data["team"] = driver_data.team
                relative_data.set(name, data)
            }
            console.log(relative_data.values().next())
            console.log(this.filtered_data.values().next())

            this.driver_lines
                .selectAll("path")
                .data(relative_data.values())
                .join("path")
                .style("mix-blend-mode", "multiply")
                .attr("d", this.line)
                .style("stroke", d => colors[d.team])
        },

        get_interpolated_speed(driver, dist) {
            // filtered data is array of [x (pixel space), y (pixel space), full_name, team, dist, speed]
            const data = this.filtered_data.get(driver)
            let i = 0;
            while (i < data.length && data[i][4] < dist) {
                i++;
            }

            if (i === 0) {
                return data[0][1];
            }
            if (i === data.length) {
                return data[data.length - 1][1];
            }
            if (i === data.length - 1 || i === 1) {
                return linearInterpolate(dist, data[i - 1], data[i])
            }

            return cubicBezierInterpolation(dist, data[i - 2], data[i - 1], data[i], data[i + 1]);
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
            for (const [driver, data] of this.filtered_data.entries()) {
                const [x, y, full_name, team] = d3.least(data, horizontal_distance);
                this.dots.append("circle")
                    .attr("r", 4)
                    .attr("transform", `translate(${x},${y})`)
                    .attr("fill", colors[team])

                const textNode = this.dots.append("text")
                    .text(full_name)
                    .attr("fill", colors[team]);

                y_positions.push([y, textNode])

                this.svg.property("value", full_name).dispatch("input", { bubbles: true });
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

        set_drivers(drivers) {
            this.filtered_data = new Map();
            for (const driver_data of this.pixel_data.values()) {
                if (drivers.includes(driver_data.full_name)) {
                    this.filtered_data.set(driver_data.full_name, driver_data)
                }
            }

            this.driver_lines
                .selectAll("path")
                .data(this.filtered_data.values())
                .join("path")
                .style("mix-blend-mode", "multiply")
                .attr("d", this.line)
                .style("stroke", d => colors[d.team])
        },

        async init() {
            // Load data
            this.data_raw = await d3.csv("../data/monza_2023_fastest_laps.csv", d => {
                let driver = {
                    full_name: d.FullName,
                    team: d.TeamId,
                    dist: parseFloat(d.Distance),
                    speed: parseFloat(d.Speed),
                };
                return driver
            });

            // Declare the chart dimensions and margins.
            const marginTop = 20;
            const marginRight = 20;
            const marginBottom = 30;
            const marginLeft = 30;
            const width = 640;
            const height = 400;

            this.maxX = d3.max(this.data_raw, d => d.dist)
            // Declare the scales
            this.x = d3.scaleLinear()
                .domain([0, this.maxX]).nice()
                .range([marginLeft, width - marginRight])

            this.y = d3.scaleLinear()
                // .domain(d3.extent(this.data_raw, d => d.speed)).nice()
                .domain([0, d3.max(this.data_raw, d => d.speed)]).nice()
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

            // compute poitns in pixel space [x, y, z] where z is the driver 
            this.points = this.data_raw.map(d => [this.x(d.dist), this.y(d.speed), d.full_name, d.team, d.dist, d.speed])

            // create map of driver name -> track points
            this.pixel_data = d3.rollup(this.points, v => Object.assign(v, { full_name: v[0][2], team: v[0][3] }), d => d[2])

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
            this.driver_lines = this.svg.append("g")
                .attr("fill", "none")
                .attr("stroke-width", 1.5)
                .attr("stroke-linejoin", "round")
                .attr("stroke-linecap", "round")


            // Add an invisible layer for the interactive tip.
            this.dots = this.svg.append("g")
                .attr("display", "none");



            this.svg
                .on("pointermove", this.pointermoved)
                .on("pointerenter", this.showDistanceLine)
                // .on("pointerleave", this.hideDistanceLine)
                .on("touchstart", event => event.preventDefault());

            container.append(this.svg.node())
        },

        // Update dots
        pointermoved(event) {
            const [xm, ym] = d3.pointer(event);

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
