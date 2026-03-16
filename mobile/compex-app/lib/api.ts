import { getToken } from './auth';

// Point to your existing CompEx API
// In dev, use your local IP. In prod, point to your deployed Vercel URL.
const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'https://your-compex-url.vercel.app';

interface RequestOptions extends RequestInit {
  skipAuth?: boolean;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { skipAuth = false, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers as Record<string, string>),
  };

  if (!skipAuth) {
    const token = await getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message ?? `HTTP ${response.status}`);
  }

  return response.json() as Promise<T>;
}

// ─── Auth endpoints ────────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    apiRequest<{ token: string; user: Record<string, unknown> }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      skipAuth: true,
    }),

  signup: (email: string, password: string, name: string) =>
    apiRequest<{ token: string; user: Record<string, unknown> }>('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
      skipAuth: true,
    }),

  me: () =>
    apiRequest<Record<string, unknown>>('/api/auth/me'),

  logout: () =>
    apiRequest('/api/auth/logout', { method: 'POST' }),
};

// ─── Problems endpoints ────────────────────────────────────────────────────
export const problemsApi = {
  list: (params?: { examType?: string; section?: string; difficulty?: number; page?: number }) => {
    const qs = new URLSearchParams(
      Object.entries(params ?? {}).reduce((acc, [k, v]) => {
        if (v !== undefined) acc[k] = String(v);
        return acc;
      }, {} as Record<string, string>)
    ).toString();
    return apiRequest<{ problems: unknown[]; total: number; page: number }>(`/api/problems${qs ? `?${qs}` : ''}`);
  },
};

// ─── Dashboard endpoints ───────────────────────────────────────────────────
export const dashboardApi = {
  stats: () =>
    apiRequest<{
      streak: number;
      totalSolved: number;
      accuracy: number;
      weeklyProgress: unknown[];
    }>('/api/dashboard/stats'),
};
