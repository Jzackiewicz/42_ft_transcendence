import { useSolarSystem } from './useSolarSystem';
import './useSolarSystem.css';

export default function SolarSystem() {
  const { canvasRef, randomize } = useSolarSystem();

  return (
    <div className="solar-system-tab" onClick={randomize}>
      <canvas ref={canvasRef} className="solar-system-canvas" />
    </div>
  );
}
