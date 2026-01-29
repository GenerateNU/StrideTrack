import { supabase } from './supabase'

const API_URL = import.meta.env.VITE_API_URL

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const { data: { session } } = await supabase.auth.getSession()

  return fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${session?.access_token}`,
      'Content-Type': 'application/json'
    }
  })
}