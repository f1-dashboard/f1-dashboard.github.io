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
        this.updateLinePosition('Q1');
        window.addEventListener('resize', this.handleResize);

        setTimeout(() => {
            this.changeQuali('Q1');
        }, 50);
    },
    beforeDestroy() {
        window.removeEventListener('resize', this.handleResize);
    },
    methods: {
        changeQuali(q) {
            this.$emit('QualiChanged', q);
            this.updateLinePosition(q);
        },
        handleResize() {
            const currentQuali = this.$refs.underline.dataset.currentQuali;
            this.updateLinePosition(currentQuali);
        },
        updateLinePosition(q) {
            const targetSpan = this.$refs[q];
            const movingLine = this.$refs.underline;

            if (targetSpan && movingLine) {
                const targetPosition = targetSpan.offsetLeft;
                movingLine.style.left = targetPosition + 'px';
                movingLine.style.transition = 'left 0.2s ease';
                movingLine.style.display = 'grid';
                movingLine.dataset.currentQuali = q;
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
    font-family: 'formula1';
}

.underline {
    width: 2.5em;
    margin: 3px auto;
    color: red;
    background-color: red;
    height: 5px;
    position: absolute;
    left: 0;
    display: none;
    border-radius: 2px;
}
</style>