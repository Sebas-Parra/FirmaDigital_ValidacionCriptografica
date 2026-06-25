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
      <h2 class="text-2xl font-bold text-gray-900 tracking-tight mb-8">Documentos</h2>

      <!-- Subir -->
      <div class="bg-white border border-gray-200 rounded-xl p-6 mb-5">
        <h3 class="font-semibold text-gray-800 mb-4 text-sm">Subir documento</h3>
        <div class="flex flex-col gap-3">
          <input ref="uploadInput" type="file" accept=".pdf" @change="handleFile" class="hidden"/>
          <div class="flex items-center gap-2 flex-wrap">
            <button @click="$refs.uploadInput.click()"
              class="text-xs bg-indigo-50 text-indigo-700 border border-indigo-100 hover:bg-indigo-100 px-4 py-1.5 rounded-lg font-medium transition-all">
              Seleccionar PDF
            </button>
            <div v-if="selectedFile" class="flex items-center gap-1.5 bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5">
              <svg class="w-3.5 h-3.5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <span class="text-xs text-gray-600 max-w-xs truncate">{{ selectedFile.name }}</span>
              <button @click="clearUploadFile" class="ml-1 text-gray-400 hover:text-red-500 transition-colors">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
            <span v-else class="text-xs text-gray-400">Ningún archivo seleccionado</span>
          </div>
          <label class="flex items-center gap-2 text-sm text-gray-500 cursor-pointer w-fit">
            <input type="checkbox" v-model="encrypt" class="rounded accent-indigo-700"/>
            Cifrar con AES-256-GCM
          </label>
          <button
            @click="uploadDocument"
            :disabled="!selectedFile || uploading"
            class="bg-indigo-950 hover:bg-indigo-900 disabled:bg-gray-200 disabled:text-gray-400 text-white px-5 py-2 rounded-lg text-sm font-medium w-fit transition-all">
            {{ uploading ? 'Subiendo...' : 'Subir' }}
          </button>
        </div>

        <div v-if="uploadResult" class="mt-4 bg-green-50 border border-green-100 rounded-lg p-4">
          <p class="text-green-800 font-medium text-sm">Documento subido: <span class="font-semibold">{{ uploadResult.document.filename }}</span></p>
          <p class="text-xs text-gray-500 font-mono break-all mt-1">SHA-256: {{ uploadResult.file_hash }}</p>
          <div v-if="uploadResult.encryption_key" class="mt-3 bg-amber-50 border border-amber-100 rounded-lg p-3">
            <p class="text-amber-800 text-xs font-semibold mb-1.5">Guarda estos valores — son necesarios para descifrar</p>
            <p class="text-xs font-mono break-all text-gray-600">Key: {{ uploadResult.encryption_key }}</p>
            <p class="text-xs font-mono break-all text-gray-600 mt-1">Nonce: {{ uploadResult.encryption_nonce }}</p>
          </div>
        </div>

        <div v-if="uploadError" class="mt-3 bg-red-50 border border-red-100 rounded-lg p-3">
          <p class="text-red-700 text-sm">{{ uploadError }}</p>
        </div>
      </div>

      <!-- Notificación -->
      <div v-if="notification" class="flex items-start justify-between rounded-xl px-4 py-3 mb-5 border"
        :class="notification.type === 'success' ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'">
        <div>
          <p class="text-sm font-medium" :class="notification.type === 'success' ? 'text-green-800' : 'text-red-700'">
            {{ notification.message }}
          </p>
          <div v-if="notification.hashes" class="mt-2 space-y-0.5">
            <p class="text-xs font-mono text-gray-500">Original: {{ notification.hashes.stored }}</p>
            <p class="text-xs font-mono" :class="notification.type === 'success' ? 'text-gray-500' : 'text-red-400'">
              Actual:&nbsp;&nbsp;&nbsp;{{ notification.hashes.current }}
            </p>
          </div>
        </div>
        <button @click="notification = null" class="ml-4 text-lg leading-none opacity-50 hover:opacity-100">&times;</button>
      </div>

      <!-- Lista -->
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <h3 class="font-semibold text-gray-800 mb-5 text-sm">Mis documentos</h3>
        <div v-if="loading" class="text-center text-gray-400 py-10 text-sm">Cargando...</div>
        <div v-else-if="documents.length === 0" class="text-center text-gray-400 py-10 text-sm">
          No has subido documentos aún
        </div>
        <div v-else class="divide-y divide-gray-100">
          <div v-for="doc in documents" :key="doc.id"
            class="py-4 flex items-start justify-between gap-4 first:pt-0 last:pb-0">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-medium text-gray-800 text-sm truncate">{{ doc.filename }}</span>
                <span v-if="doc.is_encrypted"
                  class="text-xs bg-amber-50 text-amber-700 border border-amber-100 px-2 py-0.5 rounded-md">Cifrado</span>
                <span v-if="doc.signature"
                  class="text-xs bg-green-50 text-green-700 border border-green-100 px-2 py-0.5 rounded-md">Firmado</span>
                <span v-if="verifiedDocs[doc.id] === true"
                  class="text-xs bg-indigo-50 text-indigo-700 border border-indigo-100 px-2 py-0.5 rounded-md">Verificado</span>
                <span v-if="verifiedDocs[doc.id] === false"
                  class="text-xs bg-red-50 text-red-700 border border-red-100 px-2 py-0.5 rounded-md">Firma inválida</span>
              </div>
              <p class="text-xs text-gray-400 font-mono mt-1 truncate">{{ doc.file_hash }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ new Date(doc.uploaded_at).toLocaleString() }}</p>
            </div>
            <div class="flex gap-2 shrink-0">
              <button v-if="!doc.signature"
                @click="signDocument(doc.id)"
                class="text-xs border border-gray-200 text-gray-600 hover:border-indigo-300 hover:text-indigo-700 px-3 py-1.5 rounded-lg transition-all">
                Firmar
              </button>
              <button v-if="doc.signature"
                @click="verifySignature(doc.id)"
                class="text-xs border border-gray-200 text-gray-600 hover:border-green-300 hover:text-green-700 px-3 py-1.5 rounded-lg transition-all">
                Verificar
              </button>
              <button
                @click="downloadDocument(doc.id, doc.filename)"
                class="text-xs border border-gray-200 text-gray-600 hover:border-indigo-300 hover:text-indigo-700 px-3 py-1.5 rounded-lg transition-all">
                Descargar
              </button>
              <button
                @click="deleteDocument(doc.id)"
                class="text-xs border border-gray-200 text-gray-400 hover:border-red-200 hover:text-red-600 px-3 py-1.5 rounded-lg transition-all">
                Eliminar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Verificar integridad -->
      <div class="bg-white border border-gray-200 rounded-xl p-6 mt-5">
        <h3 class="font-semibold text-gray-800 mb-1 text-sm">Verificar integridad</h3>
        <p class="text-xs text-gray-400 mb-4">Sube el archivo y selecciona el documento original para comprobar si fue modificado</p>
        <div class="flex flex-col gap-3">
          <div>
            <label class="block text-xs text-gray-500 mb-1.5">Archivo a verificar (.pdf)</label>
            <input ref="verifyInput" type="file" accept=".pdf" @change="handleVerifyFile" class="hidden"/>
            <div class="flex items-center gap-2 flex-wrap">
              <button @click="$refs.verifyInput.click()"
                class="text-xs bg-gray-50 text-gray-700 border border-gray-200 hover:bg-gray-100 px-4 py-1.5 rounded-lg font-medium transition-all">
                Seleccionar PDF
              </button>
              <div v-if="verifyForm.file" class="flex items-center gap-1.5 bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5">
                <svg class="w-3.5 h-3.5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <span class="text-xs text-gray-600 max-w-xs truncate">{{ verifyForm.file.name }}</span>
                <button @click="clearVerifyFile" class="ml-1 text-gray-400 hover:text-red-500 transition-colors">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
              <span v-else class="text-xs text-gray-400">Ningún archivo seleccionado</span>
            </div>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1.5">Documento original a comparar</label>
            <div class="relative">
              <div class="flex items-center border rounded-lg overflow-hidden transition-all"
                :class="verifyForm.showDocDropdown ? 'border-indigo-400 ring-2 ring-indigo-100' : 'border-gray-200'">
                <svg class="w-3.5 h-3.5 text-gray-400 ml-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
                <input
                  v-model="verifyForm.docSearch"
                  @focus="verifyForm.showDocDropdown = true"
                  @blur="closeDocDropdown"
                  @input="verifyForm.documentId = ''"
                  type="text"
                  placeholder="Buscar por nombre de archivo..."
                  class="w-full px-2.5 py-2 text-sm bg-white focus:outline-none"/>
                <button v-if="verifyForm.documentId" @click="clearVerifyDoc"
                  class="px-2.5 text-gray-400 hover:text-red-500 transition-colors">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
              <div v-if="verifyForm.showDocDropdown"
                class="absolute z-20 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden">
                <div class="max-h-48 overflow-y-auto">
                  <button v-for="doc in filteredDocuments" :key="doc.id"
                    @mousedown="selectVerifyDoc(doc)"
                    class="w-full text-left px-3.5 py-2.5 text-sm hover:bg-indigo-50 flex items-center justify-between gap-3 transition-colors"
                    :class="verifyForm.documentId === doc.id ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700'">
                    <span class="truncate font-medium">{{ doc.filename }}</span>
                    <span class="text-xs text-gray-400 font-mono shrink-0">{{ doc.file_hash.slice(0, 12) }}…</span>
                  </button>
                  <p v-if="filteredDocuments.length === 0" class="px-3.5 py-3 text-xs text-gray-400">
                    Sin resultados para "{{ verifyForm.docSearch }}"
                  </p>
                </div>
                <div v-if="documents.length > 0" class="border-t border-gray-100 px-3.5 py-1.5">
                  <p class="text-xs text-gray-400">{{ filteredDocuments.length }} de {{ documents.length }} documentos</p>
                </div>
              </div>
            </div>
          </div>
          <button
            @click="verifyIntegrity"
            :disabled="!verifyForm.file || !verifyForm.documentId || verifyForm.loading"
            class="bg-indigo-950 hover:bg-indigo-900 disabled:bg-gray-200 disabled:text-gray-400 text-white px-5 py-2 rounded-lg text-sm font-medium w-fit transition-all">
            {{ verifyForm.loading ? 'Verificando...' : 'Verificar integridad' }}
          </button>
        </div>

        <div v-if="verifyForm.result" class="mt-4 rounded-lg p-4 border"
          :class="verifyForm.result.is_valid ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'">
          <p class="font-medium text-sm" :class="verifyForm.result.is_valid ? 'text-green-800' : 'text-red-700'">
            {{ verifyForm.result.message }}
          </p>
          <div class="mt-2 mb-2 flex items-center gap-1.5 text-xs text-gray-500">
            <span class="font-medium">Verificado:</span>
            <span class="font-mono bg-gray-100 px-1.5 py-0.5 rounded">{{ verifyForm.file ? verifyForm.file.name : '' }}</span>
            <span>vs</span>
            <span class="font-mono bg-gray-100 px-1.5 py-0.5 rounded">{{ verifyForm.result.filename }}</span>
          </div>
          <div class="space-y-1">
            <p class="text-xs text-gray-500 font-mono">Original: {{ verifyForm.result.stored_hash }}</p>
            <p class="text-xs font-mono" :class="verifyForm.result.is_valid ? 'text-gray-500' : 'text-red-500'">
              Actual:&nbsp;&nbsp;&nbsp;{{ verifyForm.result.current_hash }}
            </p>
          </div>
        </div>
      </div>

      <!-- Descifrar -->
      <div class="bg-white border border-gray-200 rounded-xl p-6 mt-5">
        <h3 class="font-semibold text-gray-800 mb-4 text-sm">Descifrar documento</h3>
        <div class="flex flex-col gap-3">
          <div>
            <label class="block text-xs text-gray-500 mb-1.5">Archivo cifrado (.enc)</label>
            <input ref="encInput" type="file" @change="handleEncFile" class="hidden"/>
            <div class="flex items-center gap-2 flex-wrap">
              <button @click="$refs.encInput.click()"
                class="text-xs bg-gray-50 text-gray-700 border border-gray-200 hover:bg-gray-100 px-4 py-1.5 rounded-lg font-medium transition-all">
                Seleccionar .enc
              </button>
              <div v-if="decryptForm.encFile" class="flex items-center gap-1.5 bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5">
                <svg class="w-3.5 h-3.5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                <span class="text-xs text-gray-600 max-w-xs truncate">{{ decryptForm.encFile.name }}</span>
                <button @click="clearEncFile" class="ml-1 text-gray-400 hover:text-red-500 transition-colors">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
              <span v-else class="text-xs text-gray-400">Ningún archivo seleccionado</span>
            </div>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1.5">Key (base64)</label>
            <input
              v-model="decryptForm.key"
              type="text"
              placeholder="rFyQI5c4q3AhMaME0ATN/..."
              class="w-full px-3.5 py-2 border border-gray-200 rounded-lg text-xs font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1.5">Nonce (base64)</label>
            <input
              v-model="decryptForm.nonce"
              type="text"
              placeholder="a9Wtv94Ufdm+KPXf"
              class="w-full px-3.5 py-2 border border-gray-200 rounded-lg text-xs font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
          </div>
          <button
            @click="decryptDocument"
            :disabled="!decryptForm.encFile || !decryptForm.key || !decryptForm.nonce || decrypting"
            class="bg-indigo-950 hover:bg-indigo-900 disabled:bg-gray-200 disabled:text-gray-400 text-white px-5 py-2 rounded-lg text-sm font-medium w-fit transition-all">
            {{ decrypting ? 'Descifrando...' : 'Descifrar y descargar' }}
          </button>
        </div>

        <div v-if="decryptError" class="mt-3 bg-red-50 border border-red-100 rounded-lg p-3">
          <p class="text-red-700 text-sm">{{ decryptError }}</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { documentService, certificateService } from '@/services/api'

