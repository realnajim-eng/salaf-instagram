import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useMemo } from "react";

// PRNG déterministe (mulberry32) — mêmes particules à chaque rendu, pas de scintillement
function mulberry32(seed: number) {
  return function () {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

type Theme = "paradis" | "enfer" | "temps";

const CONF = {
  paradis: { count: 45, color: "rgba(245,233,200,", speed: 24, size: [3, 9], glow: "rgba(40,120,90,0.55)" },
  enfer: { count: 60, color: "rgba(240,150,70,", speed: 60, size: [2, 7], glow: "rgba(150,40,20,0.6)" },
  // Grains de sable dorés, fins et lents — ambiance "sablier"
  temps: { count: 40, color: "rgba(222,196,138,", speed: 18, size: [2, 6], glow: "rgba(120,95,40,0.5)" },
};

export const Background: React.FC<{ theme: Theme }> = ({ theme }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const conf = CONF[theme];

  const particles = useMemo(() => {
    const rng = mulberry32(theme === "enfer" ? 7 : theme === "temps" ? 17 : 42);
    return Array.from({ length: conf.count }, () => ({
      x: rng(),
      size: conf.size[0] + rng() * (conf.size[1] - conf.size[0]),
      speed: conf.speed * (0.6 + rng() * 0.9),
      offset: rng() * height,
      driftAmp: 20 + rng() * 60,
      driftFreq: 0.3 + rng() * 0.6,
      phase: rng() * Math.PI * 2,
      maxOp: 0.25 + rng() * 0.5,
    }));
  }, [theme, conf, height]);

  // Lueur radiale qui respire (bas pour l'enfer, centre pour le paradis)
  const pulse = 0.5 + 0.5 * Math.sin(t * 0.8);
  const glowY = theme === "enfer" ? "100%" : "42%";

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {/* Lueur d'ambiance */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% ${glowY}, ${conf.glow}, transparent 60%)`,
          opacity: 0.55 + pulse * 0.35,
        }}
      />
      {/* Particules : montent du bas, dérive latérale sinusoïdale */}
      {particles.map((p, i) => {
        const travel = (p.offset + t * p.speed) % (height + 60);
        const y = height + 30 - travel;
        const x = p.x * width + Math.sin(t * p.driftFreq + p.phase) * p.driftAmp;
        const fade = Math.sin((travel / (height + 60)) * Math.PI); // apparait/disparait en douceur
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: p.size,
              height: p.size,
              borderRadius: "50%",
              background: `${conf.color}${(p.maxOp * fade).toFixed(3)})`,
              filter: `blur(${theme === "enfer" ? 0.5 : 1}px)`,
              boxShadow: `0 0 ${p.size * 2}px ${conf.color}${(p.maxOp * fade * 0.8).toFixed(3)})`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
