<template>
    <div id="menu">
        <span ref="Q1" @click="this.changeQuali('Q1')">Q1</span>
        <span ref="Q2" @click="this.changeQuali('Q2')">Q2</span>
        <span ref="Q3" @click="this.changeQuali('Q3')">Q3</span>
        <!-- <hr ref="underline" class="underline"> -->
    </div>
</template>

<script>
export default {
    emits: ['QualiChanged'],
    methods: {
        changeQuali(q) {
            this.$emit('QualiChanged', q)

            // Move the line to the right by changing the transform property
            const targetSpan = this.$refs[q];
            const movingLine = this.$refs.underline;
            if (targetSpan && movingLine) {
                const targetPosition = targetSpan.offsetLeft + targetSpan.offsetWidth / 2;
                console.log(targetPosition)
                movingLine.style.transition = 'left 0.3s ease';
                movingLine.style.left = targetPosition + 'px';
            }
        }
    }
}
</script>


<style scoped>
#menu>span {
    font-size: x-large;
    margin: 0 10px;
    cursor: pointer;
}

.underline {
    width: 2.5em;
    /* Adjust the width as needed */
    margin: 3px auto;
    /* Adjust the top and bottom margins to control the position */
    color: red;
    /* Line color */
    background-color: red;
    /* Line color for older browsers */
    height: 5px;
    /* Line thickness */
    /* transition: transform 0.3s ease; */
    position: relative;
    transition: left 0.3s ease;
    left: 0;
    /* Smooth transition for the transform property */
}
</style>