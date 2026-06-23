export interface Player {
    id: number;
    display_name: string;
    seat_number: number;
    lives: number;
    points: number;
    answered_count: number;
    is_alive: boolean;
    is_online: boolean;
    total_answer_time_ms?: number;
    user_id?: number | null;
    avatar?: string | null;
}

export interface Question {
    id: number;
    question: {
        question_text: string;
        category: string;
        is_ai_generated: boolean;
        is_verified: boolean;
    };
    order_index: number;
}

export enum GameStatus {
    LOBBY = 'lobby',
    ANSWERING = 'answering',
    EVALUATION = 'evaluation',
    NOMINATION = 'nomination',
    GAME_OVER = 'game_over'
}

export interface AnswerAttempt {
    id: number;
    answer_text: string | null;
    is_timeout: boolean;
    is_correct: boolean | null;
    correct_answer?: string;
    player: number; // player ID
}

export interface GameSnapshot {
    session_uuid: string;
    current_status: GameStatus;
    current_player: number | null;
    host_player: number | null;
    last_correct_player: number | null;
    last_nominated_player: number | null;
    players: Player[];
    is_spectator?: boolean;
    current_question: Question | null;
    current_attempt: AnswerAttempt | null;
    answer_time_limit_ms: number;
    nomination_time_limit_ms: number;
    max_players: number;
    winner: number | null;
    end_reason: string | null;
    question_asked_count: number;
    total_questions_count: number;
    ai_questions_count: number;
    generated_questions_count: number;
    extra_questions_generated: boolean;
    current_attempt_started_at?: string | null;
    turn_deadline_at?: string | null;
    nomination_deadline_at?: string | null;
    evaluation_deadline_at?: string | null;
    server_time?: string | null;
}
