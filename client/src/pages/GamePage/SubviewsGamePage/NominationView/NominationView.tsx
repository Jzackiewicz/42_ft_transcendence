import React, { useState, useEffect } from 'react';
import { Player } from '../../useGamePage';
import './NominationView.css';

interface NominationViewProps {
    isCurrentNominator: boolean;
    nominatorName: string;
    eligiblePlayers: Player[];
    onNominatePlayer: (targetPlayerId: number) => void;
}

export function NominationView({
    isCurrentNominator,
    nominatorName,
    eligiblePlayers,
    onNominatePlayer
}: NominationViewProps) {
    const [localSelectedId, setLocalSelectedId] = useState<number | ''>('');

    useEffect(() => {
        if (eligiblePlayers.length > 0) {
            if (!localSelectedId || !eligiblePlayers.some(p => p.id === localSelectedId)) {
                setLocalSelectedId(eligiblePlayers[0].id);
            }
        } else {
            setLocalSelectedId('');
        }
    }, [eligiblePlayers, localSelectedId]);

    const handleSubmit = () => {
        if (localSelectedId !== '') {
            onNominatePlayer(localSelectedId);
        }
    };

    return (
        <div className="nomination-view-container">
            <h2>Nomination Phase</h2>

            {isCurrentNominator ? (
                <div className="nomination-active-prompt">
                    <div className="nomination-prompt-label">
                        👉 Select the next player to answer:
                    </div>
                    <div className="nomination-controls">
                        <select
                            value={localSelectedId}
                            onChange={(e) => setLocalSelectedId(Number(e.target.value))}
                            className="nomination-select"
                        >
                            {eligiblePlayers.map((player) => (
                                <option key={player.id} value={player.id}>
                                    {player.display_name} ({player.lives} lives, {player.points} pts)
                                </option>
                            ))}
                        </select>
                        <button
                            onClick={handleSubmit}
                            disabled={!localSelectedId}
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

