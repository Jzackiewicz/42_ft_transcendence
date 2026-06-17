import { useEffect, useRef, useCallback } from 'react';

// ── Types ────────────────────────────────────────────────────────
export interface Sun {
  cx: number; cy: number; r: number; isSun: true;
}

export interface OrbitalPlanet {
  cx: number; cy: number;
  orbitR: number; orbitSpeed: number; angle: number;
  r: number; color: string; glow: string;
  shape: 'circle' | 'ring' | 'hex' | 'diamond' | 'star';
  label: string; isSun?: false;
}

export type Planet = Sun | OrbitalPlanet;

// ── Non-color constants ──────────────────────────────────────────
const SUN_R             = 20;
const SUN_GLOW_FACTOR   = 4.5;
const SUN_PULSE_AMP     = 0.04;
const SUN_PULSE_FREQ    = 0.02;
const ORBIT_RING_WIDTH  = 1;
const PLANET_GLOW_FACTOR = 4;
const RING_TILT         = 0.5;
const BAND_OPACITY      = '55';
const ATMO_OPACITY      = '55';
const SPEED_MIN         = 0.001;
const SPEED_RANGE       = 0.012;
const PALETTE_SIZE      = 10;

const INITIAL_PLANETS: Omit<OrbitalPlanet, 'cx' | 'cy' | 'color' | 'glow'>[] = [
  { orbitR: 52,  orbitSpeed: 0.009,  angle: 0.4, r: 7,  shape: 'circle',  label: 'P1' },
  { orbitR: 88,  orbitSpeed: 0.006,  angle: 2.1, r: 9,  shape: 'ring',    label: 'P2' },
  { orbitR: 126, orbitSpeed: 0.004,  angle: 4.2, r: 7,  shape: 'hex',     label: 'P3' },
  { orbitR: 164, orbitSpeed: 0.0028, angle: 1.0, r: 10, shape: 'diamond', label: 'P4' },
  { orbitR: 202, orbitSpeed: 0.002,  angle: 3.5, r: 6,  shape: 'star',    label: 'P5' },
];

// ── CSS var reader ───────────────────────────────────────────────
function cssVar(el: Element, name: string): string {
  return getComputedStyle(el).getPropertyValue(name).trim();
}

// ── Helpers ──────────────────────────────────────────────────────
function hexToRgb(hex: string): [number, number, number] {
  return [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)];
}

function rgbLighten(hex: string, f: number): string {
  const [r, g, b] = hexToRgb(hex);
  return `rgb(${Math.min(255, (r + f * 255) | 0)},${Math.min(255, (g + f * 255) | 0)},${Math.min(255, (b + f * 255) | 0)})`;
}

function rgbDarken(hex: string, f: number): string {
  const [r, g, b] = hexToRgb(hex);
  return `rgb(${(r * (1 - f)) | 0},${(g * (1 - f)) | 0},${(b * (1 - f)) | 0})`;
}

function randomizePlanets(planets: Planet[], palette: [string, string][]) {
  const used = new Set<number>();
  (planets.slice(1) as OrbitalPlanet[]).forEach((p) => {
    let idx: number;
    do { idx = Math.floor(Math.random() * palette.length); } while (used.has(idx));
    used.add(idx);
    [p.color, p.glow] = palette[idx];
    p.orbitSpeed = SPEED_MIN + Math.random() * SPEED_RANGE;
  });
}

