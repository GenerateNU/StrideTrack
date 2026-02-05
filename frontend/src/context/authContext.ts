import { createContext } from 'react'
import type { Session } from '@supabase/supabase-js'

export interface AuthContextType {
  session: Session | null
  loading: boolean
  signInWithGoogle: () => Promise<void>
  signOut: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)