import { useSolarSystem } from './useSolarSystem';
import styles from './SolarSystem.module.css';

interface SolarSystemProps {
  /** Uniform size multiplier. Default 1. */
  scale?: number;
}

export default function SolarSystem({ scale = 1 }: SolarSystemProps) {
  const { canvasRef } = useSolarSystem(scale);

  return (
    <div className={styles.wrapper}>
      <canvas ref={canvasRef} className={styles.canvas} />
    </div>
  );
}
