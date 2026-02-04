import { useAuth } from './hooks/useAuth'
import { useCurrentUser } from './hooks/useCurrentUser'

function App() {
  const { session, loading, signInWithGoogle, signOut } = useAuth()
  const { user, loading: userLoading } = useCurrentUser()

  if (loading) return <div>Loading...</div>

  return (
    <div>
      {session ? (
        <>
          <p>Logged in as {session.user.email}</p>
          {userLoading ? (
            <p>Loading user data...</p>
          ) : (
            <p>Backend user ID: {user?.user_id}</p>
          )}
          <button onClick={signOut}>Sign Out</button>
        </>
      ) : (
        <button onClick={signInWithGoogle}>Sign in with Google</button>
      )}
    </div>
  )
}

export default App