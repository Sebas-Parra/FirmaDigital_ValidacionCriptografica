<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-50 to-white flex items-center justify-center p-4">
    <div class="w-full max-w-sm">

      <div class="text-center mb-8">
        <div class="flex justify-center mb-4">
          <div class="w-11 h-11 bg-indigo-950 rounded-xl flex items-center justify-center shadow-lg">
            <svg class="w-5 h-5 text-indigo-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 tracking-tight">FirmaDigital</h1>
        <p class="text-gray-400 text-sm mt-1">Plataforma de firma digital segura</p>
      </div>

      <div class="bg-white border border-gray-200 rounded-2xl p-7 shadow-sm">

        <div class="flex rounded-lg overflow-hidden border border-gray-100 mb-6 bg-gray-50 p-1 gap-1">
          <button
            :class="mode === 'login' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-400 hover:text-gray-600'"
            class="flex-1 py-2 text-sm font-medium rounded-md transition-all"
            @click="mode = 'login'">
            Iniciar sesión
          </button>
          <button
            :class="mode === 'register' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-400 hover:text-gray-600'"
            class="flex-1 py-2 text-sm font-medium rounded-md transition-all"
            @click="mode = 'register'">
            Registrarse
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div v-if="mode === 'register'">
            <label class="block text-xs font-medium text-gray-600 mb-1.5">Usuario</label>
            <input
              v-model="form.username"
              type="text"
              placeholder="nombre de usuario"
              required
              class="w-full px-3.5 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"/>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1.5">Email</label>
            <input
              v-model="form.email"
              type="email"
              placeholder="tu@email.com"
              required
              class="w-full px-3.5 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"/>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1.5">Contraseña</label>
            <input
              v-model="form.password"
              type="password"
              placeholder="••••••••"
              required
              class="w-full px-3.5 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"/>
          </div>

          <div v-if="error" class="bg-red-50 border border-red-100 text-red-600 text-xs px-3.5 py-3 rounded-lg">
            {{ error }}
          </div>
          <div v-if="success" class="bg-green-50 border border-green-100 text-green-700 text-xs px-3.5 py-3 rounded-lg">
            {{ success }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-indigo-950 hover:bg-indigo-900 disabled:bg-gray-200 disabled:text-gray-400 text-white font-medium py-2.5 rounded-lg transition-all text-sm mt-2 shadow-sm">
            {{ loading ? 'Cargando...' : mode === 'login' ? 'Iniciar sesión' : 'Crear cuenta' }}
          </button>
        </form>
      </div>
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
          this.success = 'Cuenta creada. Ahora puedes iniciar sesión.'
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
