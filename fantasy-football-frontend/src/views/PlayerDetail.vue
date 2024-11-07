<template>
    <div>
      <h1>{{ player.name }}</h1>
      <p>Position: {{ player.position }}</p>
      <p>Team: {{ player.team }}</p>
      <p>Fantasy Points: {{ player.fantasy_points }}</p>
    </div>
  </template>
  
  <script>
  import api from '../services/api';
  
  export default {
    props: ['id'],
    data() {
      return {
        player: {}
      };
    },
    async created() {
      try {
        const response = await api.get(`/players/${this.id}`);
        this.player = response.data;
      } catch (error) {
        console.error('Error fetching player:', error);
      }
    }
  };
  </script>
  