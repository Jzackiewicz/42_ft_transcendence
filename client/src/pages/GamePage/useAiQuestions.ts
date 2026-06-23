import { useState } from 'react';
import { generateExtraQuestions } from '../../api/gameWrapper';
import { GameSnapshot } from '../../types/Game';

// Host-triggered generation of extra AI questions for the session.
export function useAiQuestions(
    sessionUuid: string,
    gameState: GameSnapshot | null,
    setErrorMsg: (msg: string | null) => void
) {
    const [isGenerating, setIsGenerating] = useState(false);
    const alreadyGenerated = gameState?.extra_questions_generated ?? false;

    const requestAiQuestions = async () => {
        if (!sessionUuid || isGenerating || alreadyGenerated) {
            return;
        }
        setIsGenerating(true);
        setErrorMsg(null);
        try {
            await generateExtraQuestions(sessionUuid);
        } catch (err: any) {
            const detail = err?.response?.data?.error;
            setErrorMsg(
                Array.isArray(detail)
                    ? detail.join(' ')
                    : (detail || 'Failed to generate AI questions. Please try again.')
            );
        } finally {
            setIsGenerating(false);
        }
    };

    return {
        isGeneratingAiQuestions: isGenerating,
        aiQuestionsGenerated: alreadyGenerated,
        onRequestAiQuestions: requestAiQuestions,
    };
}
