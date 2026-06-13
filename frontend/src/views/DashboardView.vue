<template>
  <div class="min-h-screen bg-gray-100">

    <!-- Navbar -->
    <nav class="bg-indigo-900 text-white px-6 py-4 flex justify-between items-center shadow-lg">
      <div class="flex items-center gap-2">
        <span class="text-2xl">🔐</span>
        <span class="font-bold text-lg">FirmaDigital</span>
      </div>
      <div class="flex items-center gap-4">
        <span class="text-sm text-indigo-200">{{ user.username }} 
          <span class="bg-indigo-700 px-2 py-0.5 rounded-full text-xs ml-1">{{ user.role }}</span>
        </span>
        <button @click="logout"
          class="bg-white/10 hover:bg-white/20 text-white text-sm px-4 py-1.5 rounded-lg transition-all border border-white/20">
          Cerrar sesión
        </button>
      </div>
    </nav>

    <!-- Content -->
    <div class="max-w-5xl mx-auto px-6 py-8">

      <!-- Welcome -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-indigo-900">Bienvenido, {{ user.username }} 👋</h2>
        <p class="text-gray-500 mt-1">Plataforma de firma digital y validación criptográfica</p>
      </div>

      <!-- Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">

        <div class="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-all cursor-pointer" 
          @click="$router.push('/documents')">
          <div class="text-4xl mb-4">📄</div>
          <h3 class="font-semibold text-indigo-900 text-lg mb-1">Documentos</h3>
          <p class="text-gray-500 text-sm mb-4">Sube y firma documentos digitalmente con SHA-256 y RSA</p>
          <span class="text-xs bg-green-50 text-green-600 px-3 py-1 rounded-full">Disponible</span>
        </div>

        <div class="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-all cursor-pointer" 
          @click="$router.push('/certificates')">
          <div class="text-4xl mb-4">🏆</div>
          <h3 class="font-semibold text-indigo-900 text-lg mb-1">Certificados</h3>
          <p class="text-gray-500 text-sm mb-4">Gestiona tus certificados digitales X.509</p>
          <span class="text-xs bg-green-50 text-green-600 px-3 py-1 rounded-full">Disponible</span>
        </div>

        <div class="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-all">
          <div class="text-4xl mb-4">🔒</div>
          <h3 class="font-semibold text-indigo-900 text-lg mb-1">Cifrado AES</h3>
          <p class="text-gray-500 text-sm mb-4">Cifra y descifra archivos con AES-256-GCM</p>
          <span class="text-xs bg-indigo-50 text-indigo-600 px-3 py-1 rounded-full">Sprint 3</span>
        </div>

        <div class="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-all">
          <div class="text-4xl mb-4">✍️</div>
          <h3 class="font-semibold text-indigo-900 text-lg mb-1">Firma Digital</h3>
          <p class="text-gray-500 text-sm mb-4">Firma documentos con RSA y verifica autenticidad</p>
          <span class="text-xs bg-indigo-50 text-indigo-600 px-3 py-1 rounded-full">Sprint 3</span>
        </div>

        <div class="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-all">
          <div class="text-4xl mb-4">🔍</div>
          <h3 class="font-semibold text-indigo-900 text-lg mb-1">Verificar integridad</h3>
          <p class="text-gray-500 text-sm mb-4">Comprueba si un documento fue alterado con SHA-256</p>
          <span class="text-xs bg-green-50 text-green-600 px-3 py-1 rounded-full">Disponible</span>
        </div>

        <div v-if="user.role === 'admin'" class="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-all">
          <div class="text-4xl mb-4">📋</div>
          <h3 class="font-semibold text-indigo-900 text-lg mb-1">Logs de auditoría</h3>
          <p class="text-gray-500 text-sm mb-4">Monitorea accesos y eventos criptográficos</p>
          <span class="text-xs bg-indigo-50 text-indigo-600 px-3 py-1 rounded-full">Sprint 3</span>
        </div>

      </div>

      <!-- Stats -->
      <div class="mt-8 grid grid-cols-3 gap-4">
        <div class="bg-indigo-900 text-white rounded-xl p-4 text-center">
          <div class="text-2xl font-bold">SHA-256</div>
          <div class="text-indigo-300 text-xs mt-1">Integridad activa</div>
        </div>
        <div class="bg-purple-800 text-white rounded-xl p-4 text-center">
          <div class="text-2xl font-bold">AES-256</div>
          <div class="text-purple-300 text-xs mt-1">Cifrado simétrico</div>
        </div>
        <div class="bg-teal-700 text-white rounded-xl p-4 text-center">
          <div class="text-2xl font-bold">RSA-2048</div>
          <div class="text-teal-300 text-xs mt-1">Firma digital</div>
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