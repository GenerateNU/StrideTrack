export interface Profile {
  profile_id: string;
  auth_user_id: string;
  email: string;
  name: string;
  role: "coach" | "athlete";
  created_at: string;
}

export interface Coach {
  coach_id: string;
  profile: Profile;
  created_at: string;
}
