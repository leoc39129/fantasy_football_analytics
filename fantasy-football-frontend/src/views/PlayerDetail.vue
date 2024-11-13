<template>
  <div>
    <!-- Logo, Navigation Bar Component -->
    <NavBar/>

    <!-- Player Detail Header -->
    <h1>{{ player.name }}</h1>

    <!-- Player Details Table -->
    <table class="player-detail-table">
      <tbody>
        <tr>
          <th>Position</th>
          <td>{{ player.position }}</td>
        </tr>
        <tr>
          <th>Team</th>
          <td>{{ player.team }}</td>
        </tr>
        <tr>
          <th>Fantasy Points</th>
          <td>{{ player.fantasy_points }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import api from '../services/api';

export default {
  name: "PlayerDetail",
  components: {
    NavBar,
  },
  props: ["id"],
  data() {
    return {
      player: {},
    };
  },
  async created() {
    try {
      const response = await api.get(`/players/${this.id}`);
      this.player = response.data;
    } catch (error) {
      console.error("Error fetching player details:", error);
    }
  },
};
</script>

<style scoped>

/* Page Header */
h1 {
  font-size: 1.8rem;
  margin-top: 1rem;
  text-align: center;
}

/* Table Styling for Player Details */
.player-detail-table {
  width: 50%;
  margin: 1rem auto;
  border-collapse: collapse;
}
.player-detail-table th,
.player-detail-table td {
  padding: 0.75rem;
  text-align: left;
  border: 1px solid #ddd;
}
.player-detail-table th {
  background-color: #333;
  color: white;
  font-weight: bold;
  width: 30%;
}
.player-detail-table td {
  background-color: #f9f9f9;
}
</style>
