import axios from "axios";
import type { AxiosRequestConfig } from "axios";

const instance = axios.create({
  baseURL: "http://localhost:8000",
  withCredentials: true,
});

export const apiClient = async <T>(
  url: string,
  options?: RequestInit
): Promise<T> => {
  const config: AxiosRequestConfig = {
    url,
    method: options?.method as AxiosRequestConfig["method"],
    data: options?.body,
    headers: options?.headers as AxiosRequestConfig["headers"],
    ...(options?.signal ? { signal: options.signal } : {}),
  };

  const response = await instance.request<T>(config);
  return response.data;
};
