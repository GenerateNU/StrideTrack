import axios from "axios";
import { supabase } from "./supabase";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use(async (config) => {
  //dev token first
  const devToken = localStorage.getItem("dev-token");
  if (devToken) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${devToken}`;
    return config;
  }

  //otherwise supabase session
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;

  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default api;
