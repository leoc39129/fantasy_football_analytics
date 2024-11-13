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

// Navigation guard to reload the home page
router.beforeEach((to, from, next) => {
  if (to.path === '/' && from.path !== '/') {
    // Reload the page when navigating to the home page from another route
    window.location.reload();
  } else {
    next();
  }
});

export default router;
