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
export default {
    props: {
        distance_highlight: {
            validator(value) {
                // check between 0 and max distance
                return true
            }
        }
    },
    watch: {
        distance_highlight: function (newVal, oldVal) {
            this.set_distance(newVal)
        }
    },
    async mounted() {
        await this.init()
        // this.set_drivers(["Carlos Sainz"])
    },
    methods: {
        set_distance(dist, pixel_space = false) {
            const i = d3.leastIndex(this.points, ([x, y]) => Math.abs(x - dist));
            let x;
            if (!pixel_space) {
                x = this.x(dist)
            } else {
                x = dist
            }
            this.distance_line
                .attr('x1', x)
                .attr('x2', x)
        },

        set_drivers(drivers) {
            let filtered_data = []
            for (const driver_data of this.data.values()) {
                if (drivers.includes(driver_data.full_name)) {
                    filtered_data.push(driver_data)
                }
            }

            this.driver_lines.selectAll("path")
                .data(filtered_data)
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
                    // x: parseFloat(d.X),
                    // y: parseFloat(d.Y),
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

            // Declare the scales
            this.x = d3.scaleLinear()
                .domain([0, d3.max(this.data_raw, d => d.dist)]).nice()
                .range([marginLeft, width - marginRight])

            this.y = d3.scaleLinear()
                .domain(d3.extent(this.data_raw, d => d.speed)).nice()
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
            this.svg.append("g")
                .attr("transform", `translate(${marginLeft},0)`)
                .call(d3.axisLeft(this.y));

            // compute poitns in pixel space [x, y, z] where z is the driver 
            this.points = this.data_raw.map(d => [this.x(d.dist), this.y(d.speed), d.full_name, d.team])

            // create map of driver name -> track points
            this.data = d3.rollup(this.points, v => Object.assign(v, { full_name: v[0][2], team: v[0][3] }), d => d[2])


            // draw distance line highlight
            this.distance_line = this.svg
                .append('line')
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
                .selectAll("path")
                .data(this.data.values())
                .join("path")
                .filter(d => d.full_name === "Carlos Sainz")
                .style("mix-blend-mode", "multiply")
                .attr("d", this.line)
                .style("stroke", d => colors[d.team])


            // Add an invisible layer for the interactive tip.
            this.dot = this.svg.append("g")
                .attr("display", "none");

            this.dot.append("circle")
                .attr("r", 2.5);

            this.dot.append("text")
                .attr("text-anchor", "middle")
                .attr("y", -8);



            this.svg
                .on("pointerenter", this.pointerentered)
                .on("pointermove", this.pointermoved)
                .on("pointerleave", this.pointerleft)
                .on("touchstart", event => event.preventDefault());

            container.append(this.svg.node())
        },

        pointermoved(event) {
            const [xm, ym] = d3.pointer(event);
            const [x, y, full_name] = d3.least(this.data.get("Carlos Sainz"), ([x, y]) => Math.hypot(x - xm, y - ym));
            this.driver_lines
                .style("stroke", (d) => d.full_name === full_name ? colors[d.team] : "#ddd")
                .filter(d => d.full_name === full_name).raise();
            this.dot.attr("transform", `translate(${x},${y})`);
            this.dot.select("text").text(full_name);
            this.svg.property("value", full_name).dispatch("input", { bubbles: true });
            this.set_distance(x, true);
        },

        pointerentered() {
            this.driver_lines.style("mix-blend-mode", null).style("stroke", "#ddd");
            this.dot.attr("display", null);
        },

        pointerleft() {
            this.driver_lines.style("mix-blend-mode", "multiply").style("stroke", d => colors[d.team]);
            this.dot.attr("display", "none");
            this.svg.node().value = null;
            this.svg.dispatch("input", { bubbles: true });
        }
    }
};
</script>
