import React from 'react';
import { Player } from '../../useGamePage';
import './NominationView.css';

interface NominationViewProps {
    isCurrentNominator: boolean;
    nominatorName: string;
    eligiblePlayers: Player[];
    selectedNomineeId: number | '';
    setSelectedNomineeId: (id: number) => void;
    onNominatePlayer: () => void;
}

export function NominationView({
    isCurrentNominator,
    nominatorName,
    eligiblePlayers,
    selectedNomineeId,
    setSelectedNomineeId,
    onNominatePlayer
}: NominationViewProps) {
    return (
        <div className="nomination-view-container">
            <h2>Nomination Phase</h2>

            {isCurrentNominator ? (
                <div className="nomination-active-prompt">
                    <div className="nomination-prompt-label">
                        👉 YOU ANSWERED CORRECTLY! Select the next player to answer:
                    </div>
                    <div className="nomination-controls">
                        <select
                            value={selectedNomineeId}
                            onChange={(e) => setSelectedNomineeId(Number(e.target.value))}
                            className="nomination-select"
                        >
                            {eligiblePlayers.map((player) => (
                                <option key={player.id} value={player.id}>
                                    {player.display_name} ({player.lives} lives, {player.points} pts)
                                </option>
                            ))}
                        </select>
                        <button
                            onClick={onNominatePlayer}
                            disabled={!selectedNomineeId}
                            className="btn-nominate"
                        >
                            Nominate
                        </button>
                    </div>
                </div>
            ) : (
                <div className="nomination-spectator-waiting">
                    👀 {nominatorName} is selecting the next target...
                </div>
            )}
        </div>
    );
}

