import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authService = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me')
}

export const documentService = {
  upload: (formData) => api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  list: () => api.get('/documents/list'),
  verify: (formData) => api.post('/documents/verify', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  delete: (id) => api.delete(`/documents/${id}`)
}

export const certificateService = {
  generate: () => api.post('/certificates/generate'),
  list: () => api.get('/certificates/list'),
  sign: (docId) => api.post(`/certificates/sign/${docId}`),
  verifySignature: (docId) => api.get(`/certificates/verify-signature/${docId}`),
  revoke: (certId) => api.post(`/certificates/revoke/${certId}`)
}

export default api