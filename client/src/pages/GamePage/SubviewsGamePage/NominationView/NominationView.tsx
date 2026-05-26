import React from 'react';
import { Player } from '../../useGamePage';

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
        <div style={{ padding: '20px', border: '1px dashed #3f51b5', borderRadius: '4px', backgroundColor: '#e8eaf6' }}>
            <h2>Nomination Phase</h2>

            {isCurrentNominator ? (
                <div style={{ marginTop: '10px' }}>
                    <div style={{ color: '#3f51b5', fontWeight: 'bold', marginBottom: '8px' }}>
                        👉 YOU ANSWERED CORRECTLY! Select the next player to answer:
                    </div>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                        <select
                            value={selectedNomineeId}
                            onChange={(e) => setSelectedNomineeId(Number(e.target.value))}
                            style={{ padding: '8px', fontSize: '16px' }}
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
                            style={{ padding: '8px 16px', fontSize: '16px', cursor: 'pointer' }}
                        >
                            Nominate
                        </button>
                    </div>
                </div>
            ) : (
                <div style={{ marginTop: '10px', color: '#666', fontStyle: 'italic' }}>
                    👀 {nominatorName} is selecting the next target...
                </div>
            )}
        </div>
    );
}
