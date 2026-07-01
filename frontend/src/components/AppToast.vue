<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="translate-y-4 opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="translate-y-4 opacity-0"
  >
    <div v-if="visible"
      class="fixed bottom-5 right-5 z-50 flex items-start gap-3 px-4 py-3.5 rounded-xl shadow-lg border max-w-sm w-full"
      :class="notification.type === 'success'
        ? 'bg-white border-emerald-100 text-emerald-800'
        : 'bg-white border-red-100 text-red-700'">

      <!-- Ícono -->
      <div class="shrink-0 mt-0.5">
        <svg v-if="notification.type === 'success'" class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <svg v-else class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      </div>

      <!-- Mensaje -->
      <div class="flex-1">
        <p class="text-sm leading-snug">{{ notification.message }}</p>
        <div v-if="notification.hashes" class="mt-2 space-y-0.5">
          <p class="text-xs font-mono text-gray-400">Original: {{ notification.hashes.stored }}</p>
          <p class="text-xs font-mono" :class="notification.type === 'success' ? 'text-gray-400' : 'text-red-400'">
            Actual:&nbsp;&nbsp;&nbsp;{{ notification.hashes.current }}
          </p>
        </div>
      </div>

      <!-- Cerrar -->
      <button @click="close" class="shrink-0 opacity-40 hover:opacity-80 transition-opacity leading-none text-base mt-0.5">&times;</button>

      <!-- Barra de progreso -->
      <div class="absolute bottom-0 left-0 h-0.5 rounded-b-xl transition-all ease-linear"
        :class="notification.type === 'success' ? 'bg-emerald-400' : 'bg-red-400'"
        :style="{ width: progress + '%', transitionDuration: running ? duration + 'ms' : '0ms' }">
      </div>
    </div>
  </Transition>
</template>

<script>
export default {
  name: 'AppToast',
  props: {
    notification: { type: Object, default: null },
    duration: { type: Number, default: 4000 }
  },
  emits: ['close'],
  data() {
    return { visible: false, progress: 100, running: false, timer: null }
  },
  watch: {
    notification(val) {
      if (val) this.show()
    }
  },
  methods: {
    show() {
      clearTimeout(this.timer)
      this.visible = true
      this.progress = 100
      this.$nextTick(() => {
        this.running = true
        this.progress = 0
        this.timer = setTimeout(this.close, this.duration)
      })
    },
    close() {
      clearTimeout(this.timer)
      this.running = false
      this.visible = false
      this.$emit('close')
    }
  }
}
</script>
