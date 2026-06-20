interface QuestionBadgesProps {
    isAiGenerated: boolean;
    isVerified: boolean;
}

export function QuestionBadges({ isAiGenerated, isVerified }: QuestionBadgesProps) {
    if (!isAiGenerated && !isVerified) {
        return null;
    }

    return (
        <span className="question-badges">
            {isAiGenerated && (
                <span className="badge badge-ai" title="AI generated question">AI Generated</span>
            )}
            {isVerified && (
                <span className="badge badge-verified" title="Verified question">Verified</span>
            )}
        </span>
    );
}
