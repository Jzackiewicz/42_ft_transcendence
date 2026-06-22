import { cx } from '../../utils/cx';
import styles from './Avatar.module.css';

type Size = 'xs' | 'sm' | 'md' | 'lg';
type Bg = 'gradient' | 'cyan' | 'neutral';

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
};

interface AvatarProps {
    name: string;
    imageUrl?: string | null;
    size?: Size;
    bg?: Bg;
    bordered?: boolean;
    className?: string;
}

export function Avatar({
    name,
    imageUrl,
    size = 'sm',
    bg = 'gradient',
    bordered = false,
    className,
}: AvatarProps) {
    const initial = (name ?? '?')[0].toUpperCase();

    return (
        <div className={cx(styles.avatar, sizeClass[size], !imageUrl && bgClass[bg], bordered && styles.avatarBordered, className)}>
            {imageUrl ? (
                <img src={imageUrl} alt={`${name}'s avatar`} className={styles.avatarImg} />
            ) : (
                initial
            )}
        </div>
    );
}

export default Avatar;
