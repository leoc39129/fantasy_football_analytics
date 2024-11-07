<template>
  <div>
    <h1>All Players</h1>
    <ul>
      <li v-for="player in players" :key="player.id">
        {{ player.name }} - {{ player.position }} - {{ player.team }} - {{ player.fantasy_points }}
      </li>
    </ul>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: "PlayersView",
  data() {
    return {
      players: [],  // Data to store players fetched from the API
    };
  },
  async created() {
    try {
      // Fetch players from the backend
      const response = await api.get('/players');
      this.players = response.data;  // Store fetched data in the component's data
    } catch (error) {
      console.error("Error fetching players:", error);
    }
  },
};
</script>

<style scoped>
/* Add any styling you need here */
</style>