// ── Hook ─────────────────────────────────────────────────────────
export function useSolarSystem() {
  const canvasRef  = useRef<HTMLCanvasElement>(null);
  const planetsRef = useRef<Planet[]>([]);
  const paletteRef = useRef<[string, string][]>([]);

  const randomize = useCallback(() => {
    randomizePlanets(planetsRef.current, paletteRef.current);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const planets = planetsRef.current;
    let W: number, H: number, raf: number;
    let sunCore   = { center: '', mid: '', edge: '', glowMid: '', glowOuter: '' };
    let orbitRing = '';

    function init() {
      W = canvas!.width  = canvas!.offsetWidth;
      H = canvas!.height = canvas!.offsetHeight;
      const cx = W * 0.5;
      const cy = H * 0.6;

      const c = (name: string) => cssVar(canvas!, name);
      sunCore   = { center: c('--sun-core-center'), mid: c('--sun-core-mid'), edge: c('--sun-core-edge'), glowMid: c('--sun-glow-mid'), glowOuter: c('--sun-glow-outer') };
      orbitRing = c('--orbit-ring');
      paletteRef.current = Array.from({ length: PALETTE_SIZE }, (_, i) => [c(`--pal-${i}-color`), c(`--pal-${i}-glow`)] as [string, string]);

      planets.length = 0;
      planets.push({ cx, cy, r: SUN_R, isSun: true });
      INITIAL_PLANETS.forEach((p, i) =>
        planets.push({ ...p, cx, cy, color: c(`--p${i + 1}-color`), glow: c(`--p${i + 1}-glow`) })
      );
    }

    function draw(t: number) {
      const ctx = canvas!.getContext('2d')!;
      ctx.clearRect(0, 0, W, H);

      const sun = planets[0] as Sun;

      // Orbit rings
      (planets.slice(1) as OrbitalPlanet[]).forEach((p) => {
        ctx.beginPath();
        ctx.arc(p.cx, p.cy, p.orbitR, 0, Math.PI * 2);
        ctx.strokeStyle = orbitRing;
        ctx.lineWidth = ORBIT_RING_WIDTH;
        ctx.stroke();
      });

      // Sun glow
      const pulse = 1 + SUN_PULSE_AMP * Math.sin(t * SUN_PULSE_FREQ);
      const glowR = sun.r * SUN_GLOW_FACTOR * pulse;
      const sg = ctx.createRadialGradient(sun.cx, sun.cy, 0, sun.cx, sun.cy, glowR);
      sg.addColorStop(0,    sunCore.center);
      sg.addColorStop(0.15, sunCore.glowMid);
      sg.addColorStop(0.4,  sunCore.glowOuter);
      sg.addColorStop(1,    'transparent');
      ctx.beginPath(); ctx.arc(sun.cx, sun.cy, glowR, 0, Math.PI * 2);
      ctx.fillStyle = sg; ctx.fill();

      // Sun core
      const sc = ctx.createRadialGradient(sun.cx, sun.cy, 0, sun.cx, sun.cy, sun.r);
      sc.addColorStop(0,   sunCore.center);
      sc.addColorStop(0.4, sunCore.mid);
      sc.addColorStop(1,   sunCore.edge);
      ctx.beginPath(); ctx.arc(sun.cx, sun.cy, sun.r, 0, Math.PI * 2);
      ctx.fillStyle = sc; ctx.fill();

      // Planets
      (planets.slice(1) as OrbitalPlanet[]).forEach((p) => {
        p.angle += p.orbitSpeed;
        const px = p.cx + Math.cos(p.angle) * p.orbitR;
        const py = p.cy + Math.sin(p.angle) * p.orbitR;
        const gr = p.r * PLANET_GLOW_FACTOR;

        const pg = ctx.createRadialGradient(px, py, 0, px, py, gr);
        pg.addColorStop(0, p.glow); pg.addColorStop(1, 'transparent');
        ctx.beginPath(); ctx.arc(px, py, gr, 0, Math.PI * 2);
        ctx.fillStyle = pg; ctx.fill();

        if (p.shape === 'ring') {
          ctx.save(); ctx.translate(px, py); ctx.rotate(RING_TILT);
          ctx.beginPath(); ctx.ellipse(0, 0, p.r * 2.5, p.r * 0.52, 0, Math.PI, Math.PI * 2);
          ctx.strokeStyle = p.color + '77'; ctx.lineWidth = 2.5; ctx.stroke();
          ctx.beginPath(); ctx.ellipse(0, 0, p.r * 1.95, p.r * 0.38, 0, Math.PI, Math.PI * 2);
          ctx.strokeStyle = p.color + '44'; ctx.lineWidth = 1.2; ctx.stroke();
          ctx.restore();
        }

        const hl = ctx.createRadialGradient(px - p.r * 0.38, py - p.r * 0.38, p.r * 0.05, px, py, p.r);
        hl.addColorStop(0, rgbLighten(p.color, 0.65));
        hl.addColorStop(0.4, p.color);
        hl.addColorStop(1, rgbDarken(p.color, 0.6));
        ctx.beginPath(); ctx.arc(px, py, p.r, 0, Math.PI * 2);
        ctx.fillStyle = hl; ctx.fill();

        if (p.r >= 8) {
          ctx.save(); ctx.beginPath(); ctx.arc(px, py, p.r, 0, Math.PI * 2); ctx.clip();
          const rot = p.angle * 0.04;
          ([[0.3, 0.14], [-0.28, 0.1], [0.52, 0.09]] as [number, number][]).forEach(([off, w]) => {
            ctx.beginPath();
            ctx.ellipse(px, py + off * p.r, p.r, p.r * w, rot, 0, Math.PI * 2);
            ctx.fillStyle = rgbDarken(p.color, 0.3) + BAND_OPACITY; ctx.fill();
          });
          ctx.restore();
        }

        ctx.beginPath(); ctx.arc(px, py, p.r, 0, Math.PI * 2);
        ctx.strokeStyle = rgbLighten(p.color, 0.3) + ATMO_OPACITY;
        ctx.lineWidth = 1.5; ctx.stroke();

        if (p.shape === 'ring') {
          ctx.save(); ctx.translate(px, py); ctx.rotate(RING_TILT);
          ctx.beginPath(); ctx.ellipse(0, 0, p.r * 2.5, p.r * 0.52, 0, 0, Math.PI);
          ctx.strokeStyle = p.color + '77'; ctx.lineWidth = 2.5; ctx.stroke();
          ctx.beginPath(); ctx.ellipse(0, 0, p.r * 1.95, p.r * 0.38, 0, 0, Math.PI);
          ctx.strokeStyle = p.color + '44'; ctx.lineWidth = 1.2; ctx.stroke();
          ctx.restore();
        }
      });

      raf = requestAnimationFrame(draw);
    }

    const resizeObserver = new ResizeObserver(init);
    resizeObserver.observe(canvas);
    init();
    raf = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(raf);
      resizeObserver.disconnect();
    };
  }, []);

  return { canvasRef, randomize };
}
