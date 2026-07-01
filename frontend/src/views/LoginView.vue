<template>
  <div class="min-h-screen flex">

    <!-- Panel izquierdo -->
    <div class="hidden lg:flex w-5/12 bg-emerald-950 flex-col justify-between px-14 py-12 relative overflow-hidden shrink-0">
      <div class="absolute inset-0 pointer-events-none opacity-[0.04]">
        <div class="absolute -top-32 -left-32 w-96 h-96 bg-white rounded-full"></div>
        <div class="absolute -bottom-24 -right-24 w-80 h-80 bg-emerald-300 rounded-full"></div>
      </div>

      <!-- Branding -->
      <div class="relative">
        <p class="text-left text-emerald-500 text-xs font-semibold tracking-widest uppercase mb-6">Seguridad del Software</p>
        <div class="flex items-center gap-3 mb-2">
          <div class="w-9 h-9 bg-white/10 rounded-xl flex items-center justify-center shrink-0">
            <svg class="w-5 h-5 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
          <span class="text-white text-2xl font-bold tracking-tight">FirmaDigital</span>
        </div>
        <p class="text-left text-emerald-400 text-sm">Validación Criptográfica de Documentos</p>

        <div class="h-px bg-white/10 my-10"></div>

        <p class="text-left text-emerald-500 text-xs font-semibold tracking-widest uppercase mb-6">Capacidades del sistema</p>
        <div class="flex flex-col gap-5">
          <div v-for="f in features" :key="f.label" class="flex items-center gap-3.5">
            <div class="w-8 h-8 bg-white/8 border border-white/10 rounded-lg flex items-center justify-center shrink-0">
              <svg class="w-4 h-4 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="f.icon"/>
              </svg>
            </div>
            <div class="text-left">
              <p class="text-white text-sm font-medium leading-tight">{{ f.label }}</p>
              <p class="text-emerald-500 text-xs mt-0.5 leading-tight">{{ f.desc }}</p>
            </div>
          </div>
        </div>
      </div>

      <p class="relative text-emerald-700 text-xs">Ingeniería de Sistemas · v1.0</p>
    </div>

    <!-- Panel derecho -->
    <div class="flex-1 flex flex-col items-center justify-center bg-white px-8">
      <div class="w-full max-w-[360px]">

        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ mode === 'login' ? 'Iniciar sesión' : 'Crear cuenta' }}
          </h2>
          <p class="text-gray-400 text-sm mt-1">
            {{ mode === 'login' ? 'Ingresa tus credenciales para continuar' : 'Completa los datos para registrarte' }}
          </p>
        </div>

        <form @submit.prevent="handleSubmit" class="flex flex-col gap-4">

          <div v-if="mode === 'register'" class="flex flex-col gap-1.5">
            <label class="text-sm font-medium text-gray-700">Usuario</label>
            <div class="relative">
              <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              <input v-model="form.username" type="text" placeholder="nombre de usuario" required
                class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"/>
            </div>
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-sm font-medium text-gray-700">Email</label>
            <div class="relative">
              <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              <input v-model="form.email" type="email" placeholder="tu@email.com" required
                class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"/>
            </div>
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-sm font-medium text-gray-700">Contraseña</label>
            <div class="relative">
              <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
              </svg>
              <input v-model="form.password" :type="showPassword ? 'text' : 'password'" placeholder="••••••••" required
                class="w-full pl-10 pr-10 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"/>
              <button type="button" @click="showPassword = !showPassword"
                class="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-300 hover:text-gray-500 transition-colors">
                <svg v-if="!showPassword" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
            </div>
          </div>

          <div v-if="error" class="bg-red-50 border border-red-100 text-red-600 text-xs px-4 py-3 rounded-xl">
            {{ error }}
          </div>
          <div v-if="success" class="bg-emerald-50 border border-emerald-100 text-emerald-700 text-xs px-4 py-3 rounded-xl">
            {{ success }}
          </div>

          <button type="submit" :disabled="loading"
            class="w-full bg-emerald-700 hover:bg-emerald-800 disabled:bg-gray-200 disabled:text-gray-400 text-white font-medium py-2.5 rounded-xl transition-all text-sm mt-1">
            {{ loading ? 'Cargando...' : mode === 'login' ? 'Iniciar sesión' : 'Crear cuenta' }}
          </button>
        </form>

        <p class="text-center text-sm text-gray-400 mt-6">
          {{ mode === 'login' ? '¿No tienes cuenta?' : '¿Ya tienes cuenta?' }}
          <button @click="switchMode" class="text-emerald-700 hover:text-emerald-900 font-medium ml-1 transition-colors">
            {{ mode === 'login' ? 'Regístrate' : 'Inicia sesión' }}
          </button>
        </p>

      </div>

      <p class="mt-16 text-xs text-gray-300">FirmaDigital · Validación Criptográfica</p>
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
      loading: false,
      showPassword: false,
      features: [
        { label: 'Firma digital RSA-2048', desc: 'Firma y verifica documentos con PSS', icon: 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z' },
        { label: 'Cifrado AES-256-GCM', desc: 'Protección autenticada de documentos', icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' },
        { label: 'Verificación SHA-256', desc: 'Integridad garantizada por hash', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
        { label: 'Certificados X.509', desc: 'PKI con autoridad certificadora simulada', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
        { label: 'Control de acceso por roles', desc: 'Usuario · Admin · Superusuario', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z' }
      ]
    }
  },
  methods: {
    switchMode() {
      this.mode = this.mode === 'login' ? 'register' : 'login'
      this.error = null
      this.success = null
    },
    async handleSubmit() {
      this.error = null
      this.success = null
      this.loading = true
      try {
        if (this.mode === 'login') {
          const res = await authService.login({ email: this.form.email, password: this.form.password })
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
