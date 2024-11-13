<template>
    <div>
      <!-- Logo Section -->
      <div class="logo">FFA</div>
  
      <!-- Navigation Bar -->
      <nav class="navbar">
        <a href="/" class="nav-link">Home</a>
        <a href="/players" class="nav-link">Players</a>
        <a href="/teams" class="nav-link">Teams</a>
        <a href="/divisions" class="nav-link">Divisions</a>
      </nav>
    </div>
  </template>
  
  <script>
  export default {
    name: "NavBar",
  };
  </script>
  
  <style scoped>
  /* Logo Styling */
  .logo {
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
    background-color: #d32f2f; /* Red background */
    padding: 0.5rem 1rem;
    text-align: center;
  }
  
  /* Navbar Styling */
  .navbar {
    background-color: #333;
    padding: 1rem;
    display: flex;
    gap: 1rem;
    justify-content: center;
  }
  .nav-link {
    color: white;
    text-decoration: none;
    font-weight: bold;
  }
  .nav-link:hover {
    color: #ddd;
  }
  </style>
  