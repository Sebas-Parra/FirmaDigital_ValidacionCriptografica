<template>
  <aside class="bg-emerald-950 w-52 h-screen sticky top-0 flex flex-col py-6 px-3 shrink-0">

    <!-- Brand -->
    <div class="flex items-center gap-2.5 px-3 mb-8">
      <svg class="w-4 h-4 text-emerald-300 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
      </svg>
      <span class="text-white font-semibold tracking-tight text-sm">FirmaDigital</span>
    </div>

    <!-- Nav principal -->
    <nav class="flex flex-col gap-0.5 flex-1">
      <router-link to="/dashboard" :class="linkClass('/dashboard')">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
        </svg>
        Dashboard
      </router-link>

      <router-link to="/documents" :class="linkClass('/documents')">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        Documentos
      </router-link>

      <router-link to="/certificates" :class="linkClass('/certificates')">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/>
        </svg>
        Certificados
      </router-link>

      <router-link v-if="isAdmin" to="/admin" :class="linkClass('/admin', true)">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
        </svg>
        <span :class="$route.path.startsWith('/admin') ? 'text-amber-300' : 'text-amber-400'">Admin</span>
      </router-link>
    </nav>

    <!-- Perfil + salir -->
    <div class="border-t border-emerald-800 pt-3 flex flex-col gap-0.5">
      <router-link to="/profile" :class="linkClass('/profile')">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
        </svg>
        <span class="truncate">{{ user.username }}</span>
      </router-link>

      <button @click="logout" class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-emerald-300 hover:bg-emerald-900 hover:text-white transition-colors w-full text-left">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
        </svg>
        Salir
      </button>
    </div>

  </aside>
</template>

<script>
export default {
  name: 'AppSidebar',
  computed: {
    user() {
      return JSON.parse(localStorage.getItem('user') || '{}')
    },
    isAdmin() {
      return ['admin', 'superuser'].includes(this.user.role)
    }
  },
  methods: {
    linkClass(path) {
      const active = this.$route.path.startsWith(path)
      const base = 'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors'
      return active
        ? `${base} bg-emerald-900 text-white`
        : `${base} text-emerald-300 hover:bg-emerald-900 hover:text-white`
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    }
  }
}
</script>
