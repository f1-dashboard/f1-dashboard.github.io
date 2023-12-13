<template>
    <div id="menu">
        <span ref="Q1" @click="this.changeQuali('Q1')">Q1</span>
        <span ref="Q2" @click="this.changeQuali('Q2')">Q2</span>
        <span ref="Q3" @click="this.changeQuali('Q3')">Q3</span>
        <hr ref="underline" class="underline">
    </div>
</template>

<script>
export default {
    emits: ['QualiChanged'],
    mounted() {
        this.changeQuali('Q1')
    },
    methods: {
        changeQuali(q) {
            this.$emit('QualiChanged', q)

            // Move the line to the right by changing the transform property
            const targetSpan = this.$refs[q];
            const movingLine = this.$refs.underline;
            if (targetSpan && movingLine) {
                const targetPosition = targetSpan.offsetLeft;
                console.log(targetPosition)
                movingLine.style.left = targetPosition + 'px';
            }
        }
    }
}
</script>


<style scoped>
#menu>span {
    font-size: x-large;
    margin: 0 30px;
    cursor: pointer;
}

.underline {
    width: 2.5em;
    margin: 3px auto;
    color: red;
    background-color: red;
    height: 5px;
    position: absolute;
    transition: left 0.3s ease;
    left: 0;
    border-radius: 2px;
}
</style>