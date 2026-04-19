# Planning Directory
| Method | Pros | Cons |
|------|------|------|
| **Email + Password**<br><br>User signs up and logs in with email and password | - Familiar and simple for users to understand<br>- Works without any third-party apps | - Users may forget passwords<br>- Password security must be handled (Supabase handles hashing, storage, resets, etc.) |
| **Passwordless (Magic Link)**<br><br>User enters email, receives a link, and clicks it to log in | - No password to forget or steal | - Slower than typing a password<br>- Can be cumbersome for users |
| **OAuth (Login through third-party service)**<br><br>Supabase supports many providers (e.g., Google, GitHub, Apple, Facebook, etc.)<br><br>Users click “Login with [provider]”; the provider confirms identity, Supabase trusts the provider, and the user is logged in | - Very fast login experience<br>- No passwords to manage | - Depends on third-party services<br>- Risk of account compromise at the provider level |
| **Two-Factor Authentication (Phone number + one-time code)**<br><br>User enters phone number, receives a one-time code, enters the code, and logs in | - No password required<br>- Works well for mobile apps (users already on their phone) | - SMS delivery issues<br>- Costs money at scale |
| **Enterprise / Custom SSO**<br><br>Used by companies and institutions to log in with organization-managed accounts | - One login for everything<br>- IT departments handle account security<br>- Admins can enable or revoke access instantly | - Requires company or institution-managed accounts<br>- Smaller teams may not have SSO<br>- Often behind a paywall |


**Sign Up + Log In token flows/overall overview:** ![](strideTrackAuthWorkFlow.png)

**Chosen model and reasoning:** We chose OAuth login/signup because it is the simplest for users. 

## Implementation plan for OAuth login/signup

1. **Design the Supabase Database** (need to create a Supabase project for this)
   - Email
   - Password
   - Name
   - Additional data (Team, Role)
   - Set up RLS policies for who can access what data
     - Example: a person who is a **Coach** for the **Northeastern Track Team** can access the running times for anyone who is a member of that team
     - Each athlete can only view their own data

2. **Configure the Supabase Auth settings**
   - Set redirect URLs (deep URLs for mobile apps)
     - Tokens will lock the redirect URL
   - Enable OAuth providers (Google) in Supabase

3. **Create the signup/login UI**
   - Add a button to request sign-in with OAuth
   - Request the redirect link to sign in with Google
   - Display the given URL from the backend
   - User signs in with Google (Google receives credentials)
   - Send Supabase tokens (access + refresh) to the backend for future requests

4. **Implement backend**
   - Request Google OAuth redirect URL from Supabase with:
     - Provider (Google)
     - Callback URL (frontend)
     - Requested user info (email, name, etc.)
   - Send the redirect URL to the frontend
   - Store Supabase tokens received from the frontend
   - Use these tokens with FastAPI for future Supabase requests

5. **Supabase**
   - Request redirect URL from Google and



**In the future:**
- Adding usernames?
- Player accounts and teams
- Email and password on top of the OAuth
- Figure out if we can bypass the frontend or if we need to do the traditional username + password so that we can use the fastAPI backend as a middleman

