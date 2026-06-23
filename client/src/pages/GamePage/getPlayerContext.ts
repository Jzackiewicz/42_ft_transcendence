import { GameSnapshot, Player } from '../../types/Game';

export interface PlayerContext {
    eligiblePlayers: Player[];
    currentPlayerObj: Player | undefined;
    isHost: boolean;
    hostPlayerId: number | null;
}

// Derives this client's relationship to the snapshot: which player they are,
// whether they host, and who is eligible for nomination.
export function getPlayerContext(
    gameState: GameSnapshot | null,
    myPlayerId: number | null,
    userId: number | undefined
): PlayerContext {
    const eligiblePlayers = gameState?.players.filter(p => p.is_alive) || [];

    const currentPlayerObj = myPlayerId !== null
        ? gameState?.players.find(p => p.id === myPlayerId)
        : gameState?.players.find(p => p.user_id !== null && p.user_id && p.user_id === userId);

    const sortedPlayers = [...(gameState?.players || [])].sort((a, b) => a.id - b.id);

    const isHost = gameState !== null &&
        ((myPlayerId !== null && gameState.host_player === myPlayerId) ||
         (myPlayerId === null && sortedPlayers.length > 0 && currentPlayerObj !== undefined && sortedPlayers[0].id === currentPlayerObj.id));

    const hostPlayerId = gameState?.host_player ?? (sortedPlayers.length > 0 ? sortedPlayers[0].id : null);

    return { eligiblePlayers, currentPlayerObj, isHost, hostPlayerId };
}
