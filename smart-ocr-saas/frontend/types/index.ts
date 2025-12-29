// User types
export interface User {
  id: string
  username: string
  display_name: string
  email?: string
  role: 'admin' | 'user'
  auth_type: 'local' | 'ldap'
  is_active: boolean
  created_at: string
  last_login?: string
}

// OCR Task types
export interface OCRTask {
  id: string
  user_id: string
  original_filename: string
  file_type: 'image' | 'pdf'
  file_size: number
  page_count: number
  status: 'uploaded' | 'processing' | 'completed' | 'failed'
  progress: number
  error_message?: string
  created_at: string
  updated_at: string
}

// OCR Result types
export interface StructuredField {
  key: string
  value: string
  confidence: number
}

export interface TableData {
  headers: string[]
  rows: string[][]
}

export interface StructuredData {
  type?: string
  fields: StructuredField[]
  tables: TableData[]
}

export interface OCRResult {
  id: string
  task_id: string
  page_number: number
  extracted_text: string
  structured_data?: StructuredData
  confidence: number
  created_at: string
  updated_at: string
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface ListResponse<T> {
  items: T[]
  total: number
}

export interface TokenResponse {
  access_token: string
  token_type: string
}
