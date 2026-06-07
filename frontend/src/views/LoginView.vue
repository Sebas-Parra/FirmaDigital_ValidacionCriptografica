<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-900 to-purple-900 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
      
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="text-5xl mb-3">🔐</div>
        <h1 class="text-2xl font-bold text-indigo-900">FirmaDigital</h1>
        <p class="text-gray-500 text-sm mt-1">Plataforma de firma digital segura</p>
      </div>

      <!-- Tabs -->
      <div class="flex rounded-lg overflow-hidden border border-gray-200 mb-6">
        <button
          :class="mode === 'login' ? 'bg-indigo-800 text-white' : 'bg-gray-50 text-gray-600'"
          class="flex-1 py-2.5 text-sm font-medium transition-all"
          @click="mode = 'login'">
          Iniciar sesión
        </button>
        <button
          :class="mode === 'register' ? 'bg-indigo-800 text-white' : 'bg-gray-50 text-gray-600'"
          class="flex-1 py-2.5 text-sm font-medium transition-all"
          @click="mode = 'register'">
          Registrarse
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div v-if="mode === 'register'">
          <label class="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="Tu nombre de usuario"
            required
            class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            v-model="form.email"
            type="email"
            placeholder="tu@email.com"
            required
            class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="Mínimo 8 caracteres"
            required
            class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
        </div>

        <!-- Error / Success -->
        <div v-if="error" class="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg">
          {{ error }}
        </div>
        <div v-if="success" class="bg-green-50 text-green-700 text-sm px-4 py-3 rounded-lg">
          {{ success }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-indigo-800 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-medium py-3 rounded-lg transition-all text-sm">
          {{ loading ? 'Cargando...' : mode === 'login' ? 'Iniciar sesión' : 'Registrarse' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { authService } from '@/services/api'

export default {
  name: 'LoginView',
  data() {
    return {
      mode: 'login',
      form: { username: '', email: '', password: '' },
      error: null,
      success: null,
      loading: false
    }
  },
  methods: {
    async handleSubmit() {
      this.error = null
      this.success = null
      this.loading = true
      try {
        if (this.mode === 'login') {
          const res = await authService.login({
            email: this.form.email,
            password: this.form.password
          })
          localStorage.setItem('token', res.data.access_token)
          localStorage.setItem('user', JSON.stringify(res.data.user))
          this.$router.push('/dashboard')
        } else {
          await authService.register(this.form)
          this.success = 'Usuario registrado. Ahora puedes iniciar sesión.'
          this.mode = 'login'
        }
      } catch (err) {
        this.error = err.response?.data?.error || 'Error al procesar la solicitud'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>