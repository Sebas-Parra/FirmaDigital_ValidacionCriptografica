<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-indigo-900 text-white px-6 py-4 flex justify-between items-center">
      <div class="flex items-center gap-2">
        <span class="text-2xl">🔐</span>
        <span class="font-bold text-lg">FirmaDigital</span>
      </div>
      <div class="flex gap-4 text-sm">
        <router-link to="/dashboard" class="text-indigo-200 hover:text-white">Dashboard</router-link>
        <router-link to="/documents" class="text-white font-medium">Documentos</router-link>
        <router-link to="/certificates" class="text-indigo-200 hover:text-white">Certificados</router-link>
      </div>
    </nav>

    <div class="max-w-4xl mx-auto px-6 py-8">
      <h2 class="text-2xl font-bold text-indigo-900 mb-6">Documentos</h2>

      <!-- Subir documento -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h3 class="font-semibold text-gray-800 mb-4">Subir documento PDF</h3>
        <div class="flex flex-col gap-3">
          <input
            type="file"
            accept=".pdf"
            @change="handleFile"
            class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"/>
          <label class="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
            <input type="checkbox" v-model="encrypt" class="rounded"/>
            Cifrar con AES-256-GCM
          </label>
          <button
            @click="uploadDocument"
            :disabled="!selectedFile || uploading"
            class="bg-indigo-800 hover:bg-indigo-700 disabled:bg-gray-300 text-white px-6 py-2.5 rounded-lg text-sm font-medium w-fit transition-all">
            {{ uploading ? 'Subiendo...' : 'Subir documento' }}
          </button>
        </div>

        <!-- Resultado de subida -->
        <div v-if="uploadResult" class="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <p class="text-green-800 font-medium text-sm mb-2">Documento subido exitosamente</p>
          <p class="text-xs text-gray-600 font-mono break-all">Hash SHA-256: {{ uploadResult.file_hash }}</p>
          <div v-if="uploadResult.encryption_key" class="mt-2 bg-amber-50 border border-amber-200 rounded p-3">
            <p class="text-amber-800 text-xs font-medium mb-1">Guarda esta informacion para descifrar:</p>
            <p class="text-xs font-mono break-all">Key: {{ uploadResult.encryption_key }}</p>
            <p class="text-xs font-mono break-all">Nonce: {{ uploadResult.encryption_nonce }}</p>
          </div>
        </div>

        <div v-if="uploadError" class="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
          <p class="text-red-700 text-sm">{{ uploadError }}</p>
        </div>
      </div>

      <!-- Lista de documentos -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="font-semibold text-gray-800 mb-4">Mis documentos</h3>
        <div v-if="loading" class="text-center text-gray-400 py-8">Cargando...</div>
        <div v-else-if="documents.length === 0" class="text-center text-gray-400 py-8">
          No tienes documentos aun
        </div>
        <div v-else class="space-y-3">
          <div v-for="doc in documents" :key="doc.id"
            class="border border-gray-100 rounded-lg p-4 flex items-center justify-between hover:bg-gray-50">
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span class="text-lg">📄</span>
                <span class="font-medium text-gray-800 text-sm">{{ doc.filename }}</span>
                <span v-if="doc.is_encrypted"
                  class="text-xs bg-amber-50 text-amber-700 px-2 py-0.5 rounded-full">Cifrado</span>
                <span v-if="doc.signature"
                  class="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full">Firmado</span>
              </div>
              <p class="text-xs text-gray-400 font-mono mt-1 break-all">{{ doc.file_hash }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ new Date(doc.uploaded_at).toLocaleString() }}</p>
            </div>
            <div class="flex gap-2 ml-4">
              <button v-if="!doc.signature"
                @click="signDocument(doc.id)"
                class="text-xs bg-indigo-50 text-indigo-700 hover:bg-indigo-100 px-3 py-1.5 rounded-lg transition-all">
                Firmar
              </button>
              <button v-if="doc.signature"
                @click="verifySignature(doc.id)"
                class="text-xs bg-green-50 text-green-700 hover:bg-green-100 px-3 py-1.5 rounded-lg transition-all">
                Verificar firma
              </button>
              <button
                @click="deleteDocument(doc.id)"
                class="text-xs bg-red-50 text-red-700 hover:bg-red-100 px-3 py-1.5 rounded-lg transition-all">
                Eliminar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Resultado verificacion -->
      <div v-if="verifyResult" class="mt-4 rounded-lg p-4"
        :class="verifyResult.signature_valid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
        <p :class="verifyResult.signature_valid ? 'text-green-800' : 'text-red-800'" class="font-medium text-sm">
          {{ verifyResult.message }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { documentService, certificateService } from '@/services/api'

export default {
  name: 'DocumentsView',
  data() {
    return {
      documents: [],
      selectedFile: null,
      encrypt: false,
      uploading: false,
      loading: false,
      uploadResult: null,
      uploadError: null,
      verifyResult: null
    }
  },
  async created() {
    if (!localStorage.getItem('token')) {
      this.$router.push('/login')
      return
    }
    await this.loadDocuments()
  },
  methods: {
    handleFile(e) {
      this.selectedFile = e.target.files[0]
      this.uploadResult = null
      this.uploadError = null
    },
    async loadDocuments() {
      this.loading = true
      try {
        const res = await documentService.list()
        this.documents = res.data.documents
      } catch (err) {
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    async uploadDocument() {
      if (!this.selectedFile) return
      this.uploading = true
      this.uploadResult = null
      this.uploadError = null
      try {
        const formData = new FormData()
        formData.append('file', this.selectedFile)
        formData.append('encrypt', this.encrypt.toString())
        const res = await documentService.upload(formData)
        this.uploadResult = res.data
        await this.loadDocuments()
      } catch (err) {
        this.uploadError = err.response?.data?.error || 'Error al subir el archivo'
      } finally {
        this.uploading = false
      }
    },
    async signDocument(docId) {
    try {
        await certificateService.sign(docId)
        this.documents = []
        await this.loadDocuments()
    } catch (err) {
        alert(err.response?.data?.error || 'Error al firmar')
    }
    },
    async verifySignature(docId) {
      try {
        const res = await certificateService.verifySignature(docId)
        this.verifyResult = res.data
      } catch (err) {
        alert(err.response?.data?.error || 'Error al verificar')
      }
    },
    async deleteDocument(docId) {
      if (!confirm('¿Eliminar este documento?')) return
      try {
        await documentService.delete(docId)
        await this.loadDocuments()
      } catch (err) {
        alert('Error al eliminar')
      }
    }
  }
}
</script>