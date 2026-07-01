<template>
  <div class="min-h-screen bg-gray-50 flex">
    <AppSidebar />

    <div class="flex-1 overflow-y-auto">
      <!-- Header -->
      <div class="bg-white border-b border-gray-100 px-8 py-8">
        <h1 class="text-2xl font-bold text-gray-900 tracking-tight">Hola, {{ user.username }}</h1>
        <p class="text-gray-400 mt-1 text-sm">Plataforma de firma digital y validación criptográfica</p>
      </div>

      <div class="max-w-4xl mx-auto px-8 py-8 flex flex-col gap-6">

        <!-- Stats -->
        <div class="grid grid-cols-3 gap-4">
          <div class="bg-white border border-gray-200 rounded-xl px-5 py-4">
            <p class="text-xs text-gray-400 mb-1">Documentos</p>
            <p class="text-2xl font-bold text-gray-900">{{ documents.length }}</p>
          </div>
          <div class="bg-white border border-gray-200 rounded-xl px-5 py-4">
            <p class="text-xs text-gray-400 mb-1">Firmados</p>
            <p class="text-2xl font-bold text-gray-900">{{ documents.filter(d => d.signature).length }}</p>
          </div>
          <div class="bg-white border border-gray-200 rounded-xl px-5 py-4">
            <p class="text-xs text-gray-400 mb-1">Certificado</p>
            <p class="text-sm font-semibold mt-1" :class="activeCert ? 'text-green-600' : 'text-gray-400'">
              {{ activeCert ? 'Activo' : 'Sin certificado' }}
            </p>
          </div>
        </div>

        <!-- Documentos recientes (solo si hay datos) -->
        <div v-if="documents.length > 0" class="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="font-semibold text-gray-800 text-sm">Documentos recientes</h2>
            <router-link to="/documents" class="text-xs text-emerald-600 hover:text-emerald-800 transition-colors">Ver todos →</router-link>
          </div>
          <div class="divide-y divide-gray-50">
            <div v-for="doc in recentDocuments" :key="doc.id"
              class="flex items-center justify-between px-6 py-3.5 hover:bg-gray-50 transition-colors">
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-8 h-8 bg-emerald-50 rounded-lg flex items-center justify-center shrink-0">
                  <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                  </svg>
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-800 truncate">{{ doc.filename }}</p>
                  <p class="text-xs text-gray-400 font-mono">{{ doc.file_hash.slice(0, 20) }}…</p>
                </div>
              </div>
              <div class="flex items-center gap-2 shrink-0 ml-4">
                <span v-if="doc.is_encrypted" class="text-xs bg-amber-50 text-amber-700 border border-amber-100 px-2 py-0.5 rounded-md">Cifrado</span>
                <span v-if="doc.signature" class="text-xs bg-green-50 text-green-700 border border-green-100 px-2 py-0.5 rounded-md">Firmado</span>
                <span class="text-xs text-gray-400">{{ new Date(doc.uploaded_at).toLocaleDateString() }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Certificado activo (solo si existe) -->
        <div v-if="activeCert" class="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="font-semibold text-gray-800 text-sm">Certificado digital</h2>
            <router-link to="/certificates" class="text-xs text-emerald-600 hover:text-emerald-800 transition-colors">Gestionar →</router-link>
          </div>
          <div class="px-6 py-5 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-green-50 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                </svg>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-800">Certificado X.509 #{{ activeCert.id }}</p>
                <p class="text-xs text-gray-400">Vence el {{ new Date(activeCert.expires_at).toLocaleDateString() }}</p>
              </div>
            </div>
            <span class="text-xs bg-green-50 text-green-700 border border-green-100 px-2.5 py-1 rounded-md font-medium">Activo</span>
          </div>
        </div>

        <!-- Feature cards (siempre visibles) -->
        <div class="grid grid-cols-3 gap-4">
          <div class="bg-white border border-gray-200 rounded-xl p-5">
            <div class="w-9 h-9 bg-blue-50 rounded-lg flex items-center justify-center mb-4">
              <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
            </div>
            <h3 class="text-sm font-semibold text-gray-800 mb-1">Cifrado de documentos</h3>
            <p class="text-xs text-gray-400 leading-relaxed">Los archivos PDF se cifran con AES-256-GCM antes de almacenarse. Solo tú puedes descifrarlos.</p>
          </div>
          <div class="bg-white border border-gray-200 rounded-xl p-5">
            <div class="w-9 h-9 bg-violet-50 rounded-lg flex items-center justify-center mb-4">
              <svg class="w-5 h-5 text-violet-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
              </svg>
            </div>
            <h3 class="text-sm font-semibold text-gray-800 mb-1">Firma digital</h3>
            <p class="text-xs text-gray-400 leading-relaxed">Firma tus documentos con tu certificado X.509 y clave privada RSA-2048 mediante el estándar PSS.</p>
          </div>
          <div class="bg-white border border-gray-200 rounded-xl p-5">
            <div class="w-9 h-9 bg-emerald-50 rounded-lg flex items-center justify-center mb-4">
              <svg class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h3 class="text-sm font-semibold text-gray-800 mb-1">Verificación de integridad</h3>
            <p class="text-xs text-gray-400 leading-relaxed">Compara el hash SHA-256 de cualquier archivo contra el registrado para detectar modificaciones.</p>
          </div>
        </div>

        <!-- Tech pills -->
        <div class="flex items-center gap-2.5 flex-wrap">
          <div class="flex items-center gap-2 bg-white border border-gray-200 rounded-full px-3.5 py-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            <span class="text-xs font-medium text-gray-600">SHA-256</span>
            <span class="text-xs text-gray-400">integridad</span>
          </div>
          <div class="flex items-center gap-2 bg-white border border-gray-200 rounded-full px-3.5 py-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
            <span class="text-xs font-medium text-gray-600">AES-256-GCM</span>
            <span class="text-xs text-gray-400">cifrado</span>
          </div>
          <div class="flex items-center gap-2 bg-white border border-gray-200 rounded-full px-3.5 py-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-violet-500"></span>
            <span class="text-xs font-medium text-gray-600">RSA-2048</span>
            <span class="text-xs text-gray-400">firma</span>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import AppSidebar from '@/components/AppSidebar.vue'
import { documentService, certificateService } from '@/services/api'

export default {
  name: 'DashboardView',
  components: { AppSidebar },
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      documents: [],
      certificates: [],
      loading: false
    }
  },
  computed: {
    recentDocuments() {
      return [...this.documents].sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at)).slice(0, 5)
    },
    activeCert() {
      return this.certificates.find(c => c.status === 'active') || null
    }
  },
  async created() {
    if (!localStorage.getItem('token')) {
      this.$router.push('/login')
      return
    }
    this.loading = true
    try {
      const [docsRes, certsRes] = await Promise.all([
        documentService.list(),
        certificateService.list()
      ])
      this.documents = docsRes.data.documents
      this.certificates = certsRes.data.certificates
    } catch (e) {
      console.error(e)
    } finally {
      this.loading = false
    }
  }
}
</script>