export default {
  name: 'DocumentsView',
  computed: {
    isAdmin() {
      return ['admin', 'superuser'].includes(this.user.role)
    },
    filteredDocuments() {
      const q = this.verifyForm.docSearch.toLowerCase().trim()
      if (!q) return this.documents
      return this.documents.filter(d => d.filename.toLowerCase().includes(q))
    }
  },
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      documents: [],
      selectedFile: null,
      encrypt: false,
      uploading: false,
      loading: false,
      uploadResult: null,
      uploadError: null,
      decryptForm: { encFile: null, key: '', nonce: '' },
      decrypting: false,
      decryptError: null,
      verifyForm: { file: null, documentId: '', docSearch: '', showDocDropdown: false, loading: false, result: null },
      notification: null,
      verifiedDocs: {}
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
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    },
    handleFile(e) {
      this.selectedFile = e.target.files[0]
      this.uploadResult = null
      this.uploadError = null
    },
    clearUploadFile() {
      this.selectedFile = null
      this.uploadResult = null
      this.uploadError = null
      this.$refs.uploadInput.value = ''
    },
    clearVerifyFile() {
      this.verifyForm.file = null
      this.verifyForm.result = null
      this.$refs.verifyInput.value = ''
    },
    selectVerifyDoc(doc) {
      this.verifyForm.documentId = doc.id
      this.verifyForm.docSearch = doc.filename
      this.verifyForm.showDocDropdown = false
    },
    clearVerifyDoc() {
      this.verifyForm.documentId = ''
      this.verifyForm.docSearch = ''
    },
    closeDocDropdown() {
      setTimeout(() => { this.verifyForm.showDocDropdown = false }, 150)
    },
    clearEncFile() {
      this.decryptForm.encFile = null
      this.decryptError = null
      this.$refs.encInput.value = ''
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
      this.notification = null
      try {
        await certificateService.sign(docId)
        this.documents = []
        await this.loadDocuments()
        this.notification = { type: 'success', message: 'Documento firmado correctamente' }
      } catch (err) {
        this.notification = { type: 'error', message: err.response?.data?.error || 'Error al firmar el documento' }
      }
    },
    async verifySignature(docId) {
      this.notification = null
      try {
        const res = await certificateService.verifySignature(docId)
        this.verifiedDocs = { ...this.verifiedDocs, [docId]: res.data.signature_valid }
        if (!res.data.signature_valid) {
          this.notification = { type: 'error', message: res.data.message }
        }
      } catch (err) {
        this.notification = { type: 'error', message: err.response?.data?.error || 'Error al verificar la firma' }
      }
    },
    handleVerifyFile(e) {
      this.verifyForm.file = e.target.files[0]
      this.verifyForm.result = null
    },
    async verifyIntegrity() {
      this.verifyForm.loading = true
      this.verifyForm.result = null
      try {
        const formData = new FormData()
        formData.append('file', this.verifyForm.file)
        formData.append('document_id', this.verifyForm.documentId)
        const res = await documentService.verify(formData)
        this.verifyForm.result = res.data
      } catch (err) {
        this.verifyForm.result = { is_valid: false, message: 'Error al verificar', stored_hash: '', current_hash: '' }
      } finally {
        this.verifyForm.loading = false
      }
    },
    handleEncFile(e) {
      this.decryptForm.encFile = e.target.files[0]
      this.decryptError = null
    },
    async decryptDocument() {
      this.decrypting = true
      this.decryptError = null
      try {
        const arrayBuffer = await this.decryptForm.encFile.arrayBuffer()
        const encrypted_data = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)))
        const res = await documentService.decrypt({
          encrypted_data,
          key: this.decryptForm.key,
          nonce: this.decryptForm.nonce
        })
        const binary = atob(res.data.decrypted_data)
        const bytes = new Uint8Array(binary.length)
        for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
        const blob = new Blob([bytes], { type: 'application/pdf' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = this.decryptForm.encFile.name.replace('.enc', '')
        a.click()
        URL.revokeObjectURL(url)
      } catch (err) {
        this.decryptError = err.response?.data?.error || 'Clave incorrecta o archivo inválido'
      } finally {
        this.decrypting = false
      }
    },
    async downloadDocument(docId, filename) {
      try {
        const res = await documentService.download(docId)
        const a = document.createElement('a')
        a.href = res.data.url
        a.download = filename
        a.target = '_blank'
        a.click()
      } catch (err) {
        this.notification = { type: 'error', message: 'Archivo no disponible para descarga' }
      }
    },
    async deleteDocument(docId) {
      if (!confirm('¿Eliminar este documento?')) return
      this.notification = null
      try {
        await documentService.delete(docId)
        await this.loadDocuments()
      } catch (err) {
        this.notification = { type: 'error', message: 'Error al eliminar el documento' }
      }
    }
  }
}
</script>
