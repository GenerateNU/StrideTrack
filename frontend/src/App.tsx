import { useAuth } from './hooks/useAuth'
import api from './lib/api'

function App() {
  const { session, loading, signInWithGoogle, signOut } = useAuth()

  const testApi = async () => {
    const { data } = await api.get('/api/auth/me')
    console.log(data)
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