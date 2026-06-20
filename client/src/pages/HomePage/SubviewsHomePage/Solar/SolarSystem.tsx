import { useSolarSystem } from './useSolarSystem';
import styles from './useSolarSystem.module.css';

export default function SolarSystem() {
  const { canvasRef, randomize } = useSolarSystem();

  return (
    <div className={styles['solar-system-tab']} onClick={randomize}>
      <canvas ref={canvasRef} className={styles['solar-system-canvas']} />
    </div>
  );
}
