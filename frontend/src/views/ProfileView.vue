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
        <span class="text-indigo-700">|</span>
        <span class="text-indigo-300">{{ user.username }}</span>
        <button @click="logout" class="text-indigo-400 hover:text-white transition-colors">Salir</button>
      </div>
    </nav>

    <div class="max-w-xl mx-auto px-6 py-10">
      <h2 class="text-2xl font-bold text-gray-900 tracking-tight mb-8">Mi perfil</h2>

      <!-- Notificación -->
      <div v-if="notification" class="flex items-start justify-between rounded-xl px-4 py-3 mb-5 border"
        :class="notification.type === 'success' ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'">
        <p class="text-sm font-medium" :class="notification.type === 'success' ? 'text-green-800' : 'text-red-700'">
          {{ notification.message }}
        </p>
        <button @click="notification = null" class="ml-4 text-lg leading-none opacity-50 hover:opacity-100">&times;</button>
      </div>

      <!-- Datos de cuenta -->
      <div class="bg-white border border-gray-200 rounded-xl p-6 mb-5">
        <h3 class="font-semibold text-gray-800 text-sm mb-5">Datos de cuenta</h3>
        <div class="flex flex-col gap-4">
          <div>
            <label class="block text-xs text-gray-500 mb-1.5">Nombre de usuario</label>
            <input v-model="form.username" type="text"
              class="w-full px-3.5 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1.5">Correo electrónico</label>
            <input v-model="form.email" type="email"
              class="w-full px-3.5 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1.5">Nueva contraseña <span class="text-gray-400">(dejar vacío para no cambiar)</span></label>
            <input v-model="form.password" type="password" placeholder="mínimo 8 caracteres"
              class="w-full px-3.5 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
          </div>
          <button @click="updateProfile" :disabled="saving"
            class="bg-indigo-950 hover:bg-indigo-900 disabled:bg-gray-200 disabled:text-gray-400 text-white px-5 py-2 rounded-lg text-sm font-medium w-fit transition-all">
            {{ saving ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </div>
      </div>

      <!-- Zona de peligro -->
      <div class="bg-white border border-red-100 rounded-xl p-6">
        <h3 class="font-semibold text-red-700 text-sm mb-1">Zona de peligro</h3>
        <p class="text-xs text-gray-400 mb-4">Esta acción eliminará tu cuenta y todos tus datos permanentemente. No se puede deshacer.</p>
        <button @click="confirmDelete"
          class="text-sm border border-red-200 text-red-600 hover:bg-red-50 px-4 py-2 rounded-lg transition-all">
          Eliminar mi cuenta
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { authService } from '@/services/api'

export default {
  name: 'ProfileView',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      form: { username: '', email: '', password: '' },
      saving: false,
      notification: null
    }
  },
  created() {
    if (!localStorage.getItem('token')) {
      this.$router.push('/login')
      return
    }
    this.form.username = this.user.username || ''
    this.form.email = this.user.email || ''
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    },
    async updateProfile() {
      this.saving = true
      this.notification = null
      const payload = {}
      if (this.form.username && this.form.username !== this.user.username)
        payload.username = this.form.username
      if (this.form.email && this.form.email !== this.user.email)
        payload.email = this.form.email
      if (this.form.password)
        payload.password = this.form.password

      if (Object.keys(payload).length === 0) {
        this.notification = { type: 'error', message: 'No se realizaron cambios' }
        this.saving = false
        return
      }

      try {
        const res = await authService.updateProfile(payload)
        const updatedUser = res.data.user
        localStorage.setItem('user', JSON.stringify(updatedUser))
        this.user = updatedUser
        this.form.password = ''
        this.notification = { type: 'success', message: 'Perfil actualizado correctamente' }
      } catch (err) {
        this.notification = { type: 'error', message: err.response?.data?.error || 'Error al actualizar perfil' }
      } finally {
        this.saving = false
      }
    },
    async confirmDelete() {
      if (!confirm('¿Seguro que deseas eliminar tu cuenta? Se eliminarán todos tus documentos y certificados.')) return
      try {
        await authService.deleteAccount()
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        this.$router.push('/login')
      } catch (err) {
        this.notification = { type: 'error', message: err.response?.data?.error || 'Error al eliminar cuenta' }
      }
    }
  }
}
</script>
