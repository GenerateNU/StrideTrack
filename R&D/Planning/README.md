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