
import { useMemo } from 'react';

function createStars() {
    return Array.from({ length: 100 }, () => ({
        x: Math.random() * 100,
        y: Math.random() * 100,
    }))
}

function Star({ x, y }: { x: number, y: number }) {
    return (
        <div className="star" style={{ left: `${x}%`, top: `${y}%` }} />
    )
}

function BlinkingSpaceBGDiv() {
    const stars = useMemo(() => createStars(), [])

    return (
        <div className="blinking-space-bg">
            {stars.map((star, index) => (
                <Star key={index} x={star.x} y={star.y} />
            ))}
        </div>
    )
}

export default BlinkingSpaceBGDiv;