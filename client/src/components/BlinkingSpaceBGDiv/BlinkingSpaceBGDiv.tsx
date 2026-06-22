
import { useMemo } from 'react';
import styles from './BlinkingSpaceBGDiv.module.css';

function createStars() {
    return Array.from({ length: 100 }, () => ({
        x: Math.random() * 100,
        y: Math.random() * 100,
    }))
}

function Star({ x, y }: { x: number, y: number }) {
    return (
        <div className={styles.star} style={{ left: `${x}%`, top: `${y}%` }} />
    )
}

function BlinkingSpaceBGDiv() {
    const stars = useMemo(() => createStars(), [])

    return (
        <div className={styles.bg}>
            {stars.map((star, index) => (
                <Star key={index} x={star.x} y={star.y} />
            ))}
        </div>
    )
}

export default BlinkingSpaceBGDiv;