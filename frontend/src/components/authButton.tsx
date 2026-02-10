// import { useAuth } from "../hooks/useAuth";

// export function AuthButton() {
//   const { mode, session, loading, loginWithGoogle, loginAsDev, logout } =
//     useAuth();

//   const env = import.meta.env.VITE_ENVIRONMENT; // or VITE_ENVIRONMENT if that's what you used

//   if (loading) return <button disabled>Loading...</button>;

//   if (mode === "google" && session) {
//     return (
//       <div>
//         <span>{session.user.email}</span>
//         <button onClick={logout}>Sign Out</button>
//       </div>
//     );
//   }

//   if (mode === "dev") {
//     return (
//       <div>
//         <span>Dev User</span>
//         <button onClick={logout}>Sign Out</button>
//       </div>
//     );
//   }

//   return (
//     <div style={{ display: "flex", gap: 8 }}>
//       <button onClick={loginWithGoogle}>Sign in with Google</button>
//       {env === "development" && (
//         <button onClick={loginAsDev}>Login as Dev</button>
//       )}
//     </div>
//   );
// }

import { useAuth } from "@/context/AuthenticationContext";

export function AuthButton() {
  const { session, loading, signInWithGoogle, signOut } = useAuth();

  if (loading) return <button disabled>Loading...</button>;

  return session ? (
    <div>
      <span>{session.user.email}</span>
      <button onClick={signOut}>Sign Out</button>
    </div>
  ) : (
    <button onClick={signInWithGoogle}>Sign in with Google</button>
  );
}
