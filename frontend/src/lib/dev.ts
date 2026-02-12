import { config } from "./config";

export function getDevToken(): string | undefined {
  return config.development.bypassAuth
    ? (localStorage.getItem(config.development.devTokenKey) ?? undefined)
    : undefined;
}

export function setDevToken(): void {
  localStorage.setItem(config.development.devTokenKey, "dev-token");
}

export function clearDevToken(): void {
  localStorage.removeItem(config.development.devTokenKey);
}
