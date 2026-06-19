import React from 'react';
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
    nominatorName
}: NominationViewProps) {
    return (
        <div className="nomination-view-container">
            {isCurrentNominator ? (
                <div className="nomination-active-prompt">
                    <div className="nomination-prompt-label">
                        👉 Click on any player in the sidebar list to nominate them for the next turn!
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
export default NominationView;

