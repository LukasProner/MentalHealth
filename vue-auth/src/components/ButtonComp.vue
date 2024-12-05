<template>
    <button class="custom-button">
      {{ text }}
    </button>
  </template>
  
  <script>
  export default {
    name: 'ButtonComp',
    props: {
      text: {
        type: String,
        required: true
      }
    }
  }
  </script>
  
  <style scoped>
  .custom-button{
    background-color: var(--color-lightblue);
    color: var(--color-h1);
    border: 1px solid var(--color-h2);
    padding: 10px 20px;
    font-size: 1.5rem;
    font-weight: bold;
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.3s, box-shadow 0.3s, transform 0.2s;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
}

.custom-button:hover {
    background-color: var(--color-button-hover);
    color: var(--color-white);
}
@media (max-width: 768px) {
    .custom-button{
        font-size: 1.2rem;
    }
}
</style>
  