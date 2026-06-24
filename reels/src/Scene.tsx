import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

/**
 * Décor partagé "même paysage, deux états".
 * Même géométrie (ciel, collines, arbres, rivière en perspective) déclinée :
 *  - paradis : jardin verdoyant + rivière d'eau qui coule
 *  - enfer   : le même décor calciné + rivière de lave
 */

type Theme = "paradis" | "enfer";

const W = 1080;
const H = 1920;
const HORIZON = 1000;

const SCENE = {
  paradis: {
    sky: ["#bfe9ff", "#7fc9e8", "#dff3e6"],
    sun: "rgba(255,250,225,0.95)",
    sunGlow: "rgba(255,245,200,0.7)",
    hills: ["#2f7d4f", "#246b43", "#1b5435"],
    ground: "#1c4f30",
    tree: "#143b24",
    treeCanopy: "#1f6b3e",
    river: ["#9fe8ff", "#4fb6e6", "#2b7fb8"],
    flow: "rgba(255,255,255,0.55)",
    burned: false,
  },
  enfer: {
    sky: ["#3a0d06", "#7a1f0c", "#2a0a05"],
    sun: "rgba(255,120,40,0.9)",
    sunGlow: "rgba(200,50,10,0.65)",
    hills: ["#2a1410", "#1d0d0a", "#120705"],
    ground: "#140907",
    tree: "#0a0504",
    treeCanopy: "#1a0c07",
    river: ["#ffd24a", "#ff7a1a", "#c21d05"],
    flow: "rgba(255,220,120,0.8)",
    burned: true,
  },
};

// Largeur de la rivière en perspective : étroite à l'horizon, large au premier plan
const halfWidth = (y: number) => {
  const t = (y - HORIZON) / (H - HORIZON); // 0 horizon → 1 bas
  return 26 + t * 230;
};
// Léger S de la rivière
const centerX = (y: number) => {
  const t = (y - HORIZON) / (H - HORIZON);
  return W / 2 + Math.sin(t * 2.4) * 70;
};

function riverPolygon() {
  const left: string[] = [];
  const right: string[] = [];
  for (let y = HORIZON; y <= H; y += 30) {
    left.push(`${centerX(y) - halfWidth(y)},${y}`);
    right.push(`${centerX(y) + halfWidth(y)},${y}`);
  }
  return [...left, ...right.reverse()].join(" ");
}

export const Scene: React.FC<{ theme: Theme }> = ({ theme }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const s = SCENE[theme];

  // Lave qui respire
  const pulse = 0.5 + 0.5 * Math.sin(t * 1.6);

  // Bandes d'écoulement le long de la rivière (descendent vers le spectateur)
  const bands = Array.from({ length: 16 }, (_, i) => {
    const prog = ((t * (s.burned ? 0.10 : 0.16) + i / 16) % 1);
    const y = HORIZON + prog * (H - HORIZON);
    const fade = Math.sin(prog * Math.PI);
    return { y, hw: halfWidth(y) * 0.82, cx: centerX(y), fade };
  });

  return (
    <AbsoluteFill>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
        <defs>
          <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={s.sky[0]} />
            <stop offset="60%" stopColor={s.sky[1]} />
            <stop offset="100%" stopColor={s.sky[2]} />
          </linearGradient>
          <linearGradient id="river" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={s.river[0]} />
            <stop offset="55%" stopColor={s.river[1]} />
            <stop offset="100%" stopColor={s.river[2]} />
          </linearGradient>
          <radialGradient id="sun" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={s.sun} />
            <stop offset="100%" stopColor="rgba(0,0,0,0)" />
          </radialGradient>
          <clipPath id="riverClip">
            <polygon points={riverPolygon()} />
          </clipPath>
        </defs>

        {/* Ciel */}
        <rect x="0" y="0" width={W} height={HORIZON + 40} fill="url(#sky)" />
        {/* Halo du soleil */}
        <circle cx={W / 2} cy={760} r={520} fill="url(#sun)" opacity={s.burned ? 0.7 + pulse * 0.25 : 0.85} />
        <circle cx={W / 2} cy={760} r={120} fill={s.sun} opacity={s.burned ? 0.55 : 0.9} />

        {/* Collines en couches (parallax lent) */}
        {s.hills.map((col, i) => {
          const k = i + 1;
          const base = HORIZON - 60 + i * 55;
          const drift = Math.sin(t * 0.15 + i) * 8;
          return (
            <path
              key={i}
              d={`M0 ${base + drift}
                  C ${W * 0.25} ${base - 70 + drift}, ${W * 0.45} ${base + 40 + drift}, ${W * 0.6} ${base - 20 + drift}
                  S ${W * 0.9} ${base + 30 + drift}, ${W} ${base - 10 + drift}
                  L ${W} ${HORIZON + 600} L 0 ${HORIZON + 600} Z`}
              fill={col}
              opacity={1 - i * 0.05}
            />
          );
        })}

        {/* Sol au premier plan */}
        <rect x="0" y={HORIZON} width={W} height={H - HORIZON} fill={s.ground} />

        {/* Rivière (eau ou lave) */}
        <polygon points={riverPolygon()} fill="url(#river)" />
        {/* Lueur de lave */}
        {s.burned && (
          <polygon points={riverPolygon()} fill="#ff5a12" opacity={0.25 + pulse * 0.35} style={{ mixBlendMode: "screen" }} />
        )}
        {/* Bandes d'écoulement */}
        <g clipPath="url(#riverClip)">
          {bands.map((b, i) => (
            <ellipse
              key={i}
              cx={b.cx}
              cy={b.y}
              rx={b.hw}
              ry={Math.max(4, b.hw * 0.14)}
              fill={s.flow}
              opacity={b.fade * (s.burned ? 0.7 : 0.5)}
            />
          ))}
        </g>

        {/* Arbres / silhouettes calcinées de chaque côté */}
        {[150, 300, 930, 780].map((x, i) => {
          const tall = 250 + (i % 2) * 90;
          const y0 = 1250 + (i % 2) * 120;
          const sway = Math.sin(t * 0.6 + i) * (s.burned ? 2 : 6);
          return (
            <g key={i} transform={`translate(${x} ${y0})`}>
              <rect x={-10} y={0} width={20} height={tall} fill={s.tree} transform={`skewX(${sway * 0.1})`} />
              {s.burned ? (
                // branches nues
                <>
                  <line x1="0" y1="40" x2={-60} y2={-10} stroke={s.tree} strokeWidth="8" />
                  <line x1="0" y1="80" x2={70} y2="30" stroke={s.tree} strokeWidth="8" />
                  <line x1="0" y1="20" x2={40} y2={-40} stroke={s.tree} strokeWidth="6" />
                </>
              ) : (
                <ellipse cx={0 + sway} cy={-30} rx={120} ry={130} fill={s.treeCanopy} />
              )}
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};
