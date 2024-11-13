<template>
  <div>
    <!-- Logo, Navigation Bar Component -->
    <NavBar />

    <!-- Page Header -->
    <h1>All Players</h1>

    <!-- Player Data Table -->
    <table class="player-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Position</th>
          <th>Team</th>
          <th>Fantasy Points</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="player in players" :key="player.id">
          <td>
            <router-link :to="{ name: 'PlayerDetail', params: { id: player.id } }">
              {{ player.name }}
            </router-link>
          </td>
          <td>{{ player.position }}</td>
          <td>{{ player.team }}</td>
          <td>{{ player.fantasy_points }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
/*
SOME NOTES FOR THE FUTURE

1. Be able to sort the table (requery data)
2. Hyperlink each player's detail view page to their name (or the entire row)
3. Add filtering by position, team, and division (add division)
4. Add search for a player's name
5. 

*/
import api from '../services/api';
import NavBar from '../components/NavBar.vue'

export default {
  name: "PlayersView",
  components: {
    NavBar,
  },
  data() {
    return {
      players: [],
    };
  },
  async created() {
    try {
      const response = await api.get('/players');
      this.players = response.data;
    } catch (error) {
      console.error("Error fetching players:", error);
    }
  },
};
</script>

<style scoped>
/* Font Setup */
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');

body {
  font-family: 'Open Sans', sans-serif;
}

/* Page Header */
h1 {
  font-size: 1.8rem;
  margin-top: 1rem;
  text-align: center;
}

/* Table Styling */
.player-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
.player-table th,
.player-table td {
  padding: 0.75rem;
  text-align: left;
  border: 1px solid #ddd;
}
.player-table th {
  background-color: #333;
  color: white;
  font-weight: bold;
}
.player-table tr:nth-child(even) {
  background-color: #f9f9f9;
}
</style>
