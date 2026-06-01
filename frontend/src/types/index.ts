export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_admin: boolean;
  is_active: boolean;
}

export interface Team {
  id: number;
  name: string;
  code: string;
  group_name: string | null;
  flag_emoji: string | null;
}

export interface Match {
  id: number;
  match_number: number;
  phase: string;
  group_name: string | null;
  home_team: Team | null;
  away_team: Team | null;
  home_score: number | null;
  away_score: number | null;
  home_penalties: number | null;
  away_penalties: number | null;
  match_date: string;
  venue: string | null;
  is_finished: boolean;
  matchday: number | null;
}

export interface Prediction {
  id: number;
  match_id: number;
  home_score: number;
  away_score: number;
  home_penalties: number | null;
  away_penalties: number | null;
  points_earned: number;
  match?: Match;
}

export interface GroupPrediction {
  id: number;
  group_name: string;
  first_place_team: Team;
  second_place_team: Team;
  points_earned: number;
}

export interface BonusPrediction {
  id: number;
  prediction_type: string;
  team: Team | null;
  player_name: string | null;
  points_earned: number;
}

export interface LeaderboardEntry {
  user_id: number;
  username: string;
  full_name: string;
  total_points: number;
  exact_scores: number;
  correct_results: number;
  group_points: number;
  bonus_points: number;
}
