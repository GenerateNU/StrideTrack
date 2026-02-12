<<<<<<< HEAD
import { createClient } from "@supabase/supabase-js";
||||||| 6b0286b
import { createBrowserClient } from '@supabase/ssr'
=======
import { createBrowserClient } from "@supabase/ssr";
>>>>>>> main

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
<<<<<<< HEAD
  import.meta.env.VITE_SUPABASE_ANON_KEY,
);
// createClient used ot be createBrowserClient and supabase-js used to be ssr
||||||| 6b0286b
  import.meta.env.VITE_SUPABASE_ANON_KEY
)
=======
  import.meta.env.VITE_SUPABASE_ANON_KEY
);
>>>>>>> main
