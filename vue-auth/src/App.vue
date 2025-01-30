<template>
  <NavBar/>

  <main class="form-signin">
    <router-view/>
  </main>
</template>

<script>
import NavBar from "@/components/NavBar";
import 'normalize.css';

export default {
  components: {NavBar}
}
</script>

<style>
:root {
    --color-h2: rgba(0, 0, 0, 0.90);
    --h1-size: 3rem;
    --h2-size: 2rem;
    --color-h1: #757575;
    --color-lightblue: #E0DEFF;
    --color-white: #ffffff;
    --color-login: #E3E3E3;
    --color-lightGray:#e0e0e0;
    --color-black: #000;
    --color-button-hover: #6870D5;
    --color-background: #f3f4f6;
}

body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: var(--color-white);
}

h1 {
    font-size: var(--h1-size);
    color: var(--color-h1);
}

h2 {
    font-size: var(--h2-size);
}
</style>