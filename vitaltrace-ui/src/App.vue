<template>
  <component :is="isPublicRoute ? 'div' : DefaultLayout">
    <router-view />
    <ChatBot />
  </component>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DefaultLayout from './layouts/DefaultLayout.vue'
import ChatBot from '@/components/ChatBot.vue'

const route = useRoute()

const isPublicRoute = computed(() => route.meta.public === true)
</script>
