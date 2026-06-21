import { useSolarSystem } from './useSolarSystem';
import styles from './useSolarSystem.module.css';

export default function SolarSystem() {
  const { canvasRef, randomize } = useSolarSystem();

  return (
    <div className={styles.solarSystemTab} onClick={randomize}>
      <canvas ref={canvasRef} className={styles.solarSystemCanvas} />
    </div>
  );
}
