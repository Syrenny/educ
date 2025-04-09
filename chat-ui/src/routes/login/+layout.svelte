<!-- routes/login/+layout.svelte -->
<script lang="ts">
  // Вы можете добавить сюда общую логику для страницы входа, если нужно
</script>

<style>
  main {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f5f5f5;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  input {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  button {
    padding: 0.75rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  button:hover {
    background-color: #0056b3;
  }

  p {
    color: red;
    font-size: 0.9rem;
  }
</style>

<main>
  <slot></slot> <!-- Здесь будет рендериться ваша страница с формой входа -->
</main>
