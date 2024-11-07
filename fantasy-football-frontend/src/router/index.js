// src/router/index.js

import { createRouter, createWebHistory } from 'vue-router';
import PlayersView from '../views/PlayersView.vue';
import PlayerDetail from '../views/PlayerDetail.vue';

const routes = [
  { path: '/', name: 'Players', component: PlayersView },
  { path: '/player/:id', name: 'PlayerDetail', component: PlayerDetail, props: true }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
