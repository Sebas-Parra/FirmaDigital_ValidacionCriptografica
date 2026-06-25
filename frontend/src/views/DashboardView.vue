<template>
  <div class="min-h-screen bg-white">

    <nav class="bg-indigo-950 text-white px-8 py-4 flex justify-between items-center">
      <div class="flex items-center gap-2.5">
        <svg class="w-4 h-4 text-indigo-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
        </svg>
        <span class="font-semibold tracking-tight">FirmaDigital</span>
      </div>
      <div class="flex items-center gap-5 text-sm">
        <router-link v-if="isAdmin" to="/admin" class="text-amber-400 hover:text-white transition-colors">Admin</router-link>
        <router-link to="/profile" class="text-indigo-300 hover:text-white transition-colors">{{ user.username }}</router-link>
        <button @click="logout" class="text-indigo-400 hover:text-white transition-colors">Salir</button>
      </div>
    </nav>

    <!-- Hero -->
    <div class="bg-gradient-to-b from-slate-50 to-white border-b border-gray-100 px-6 py-20 text-center">
      <h1 class="text-4xl font-bold text-gray-900 tracking-tight">Hola, {{ user.username }}</h1>
      <p class="text-gray-400 mt-3 text-base">Plataforma de firma digital y validación criptográfica</p>
    </div>

    <div class="max-w-3xl mx-auto px-6 py-14">

      <!-- Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-10">

        <div
          @click="$router.push('/documents')"
          class="group relative bg-white border border-gray-200 rounded-2xl p-8 cursor-pointer hover:border-indigo-200 hover:shadow-xl hover:-translate-y-1 transition-all duration-200 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-indigo-50/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-2xl"></div>
          <div class="relative flex flex-col items-center text-center">
            <div class="w-11 h-11 bg-indigo-50 border border-indigo-100 rounded-xl flex items-center justify-center mb-6">
              <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-1.5">Documentos</h3>
            <p class="text-sm text-gray-500 leading-relaxed">Sube, firma y verifica la integridad de documentos PDF</p>
          </div>
        </div>

        <div
          @click="$router.push('/certificates')"
          class="group relative bg-white border border-gray-200 rounded-2xl p-8 cursor-pointer hover:border-indigo-200 hover:shadow-xl hover:-translate-y-1 transition-all duration-200 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-indigo-50/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-2xl"></div>
          <div class="relative flex flex-col items-center text-center">
            <div class="w-11 h-11 bg-indigo-50 border border-indigo-100 rounded-xl flex items-center justify-center mb-6">
              <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-1.5">Certificados</h3>
            <p class="text-sm text-gray-500 leading-relaxed">Genera y administra certificados digitales X.509</p>
          </div>
        </div>

      </div>

      <!-- Tech stack pills -->
      <div class="flex items-center justify-center gap-2.5 flex-wrap">
        <div class="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-full px-3.5 py-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          <span class="text-xs font-medium text-gray-600">SHA-256</span>
          <span class="text-xs text-gray-400">integridad</span>
        </div>
        <div class="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-full px-3.5 py-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
          <span class="text-xs font-medium text-gray-600">AES-256-GCM</span>
          <span class="text-xs text-gray-400">cifrado</span>
        </div>
        <div class="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-full px-3.5 py-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-violet-500"></span>
          <span class="text-xs font-medium text-gray-600">RSA-2048</span>
          <span class="text-xs text-gray-400">firma</span>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardView',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}')
    }
  },
  computed: {
    isAdmin() {
      return ['admin', 'superuser'].includes(this.user.role)
    }
  },
  created() {
    if (!localStorage.getItem('token')) {
      this.$router.push('/login')
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    }
  }
}
</script>
