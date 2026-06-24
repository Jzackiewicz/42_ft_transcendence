import { useEffect, useState } from 'react';
import { cx } from '../../utils/cx';
import { OnlineIndicator } from '../OnlineIndicator/OnlineIndicator';
import styles from './Avatar.module.css';

type Size = 'xs' | 'sm' | 'md' | 'lg';
type Bg = 'gradient' | 'cyan' | 'neutral' | 'accent';

const sizeClass: Record<Size, string> = {
    xs: styles.avatarXs,
    sm: styles.avatarSm,
    md: styles.avatarMd,
    lg: styles.avatarLg,
};

const bgClass: Record<Bg, string> = {
    gradient: styles.avatarGradient,
    cyan: styles.avatarCyan,
    neutral: styles.avatarNeutral,
    accent: styles.avatarAccent,
};

interface AvatarProps {
    name: string;
    imageUrl?: string | null;
    size?: Size;
    bg?: Bg;
    bordered?: boolean;
    userId?: number;
    className?: string;
    onClick?: (e: React.MouseEvent) => void;
}

export function Avatar({
    name,
    imageUrl,
    size = 'sm',
    bg = 'gradient',
    bordered = false,
    userId,
    className,
    onClick,
}: AvatarProps) {
    const initial = (name || '?')[0].toUpperCase();
    const [imgFailed, setImgFailed] = useState(false);

    useEffect(() => {
        setImgFailed(false);
    }, [imageUrl]);

    const showImage = !!imageUrl && !imgFailed;

    const bgVariant = bg === 'accent' ? styles.avatarAccent : !showImage && bgClass[bg];

    const circle = (
        <div
            className={cx(styles.avatar, sizeClass[size], bgVariant, bordered && styles.avatarBordered, onClick && styles.avatarClickable, className)}
            onClick={onClick}
        >
            {showImage ? (
                <img
                    src={imageUrl!}
                    alt={`${name}'s avatar`}
                    className={styles.avatarImg}
                    onError={() => setImgFailed(true)}
                />
            ) : (
                initial
            )}
        </div>
    );

    if (userId === undefined) return circle;

    return (
        <span className={styles.avatarPresence}>
            {circle}
            <OnlineIndicator userId={userId} />
        </span>
    );
}

export default Avatar;
