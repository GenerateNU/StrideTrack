import { useAuth } from './hooks/useAuth'
import { apiFetch } from './lib/api'

function App() {
  const { session, loading, signInWithGoogle, signOut } = useAuth()

  const testApi = async () => {
    const res = await apiFetch('/api/auth/me')
    const data = await res.json()
    console.log(data)  // Check browser console
  }

  if (loading) return <div>Loading...</div>

  return (
    <div>
      {session ? (
        <>
          <p>Logged in as {session.user.email}</p>
          <button onClick={testApi}>Test API</button>
          <button onClick={signOut}>Sign Out</button>
        </>
      ) : (
        <button onClick={signInWithGoogle}>Sign in with Google</button>
      )}
    </div>
  )
}

export default App