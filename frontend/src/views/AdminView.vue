<template>
  <div class="min-h-screen bg-gray-50 flex">
    <AppSidebar />

    <div class="flex-1 overflow-y-auto">
    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 tracking-tight">Panel de administración</h2>
          <p class="text-sm text-gray-400 mt-0.5">
            Sesión como
            <span class="font-medium" :class="roleBadgeClass(currentUser.role)">{{ currentUser.role }}</span>
          </p>
        </div>
      </div>


      <!-- Formulario nuevo usuario -->
      <div class="bg-white border border-gray-200 rounded-xl p-6 mb-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-800 text-sm">Nuevo usuario</h3>
          <button @click="showCreateForm = !showCreateForm"
            class="text-xs border border-gray-200 text-gray-500 hover:border-emerald-300 hover:text-emerald-700 px-3 py-1.5 rounded-lg transition-all">
            {{ showCreateForm ? 'Cancelar' : '+ Crear usuario' }}
          </button>
        </div>
        <div v-if="showCreateForm" class="flex gap-3 items-end flex-wrap">
          <div>
            <label class="block text-xs text-gray-500 mb-1.5">Username</label>
            <input v-model="createForm.username" type="text" placeholder="usuario123"
              class="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 w-36"/>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1.5">Email</label>
            <input v-model="createForm.email" type="email" placeholder="user@email.com"
              class="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 w-48"/>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1.5">Contraseña</label>
            <input v-model="createForm.password" type="password" placeholder="mín. 8 chars"
              class="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 w-36"/>
          </div>
          <div v-if="currentUser.role === 'superuser'">
            <label class="block text-xs text-gray-500 mb-1.5">Rol</label>
            <select v-model="createForm.role"
              class="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500">
              <option value="user">user</option>
              <option value="admin">admin</option>
              <option value="superuser">superuser</option>
            </select>
          </div>
          <button @click="createUser" :disabled="creating"
            class="bg-emerald-950 hover:bg-emerald-900 disabled:bg-gray-200 disabled:text-gray-400 text-white px-5 py-2 rounded-lg text-sm font-medium transition-all">
            {{ creating ? 'Creando...' : 'Crear' }}
          </button>
        </div>
      </div>

      <!-- Tabla de usuarios -->
      <div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 class="font-semibold text-gray-800 text-sm">Usuarios registrados</h3>
          <span class="text-xs text-gray-400">{{ users.length }} usuario{{ users.length !== 1 ? 's' : '' }}</span>
        </div>

        <div v-if="loading" class="text-center text-gray-400 py-12 text-sm">Cargando...</div>
        <div v-else-if="users.length === 0" class="text-center text-gray-400 py-12 text-sm">No hay usuarios</div>
        <div v-else>
          <!-- Encabezado -->
          <div class="grid grid-cols-12 gap-4 px-6 py-2 bg-gray-50 text-xs font-medium text-gray-400 uppercase tracking-wider border-b border-gray-100">
            <div class="col-span-1">#</div>
            <div class="col-span-3">Usuario</div>
            <div class="col-span-4">Email</div>
            <div class="col-span-2">Rol</div>
            <div class="col-span-2 text-right">Acciones</div>
          </div>

          <!-- Filas -->
          <div v-for="user in users" :key="user.id">
            <!-- Fila normal -->
            <div class="grid grid-cols-12 gap-4 px-6 py-3.5 items-center border-b border-gray-50 hover:bg-gray-50 transition-colors"
              :class="user.id === currentUser.id ? 'bg-emerald-50/30' : ''">
              <div class="col-span-1 text-xs text-gray-400">{{ user.id }}</div>
              <div class="col-span-3">
                <span class="text-sm font-medium text-gray-800">{{ user.username }}</span>
                <span v-if="user.id === currentUser.id" class="ml-1.5 text-xs text-emerald-400">(tú)</span>
              </div>
              <div class="col-span-4 text-sm text-gray-500 truncate">{{ user.email }}</div>
              <div class="col-span-2">
                <!-- Rol como select si es superuser y no es la propia cuenta -->
                <select v-if="currentUser.role === 'superuser' && user.id !== currentUser.id"
                  :value="user.role"
                  @change="changeRole(user, $event.target.value)"
                  class="text-xs border rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-emerald-500 cursor-pointer"
                  :class="roleSelectClass(user.role)">
                  <option value="user">user</option>
                  <option value="admin">admin</option>
                </select>
                <!-- Badge estático para admin o cuenta propia -->
                <span v-else
                  class="text-xs px-2 py-0.5 rounded-md border font-medium"
                  :class="roleBadgeFullClass(user.role)">
                  {{ user.role }}
                </span>
              </div>
              <div class="col-span-2 flex justify-end gap-2">
                <button @click="startEdit(user)"
                  v-if="canEdit(user)"
                  class="text-xs border border-gray-200 text-gray-500 hover:border-emerald-300 hover:text-emerald-700 px-2.5 py-1 rounded-lg transition-all">
                  Editar
                </button>
                <button @click="deleteUser(user)"
                  v-if="canDelete(user)"
                  class="text-xs border border-gray-200 text-gray-400 hover:border-red-200 hover:text-red-600 px-2.5 py-1 rounded-lg transition-all">
                  Eliminar
                </button>
              </div>
            </div>

            <!-- Fila de edición inline -->
            <div v-if="editingId === user.id" class="px-6 py-4 bg-emerald-50/40 border-b border-emerald-100">
              <div class="flex gap-3 items-end flex-wrap">
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Usuario</label>
                  <input v-model="editForm.username" type="text"
                    class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 w-40"/>
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Email</label>
                  <input v-model="editForm.email" type="email"
                    class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 w-52"/>
                </div>
                <button @click="saveEdit(user.id)"
                  class="bg-emerald-950 hover:bg-emerald-900 text-white px-4 py-1.5 rounded-lg text-sm font-medium transition-all">
                  Guardar
                </button>
                <button @click="editingId = null"
                  class="text-sm text-gray-400 hover:text-gray-700 px-3 py-1.5 transition-colors">
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Nota superuser -->
      <p v-if="currentUser.role !== 'superuser'" class="text-xs text-gray-400 mt-4 text-center">
        Solo el superusuario puede cambiar roles. Como admin puedes editar datos y eliminar usuarios regulares.
      </p>
    </div>
    </div><!-- flex-1 -->

    <AppToast :notification="notification" @close="notification = null" />

    <!-- Modal de confirmación de eliminación -->
    <div v-if="deleteModal.show" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="deleteModal.show = false"></div>
      <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm mx-4 p-6">
        <div class="w-10 h-10 bg-red-50 rounded-xl flex items-center justify-center mb-4">
          <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </div>
        <h3 class="font-semibold text-gray-900 text-base mb-1">Eliminar usuario</h3>
        <p class="text-sm text-gray-500 mb-5">
          ¿Estás seguro de que quieres eliminar a
          <span class="font-semibold text-gray-800">{{ deleteModal.username }}</span>?
          Se eliminarán todos sus documentos y certificados permanentemente.
        </p>
        <div class="flex gap-2 justify-end">
          <button @click="deleteModal.show = false"
            class="px-4 py-2 text-sm text-gray-500 border border-gray-200 rounded-lg hover:border-gray-300 hover:text-gray-700 transition-all">
            Cancelar
          </button>
          <button @click="confirmDelete" :disabled="deleteModal.loading"
            class="px-4 py-2 text-sm text-white bg-red-600 hover:bg-red-700 disabled:bg-red-300 rounded-lg font-medium transition-all">
            {{ deleteModal.loading ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adminService } from '@/services/api'
import AppSidebar from '@/components/AppSidebar.vue'
import AppToast from '@/components/AppToast.vue'

export default {
  name: 'AdminView',
  components: { AppSidebar, AppToast },
  data() {
    return {
      currentUser: JSON.parse(localStorage.getItem('user') || '{}'),
      users: [],
      loading: false,
      notification: null,
      editingId: null,
      editForm: { username: '', email: '' },
      showCreateForm: false,
      creating: false,
      createForm: { username: '', email: '', password: '', role: 'user' },
      deleteModal: { show: false, userId: null, username: '', loading: false }
    }
  },
  async created() {
    const token = localStorage.getItem('token')
    const role = this.currentUser.role
    if (!token || !['admin', 'superuser'].includes(role)) {
      this.$router.push('/dashboard')
      return
    }
    await this.loadUsers()
  },
  methods: {
    async createUser() {
      this.creating = true
      this.notification = null
      try {
        const payload = { ...this.createForm }
        if (this.currentUser.role !== 'superuser') payload.role = 'user'
        await adminService.createUser(payload)
        this.notification = { type: 'success', message: `Usuario ${payload.username} creado con rol ${payload.role}` }
        this.createForm = { username: '', email: '', password: '', role: 'user' }
        this.showCreateForm = false
        await this.loadUsers()
      } catch (err) {
        this.notification = { type: 'error', message: err.response?.data?.error || 'Error al crear usuario' }
      } finally {
        this.creating = false
      }
    },
    async loadUsers() {
      this.loading = true
      try {
        const res = await adminService.listUsers()
        this.users = res.data.users
      } catch {
        this.notification = { type: 'error', message: 'Error al cargar usuarios' }
      } finally {
        this.loading = false
      }
    },
    canEdit(user) {
      if (user.id === this.currentUser.id) return false
      if (this.currentUser.role === 'admin' && user.role !== 'user') return false
      return true
    },
    canDelete(user) {
      if (user.id === this.currentUser.id) return false
      if (this.currentUser.role === 'admin' && user.role !== 'user') return false
      return true
    },
    startEdit(user) {
      this.editingId = user.id
      this.editForm = { username: user.username, email: user.email }
    },
    async saveEdit(userId) {
      try {
        await adminService.updateUser(userId, this.editForm)
        this.notification = { type: 'success', message: 'Usuario actualizado' }
        this.editingId = null
        await this.loadUsers()
      } catch (err) {
        this.notification = { type: 'error', message: err.response?.data?.error || 'Error al actualizar' }
      }
    },
    deleteUser(user) {
      this.deleteModal = { show: true, userId: user.id, username: user.username, loading: false }
    },
    async confirmDelete() {
      this.deleteModal.loading = true
      try {
        await adminService.deleteUser(this.deleteModal.userId)
        this.notification = { type: 'success', message: `Usuario ${this.deleteModal.username} eliminado` }
        this.deleteModal.show = false
        await this.loadUsers()
      } catch (err) {
        this.notification = { type: 'error', message: err.response?.data?.error || 'Error al eliminar' }
        this.deleteModal.show = false
      }
    },
    async changeRole(user, newRole) {
      if (newRole === user.role) return
      try {
        await adminService.changeRole(user.id, newRole)
        this.notification = { type: 'success', message: `${user.username}: ${user.role} → ${newRole}` }
        await this.loadUsers()
      } catch (err) {
        this.notification = { type: 'error', message: err.response?.data?.error || 'Error al cambiar rol' }
      }
    },
    roleBadgeClass(role) {
      return {
        superuser: 'text-purple-600',
        admin: 'text-amber-600',
        user: 'text-gray-500'
      }[role] || 'text-gray-500'
    },
    roleBadgeFullClass(role) {
      return {
        superuser: 'bg-purple-50 text-purple-700 border-purple-100',
        admin: 'bg-amber-50 text-amber-700 border-amber-100',
        user: 'bg-gray-50 text-gray-500 border-gray-200'
      }[role] || 'bg-gray-50 text-gray-500 border-gray-200'
    },
    roleSelectClass(role) {
      return {
        superuser: 'bg-purple-50 text-purple-700 border-purple-200',
        admin: 'bg-amber-50 text-amber-700 border-amber-200',
        user: 'bg-gray-50 text-gray-600 border-gray-200'
      }[role] || 'bg-gray-50 text-gray-600 border-gray-200'
    }
  }
}
</script>
