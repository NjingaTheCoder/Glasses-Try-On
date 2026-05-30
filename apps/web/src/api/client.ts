/**
 * API client for WearLens backend
 */
import axios, { AxiosError, AxiosInstance } from 'axios'
import type {
  AuthResponse,
  Generation,
  PaginatedResponse,
  Product,
  Store,
  UploadPrepareResponse,
  User,
  UserImage,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken) {
            try {
              const response = await axios.post(`${API_BASE_URL}/api/auth/token/refresh/`, {
                refresh: refreshToken,
              })
              const { access } = response.data
              localStorage.setItem('access_token', access)

              // Retry original request
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${access}`
                return axios.request(error.config)
              }
            } catch {
              // Refresh failed, logout
              localStorage.removeItem('access_token')
              localStorage.removeItem('refresh_token')
              window.location.href = '/login'
            }
          } else {
            // No refresh token, logout
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/api/auth/login/', {
      email,
      password,
    })
    return response.data
  }

  async register(data: {
    email: string
    username: string
    password: string
    password_confirm: string
    role: 'MERCHANT' | 'CUSTOMER'
  }): Promise<{ user: User; message: string }> {
    const response = await this.client.post('/api/auth/register/', data)
    return response.data
  }

  async getProfile(): Promise<User> {
    const response = await this.client.get<User>('/api/auth/profile/')
    return response.data
  }

  // Store endpoints
  async getStores(): Promise<PaginatedResponse<Store>> {
    const response = await this.client.get<PaginatedResponse<Store>>('/api/stores/')
    return response.data
  }

  async getStore(id: number): Promise<Store> {
    const response = await this.client.get<Store>(`/api/stores/${id}/`)
    return response.data
  }

  async createStore(data: { name: string; description?: string }): Promise<Store> {
    const response = await this.client.post<Store>('/api/stores/', data)
    return response.data
  }

  async shopifySync(
    storeId: number,
    data: { shopify_domain: string; shopify_access_token: string }
  ): Promise<{ message: string; stats: Record<string, number> }> {
    const response = await this.client.post(`/api/stores/${storeId}/shopify-sync/`, data)
    return response.data
  }

  async csvImport(
    storeId: number,
    file: File
  ): Promise<{ message: string; stats: Record<string, number> }> {
    const formData = new FormData()
    formData.append('csv_file', file)

    const response = await this.client.post(`/api/stores/${storeId}/csv-import/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  }

  // Product endpoints
  async getProducts(params?: {
    store_id?: number
    search?: string
  }): Promise<PaginatedResponse<Product>> {
    const response = await this.client.get<PaginatedResponse<Product>>('/api/products/', {
      params,
    })
    return response.data
  }

  async getProduct(id: number): Promise<Product> {
    const response = await this.client.get<Product>(`/api/products/${id}/`)
    return response.data
  }

  // User image endpoints
  async getUserImages(): Promise<PaginatedResponse<UserImage>> {
    const response = await this.client.get<PaginatedResponse<UserImage>>('/api/user-images/')
    return response.data
  }

  async getUserImage(id: number): Promise<UserImage> {
    const response = await this.client.get<UserImage>(`/api/user-images/${id}/`)
    return response.data
  }

  async prepareUpload(data: {
    filename: string
    consent_given: boolean
  }): Promise<UploadPrepareResponse> {
    const response = await this.client.post<UploadPrepareResponse>(
      '/api/user-images/prepare-upload/',
      data
    )
    return response.data
  }

  async completeUpload(imageId: number, success: boolean): Promise<{ message: string; image: UserImage }> {
    const response = await this.client.post(`/api/user-images/${imageId}/complete/`, {
      success,
    })
    return response.data
  }

  async deleteUserImage(id: number): Promise<void> {
    await this.client.delete(`/api/user-images/${id}/`)
  }

  // Try-on endpoints
  async createGeneration(data: {
    user_image_id: number
    product_id: number
    session_id?: number
    mask_type?: string
  }): Promise<{ message: string; generation: Generation }> {
    const response = await this.client.post('/api/tryon/', data)
    return response.data
  }

  async getGenerations(params?: {
    session_id?: number
    status?: string
  }): Promise<PaginatedResponse<Generation>> {
    const response = await this.client.get<PaginatedResponse<Generation>>('/api/generations/', {
      params,
    })
    return response.data
  }

  async getGeneration(id: number): Promise<Generation> {
    const response = await this.client.get<Generation>(`/api/generations/${id}/`)
    return response.data
  }

  // Upload helper for presigned URLs
  async uploadToSignedUrl(url: string, file: File): Promise<void> {
    await axios.put(url, file, {
      headers: {
        'Content-Type': file.type,
      },
    })
  }
}

export const apiClient = new ApiClient()
export default apiClient
