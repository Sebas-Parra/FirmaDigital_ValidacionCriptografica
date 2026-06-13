<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-indigo-900 text-white px-6 py-4 flex justify-between items-center">
      <div class="flex items-center gap-2">
        <span class="text-2xl">🔐</span>
        <span class="font-bold text-lg">FirmaDigital</span>
      </div>
      <div class="flex gap-4 text-sm">
        <router-link to="/dashboard" class="text-indigo-200 hover:text-white">Dashboard</router-link>
        <router-link to="/documents" class="text-indigo-200 hover:text-white">Documentos</router-link>
        <router-link to="/certificates" class="text-white font-medium">Certificados</router-link>
      </div>
    </nav>

    <div class="max-w-4xl mx-auto px-6 py-8">
      <h2 class="text-2xl font-bold text-indigo-900 mb-6">Certificados digitales</h2>

      <!-- Generar certificado -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h3 class="font-semibold text-gray-800 mb-2">Generar certificado X.509</h3>
        <p class="text-sm text-gray-500 mb-4">Genera un par de claves RSA-2048 y un certificado firmado por la CA simulada.</p>
        <button
          @click="generateCertificate"
          :disabled="generating || hasActive"
          class="bg-indigo-800 hover:bg-indigo-700 disabled:bg-gray-300 text-white px-6 py-2.5 rounded-lg text-sm font-medium transition-all">
          {{ generating ? 'Generando...' : hasActive ? 'Ya tienes un certificado activo' : 'Generar certificado' }}
        </button>

        <div v-if="generateResult" class="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <p class="text-green-800 font-medium text-sm">Certificado generado exitosamente</p>
          <p class="text-xs text-gray-500 mt-1">Vence: {{ new Date(generateResult.expires_at).toLocaleDateString() }}</p>
        </div>
      </div>

      <!-- Lista de certificados -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="font-semibold text-gray-800 mb-4">Mis certificados</h3>
        <div v-if="loading" class="text-center text-gray-400 py-8">Cargando...</div>
        <div v-else-if="certificates.length === 0" class="text-center text-gray-400 py-8">
          No tienes certificados aun
        </div>
        <div v-else class="space-y-4">
          <div v-for="cert in certificates" :key="cert.id"
            class="border border-gray-100 rounded-lg p-4">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2">
                <span class="text-lg">🏆</span>
                <span class="font-medium text-gray-800 text-sm">Certificado #{{ cert.id }}</span>
                <span :class="cert.status === 'active'
                  ? 'bg-green-50 text-green-700'
                  : 'bg-red-50 text-red-700'"
                  class="text-xs px-2 py-0.5 rounded-full">
                  {{ cert.status }}
                </span>
              </div>
              <button v-if="cert.status === 'active'"
                @click="revokeCertificate(cert.id)"
                class="text-xs bg-red-50 text-red-700 hover:bg-red-100 px-3 py-1.5 rounded-lg transition-all">
                Revocar
              </button>
            </div>
            <div class="text-xs text-gray-400 space-y-1">
              <p>Emitido: {{ new Date(cert.issued_at).toLocaleString() }}</p>
              <p>Vence: {{ new Date(cert.expires_at).toLocaleString() }}</p>
            </div>
            <details class="mt-3">
              <summary class="text-xs text-indigo-600 cursor-pointer">Ver certificado PEM</summary>
              <pre class="text-xs bg-gray-50 rounded p-3 mt-2 overflow-auto text-gray-600">{{ cert.certificate_pem }}</pre>
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
      certificates: [],
      loading: false,
      generating: false,
      generateResult: null
    }
  },
  computed: {
    hasActive() {
      return this.certificates.some(c => c.status === 'active')
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
      try {
        const res = await certificateService.generate()
        this.generateResult = res.data.certificate
        await this.loadCertificates()
      } catch (err) {
        alert(err.response?.data?.error || 'Error al generar certificado')
      } finally {
        this.generating = false
      }
    },
    async revokeCertificate(certId) {
      if (!confirm('¿Revocar este certificado? Esta accion no se puede deshacer.')) return
      try {
        await certificateService.revoke(certId)
        await this.loadCertificates()
      } catch (err) {
        alert('Error al revocar')
      }
    }
  }
}
</script>