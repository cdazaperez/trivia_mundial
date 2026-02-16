import axios from "axios";

const API_BASE = "http://localhost:8000/api";

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

// Matches
export const getMatches = (params?: {
  phase?: string;
  group?: string;
  matchday?: number;
}) => api.get("/matches/", { params });

export const getMatch = (id: number) => api.get(`/matches/${id}`);

export const updateMatchResult = (
  id: number,
  data: { home_score: number; away_score: number }
) => api.put(`/matches/${id}/result`, data);

export const getTeams = () => api.get("/matches/teams/all");

// Predictions
export const createPrediction = (data: {
  match_id: number;
  home_score: number;
  away_score: number;
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

export default api;
