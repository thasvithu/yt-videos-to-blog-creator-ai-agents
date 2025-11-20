import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export interface GenerateRequest {
  channel_name: string
  video_title: string
  email?: string
}

export interface JobResponse {
  job_id: string
  status: string
  message: string
}

export interface JobStatus {
  job_id: string
  status: string
  progress: number
  created_at: string
  updated_at?: string
  completed_at?: string
  error_message?: string
  result?: BlogPost
}

export interface BlogPost {
  title: string
  markdown_content: string
  html_content?: string
  metadata?: any
  created_at: string
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const generateBlogPost = async (data: GenerateRequest): Promise<JobResponse> => {
  const response = await api.post('/generate', data)
  return response.data
}

export const getJobStatus = async (jobId: string): Promise<JobStatus> => {
  const response = await api.get(`/status/${jobId}`)
  return response.data
}

export const sendEmail = async (jobId: string, email: string) => {
  const response = await api.post('/send-email', { job_id: jobId, email })
  return response.data
}

export default api
