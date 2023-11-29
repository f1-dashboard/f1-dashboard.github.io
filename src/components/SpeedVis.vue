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
        point_distance: {
            validator(value) {
                return true
            }
        }
    },
    watch: {
        point_distance: function (newVal, oldVal) {
            this.set_distance(newVal)
        }
    },
    async mounted() {
        await this.init()
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


        async init() {
            // Load data
            this.data = await d3.csv("../data/monza_2023_fastest_laps.csv", d => {
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
                .domain([0, d3.max(this.data, d => d.dist)]).nice()
                .range([marginLeft, width - marginRight])

            this.y = d3.scaleLinear()
                .domain(d3.extent(this.data, d => d.speed)).nice()
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
            this.points = this.data.map(d => [this.x(d.dist), this.y(d.speed), d.full_name, d.team])

            // group points by driver 
            const groups = d3.rollup(this.points, v => Object.assign(v, { full_name: v[0][2], team: v[0][3] }), d => d[2])

            // draw distance line
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

            // draw lines
            const line = d3.line();
            this.path = this.svg.append("g")
                .attr("fill", "none")
                .attr("stroke-width", 1.5)
                .attr("stroke-linejoin", "round")
                .attr("stroke-linecap", "round")
                .selectAll("path")
                .data(groups.values())
                .join("path")
                .style("mix-blend-mode", "multiply")
                .attr("d", line)
                .style("stroke", d => colors[d.team])


            // Add an invisible layer for the interactive tip.
            this.dot = this.svg.append("g")
                .attr("display", "none");

            this.dot.append("circle")
                .attr("r", 2.5);

            this.dot.append("text")
                .attr("text-anchor", "middle")
                .attr("y", -8);



            const pointermoved = (event) => {
                const [xm, ym] = d3.pointer(event);
                const i = d3.leastIndex(this.points, ([x, y]) => Math.hypot(x - xm, y - ym));
                const [x, y, full_name] = this.points[i];
                this.path.style("stroke", (d) => d.full_name === full_name ? colors[d.team] : "#ddd").filter(d => d.full_name === full_name).raise();
                this.dot.attr("transform", `translate(${x},${y})`);
                this.dot.select("text").text(full_name);
                this.svg.property("value", this.data[i]).dispatch("input", { bubbles: true });
                this.set_distance(x, true);
            }

            const pointerentered = () => {
                this.path.style("mix-blend-mode", null).style("stroke", "#ddd");
                this.dot.attr("display", null);
            }

            const pointerleft = () => {
                this.path.style("mix-blend-mode", "multiply").style("stroke", d => colors[d.team]);
                this.dot.attr("display", "none");
                this.svg.node().value = null;
                this.svg.dispatch("input", { bubbles: true });
            }

            this.svg
                .on("pointerenter", pointerentered)
                .on("pointermove", pointermoved)
                .on("pointerleave", pointerleft)
                .on("touchstart", event => event.preventDefault());

            container.append(this.svg.node())
        },
    }
};
</script>
