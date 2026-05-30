/**
 * Type definitions for WearLens application
 */

export interface User {
  id: number
  email: string
  username: string
  first_name: string
  last_name: string
  role: 'MERCHANT' | 'CUSTOMER' | 'ADMIN'
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access: string
  refresh: string
  user: User
}

export interface Store {
  id: number
  name: string
  description: string
  integration_type: 'SHOPIFY' | 'CSV' | 'MANUAL'
  shopify_domain: string
  owner: number
  owner_email: string
  product_count: number
  is_active: boolean
  last_synced_at: string | null
  created_at: string
  updated_at: string
}

export interface Product {
  id: number
  title: string
  handle: string
  product_url: string
  image_url: string
  price: number
  vendor: string
  tags: string
  tag_list: string[]
  external_id: string
  store: number
  store_name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UserImage {
  id: number
  user: number
  user_email: string
  original_path: string
  original_url: string
  processed_path: string
  processed_url: string
  original_width: number | null
  original_height: number | null
  processed_width: number | null
  processed_height: number | null
  file_size: number | null
  mime_type: string
  consent_given: boolean
  status: 'PENDING' | 'UPLOADING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  error_message: string
  created_at: string
  updated_at: string
  processed_at: string | null
}

export interface Generation {
  id: number
  session: number | null
  user: number
  user_email: string
  user_image: number
  product: number
  product_title: string
  prompt: string
  mask_type: string
  output_path: string
  output_url: string
  status: 'QUEUED' | 'PROCESSING' | 'SUCCEEDED' | 'FAILED'
  error_message: string
  openai_request_id: string
  openai_model: string
  processing_time_seconds: number | null
  celery_task_id: string
  is_complete: boolean
  created_at: string
  updated_at: string
  started_at: string | null
  completed_at: string | null
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface UploadPrepareResponse {
  image_id: number
  upload_url: string
  upload_fields: Record<string, string>
  expires_in: number
}

export interface ApiError {
  error?: string
  detail?: string
  [key: string]: unknown
}
