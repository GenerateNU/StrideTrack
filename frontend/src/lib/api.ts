import axios from "axios";
import { supabase } from "./supabase";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});
<<<<<<< HEAD

const ENV = import.meta.env.VITE_ENVIRONMENT;
||||||| 6b0286b
})
=======
>>>>>>> main

api.interceptors.request.use(async (config) => {
<<<<<<< HEAD
  if (ENV === "development") {
    //dev token first
    const devToken = localStorage.getItem("dev-token");
    if (devToken) {
      config.headers = config.headers ?? {};
      config.headers.Authorization = `Bearer ${devToken}`;
      return config;
    }
||||||| 6b0286b
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
=======
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
>>>>>>> main
  }
<<<<<<< HEAD
  //otherwise supabase session
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
||||||| 6b0286b
  return config
})
=======
  return config;
});
>>>>>>> main

<<<<<<< HEAD
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

||||||| 6b0286b
export default api
=======
>>>>>>> main
export default api;
