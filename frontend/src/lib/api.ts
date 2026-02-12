import axios from "axios";
import { supabase } from "./supabase";
import { config } from "./config";
import { getDevToken } from "./dev";

const api = axios.create({
  baseURL: config.apiUrl,
  timeout: 30000,
});

api.interceptors.request.use(
  async (requestConfig) => {
    const devToken = getDevToken();

    if (devToken) {
      requestConfig.headers.Authorization = `Bearer ${devToken}`;
      return requestConfig;
    }

    // Otherwise use Supabase session
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;

    if (token) {
      requestConfig.headers.Authorization = `Bearer ${token}`;
    }

    return requestConfig;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = "/login";
      return Promise.reject(error);
    }

    if (error.response?.data?.detail) {
      error.message = error.response.data.detail;
    }

    return Promise.reject(error);
  }
);

export default api;
