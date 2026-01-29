import { useAuth } from '../hooks/useAuth'

export function AuthButton() {
  const { session, loading, signInWithGoogle, signOut } = useAuth()

  if (loading) return <button disabled>Loading...</button>

  return session ? (
    <div>
      <span>{session.user.email}</span>
      <button onClick={signOut}>Sign Out</button>
    </div>
  ) : (
    <button onClick={signInWithGoogle}>Sign in with Google</button>
  )
}