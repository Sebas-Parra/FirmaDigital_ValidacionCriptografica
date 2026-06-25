<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-indigo-950 text-white px-8 py-4 flex justify-between items-center">
      <div class="flex items-center gap-2.5">
        <svg class="w-4 h-4 text-indigo-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
        </svg>
        <span class="font-semibold tracking-tight">FirmaDigital</span>
      </div>
      <div class="flex items-center gap-6 text-sm">
        <router-link to="/dashboard" class="text-indigo-400 hover:text-white transition-colors">Dashboard</router-link>
        <router-link v-if="isAdmin" to="/admin" class="text-amber-400 hover:text-white transition-colors">Admin</router-link>
        <span class="text-indigo-700">|</span>
        <router-link to="/profile" class="text-indigo-300 hover:text-white transition-colors">{{ user.username }}</router-link>
        <button @click="logout" class="text-indigo-400 hover:text-white transition-colors">Salir</button>
      </div>
    </nav>

    <div class="max-w-3xl mx-auto px-6 py-10">
      <h2 class="text-2xl font-bold text-gray-900 tracking-tight mb-8">Certificados digitales</h2>

      <!-- Notificación -->
      <div v-if="notification" class="flex items-start justify-between rounded-xl px-4 py-3 mb-5 border"
        :class="notification.type === 'success' ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'">
        <p class="text-sm font-medium" :class="notification.type === 'success' ? 'text-green-800' : 'text-red-700'">
          {{ notification.message }}
        </p>
        <button @click="notification = null" class="ml-4 text-lg leading-none opacity-50 hover:opacity-100">&times;</button>
      </div>

      <!-- Generar -->
      <div class="bg-white border border-gray-200 rounded-xl p-6 mb-5">
        <div class="flex items-start justify-between">
          <div>
            <h3 class="font-semibold text-gray-800 text-sm mb-1">Certificado X.509</h3>
            <p class="text-sm text-gray-500">Par de claves RSA-2048 firmado por la CA simulada. Vigencia de 1 año.</p>
          </div>
          <button
            @click="generateCertificate"
            :disabled="generating || hasActive"
            class="shrink-0 ml-6 bg-indigo-950 hover:bg-indigo-900 disabled:bg-gray-200 disabled:text-gray-400 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all">
            {{ generating ? 'Generando...' : hasActive ? 'Ya tienes uno activo' : 'Generar' }}
          </button>
        </div>

        <div v-if="generateResult" class="mt-4 bg-green-50 border border-green-100 rounded-lg p-3">
          <p class="text-green-800 text-sm font-medium">Certificado generado</p>
          <p class="text-xs text-gray-500 mt-0.5">Vence el {{ new Date(generateResult.expires_at).toLocaleDateString() }}</p>
        </div>
      </div>

      <!-- Lista -->
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <h3 class="font-semibold text-gray-800 mb-5 text-sm">Mis certificados</h3>
        <div v-if="loading" class="text-center text-gray-400 py-10 text-sm">Cargando...</div>
        <div v-else-if="certificates.length === 0" class="text-center text-gray-400 py-10 text-sm">
          No tienes certificados aún
        </div>
        <div v-else class="divide-y divide-gray-100">
          <div v-for="cert in certificates" :key="cert.id"
            class="py-4 first:pt-0 last:pb-0">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2.5">
                <span class="font-medium text-gray-800 text-sm">Certificado #{{ cert.id }}</span>
                <span :class="cert.status === 'active'
                  ? 'bg-green-50 text-green-700 border-green-100'
                  : 'bg-gray-50 text-gray-500 border-gray-200'"
                  class="text-xs px-2 py-0.5 rounded-md border">
                  {{ cert.status === 'active' ? 'Activo' : 'Revocado' }}
                </span>
              </div>
              <button v-if="cert.status === 'active'"
                @click="revokeCertificate(cert.id)"
                class="text-xs border border-gray-200 text-gray-400 hover:border-red-200 hover:text-red-600 px-3 py-1.5 rounded-lg transition-all">
                Revocar
              </button>
            </div>
            <div class="text-xs text-gray-400 flex gap-4">
              <span>Emitido: {{ new Date(cert.issued_at).toLocaleDateString() }}</span>
              <span>Vence: {{ new Date(cert.expires_at).toLocaleDateString() }}</span>
            </div>
            <details class="mt-3">
              <summary class="text-xs text-indigo-600 cursor-pointer hover:text-indigo-800 w-fit">Ver PEM</summary>
              <pre class="text-xs bg-gray-50 border border-gray-100 rounded-lg p-3 mt-2 overflow-auto text-gray-500 leading-relaxed">{{ cert.certificate_pem }}</pre>
            </details>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { certificateService } from '@/services/api'

export default {
  name: 'CertificatesView',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      certificates: [],
      loading: false,
      generating: false,
      generateResult: null,
      notification: null
    }
  },
  computed: {
    hasActive() {
      return this.certificates.some(c => c.status === 'active')
    },
    isAdmin() {
      return ['admin', 'superuser'].includes(this.user.role)
    }
  },
  async created() {
    if (!localStorage.getItem('token')) {
      this.$router.push('/login')
      return
    }
    await this.loadCertificates()
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    },
    async loadCertificates() {
      this.loading = true
      try {
        const res = await certificateService.list()
        this.certificates = res.data.certificates
      } catch (err) {
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    async generateCertificate() {
      this.generating = true
      this.notification = null
      try {
        const res = await certificateService.generate()
        this.generateResult = res.data.certificate
        await this.loadCertificates()
        this.notification = { type: 'success', message: 'Certificado X.509 generado correctamente' }
      } catch (err) {
        this.notification = { type: 'error', message: err.response?.data?.error || 'Error al generar certificado' }
      } finally {
        this.generating = false
      }
    },
    async revokeCertificate(certId) {
      if (!confirm('¿Revocar este certificado? Esta acción no se puede deshacer.')) return
      this.notification = null
      try {
        await certificateService.revoke(certId)
        await this.loadCertificates()
        this.notification = { type: 'success', message: 'Certificado revocado' }
      } catch (err) {
        this.notification = { type: 'error', message: err.response?.data?.error || 'Error al revocar' }
      }
    }
  }
}
</script>
