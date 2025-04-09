<script lang="ts">
  import { goto } from '$app/navigation';

  let email = '';
  let password = '';
  let error = '';

  async function login() {
    const res = await fetch(`http://localhost/register_user`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!res.ok) {
      error = (await res.json()).detail;
      return;
    }

    const { token } = await res.json();
    localStorage.setItem('token', token);
    goto('/');
  }
</script>

<form on:submit|preventDefault={login}>
  <input type="email" bind:value={email} required />
  <input type="password" bind:value={password} required />
  <button type="submit">Регистрация</button>
  {#if error}<p>{error}</p>{/if}
</form>
