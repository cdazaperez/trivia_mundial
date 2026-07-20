import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

const api = axios.create({
  baseURL: API_BASE,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Auth
export const login = (username: string, password: string) =>
  api.post("/auth/login", { username, password });

export const register = (data: {
  username: string;
  email: string;
  password: string;
  full_name: string;
}) => api.post("/auth/register", data);

export const getMe = () => api.get("/auth/me");

export const changePassword = (data: {
  current_password: string;
  new_password: string;
}) => api.put("/auth/change-password", data);

export const adminResetPassword = (data: {
  username: string;
  new_password: string;
}) => api.put("/auth/admin/reset-password", data);

export const listUsers = () => api.get("/auth/users");
export const toggleUserActive = (userId: number) =>
  api.put(`/auth/admin/toggle-user/${userId}`);
export const toggleUserPayment = (userId: number) =>
  api.put(`/auth/admin/toggle-payment/${userId}`);
export const adminUpdateUser = (userId: number, data: {
  username?: string;
  email?: string;
  full_name?: string;
}) => api.put(`/auth/admin/update-user/${userId}`, data);

// Matches
export const getMatches = (params?: {
  phase?: string;
  group?: string;
  matchday?: number;
}) => api.get("/matches/", { params });

export const getMatch = (id: number) => api.get(`/matches/${id}`);

export const updateMatchResult = (
  id: number,
  data: { home_score: number; away_score: number; home_penalties?: number; away_penalties?: number }
) => api.put(`/matches/${id}/result`, data);

export const getTeams = () => api.get("/matches/teams/all");

// Predictions
export const createPrediction = (data: {
  match_id: number;
  home_score: number;
  away_score: number;
  home_penalties?: number;
  away_penalties?: number;
}) => api.post("/predictions/match", data);

export const getMyPredictions = (phase?: string) =>
  api.get("/predictions/match", { params: phase ? { phase } : {} });

export const getAllPredictionsForMatch = (matchId: number) =>
  api.get("/predictions/match/all", { params: { match_id: matchId } });

// Group predictions
export const createGroupPrediction = (data: {
  group_name: string;
  first_place_team_id: number;
  second_place_team_id: number;
}) => api.post("/predictions/group", data);

export const getMyGroupPredictions = () => api.get("/predictions/group");

// Bonus predictions
export const createBonusPrediction = (data: {
  prediction_type: string;
  team_id?: number;
  player_name?: string;
}) => api.post("/predictions/bonus", data);

export const getMyBonusPredictions = () => api.get("/predictions/bonus");

// Leaderboard
export const getLeaderboard = (phase?: string) =>
  api.get("/leaderboard/", { params: phase ? { phase } : {} });

export const getPhaseWinners = () => api.get("/leaderboard/phase-winners");

// Admin
export const resetAllResults = () => api.post("/matches/reset-all");
export const reseedData = () => api.post("/matches/reseed");
export const updateTeams = () => api.post("/matches/update-teams");
export const setBonusResult = (data: {
  prediction_type: string;
  team_id?: number;
  player_name?: string;
}) => api.post("/matches/bonus-result", data);
export const getBonusPredictionsSummary = (prediction_type: string) =>
  api.get(`/matches/bonus-predictions-summary?prediction_type=${prediction_type}`);

// Standings & Knockout
export const getKnockoutStatus = () => api.get("/matches/knockout-status");
export const generateKnockoutRound = (phase: string) =>
  api.post(`/matches/generate-knockout/${phase}`);
export const autoGenerateNext = () => api.post("/matches/auto-generate-next");
export const getGroupStandings = () => api.get("/matches/standings/");

// Audit
export const getAuditLog = (userId?: number) =>
  api.get("/predictions/audit-log", { params: userId ? { user_id: userId } : {} });
export const getBonusAudit = () => api.get("/predictions/bonus-audit");

export default api;
