import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: () => import('../views/Dashboard.vue')
    },
    {
      path: '/teams',
      name: 'Teams',
      component: () => import('../views/Teams.vue')
    },
    {
      path: '/players',
      name: 'Players',
      component: () => import('../views/Players.vue')
    },
    {
      path: '/prediction',
      name: 'Prediction',
      component: () => import('../views/Prediction.vue')
    }
  ]
})

export default router
