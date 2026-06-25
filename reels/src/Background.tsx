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

type Theme =
  | "paradis" | "enfer" | "temps" | "tawhid" | "jugement" | "coran" | "patience"
  | "rahma" | "tawba" | "shukr" | "tawakkul" | "birr" | "tafakkur"
  | "mort" | "taqwa" | "faraj" | "rappel";

const CONF = {
  paradis: { count: 45, color: "rgba(245,233,200,", speed: 24, size: [3, 9], glow: "rgba(40,120,90,0.55)" },
  enfer: { count: 60, color: "rgba(240,150,70,", speed: 60, size: [2, 7], glow: "rgba(150,40,20,0.6)" },
  // Grains de sable dorés, fins et lents — ambiance "sablier"
  temps: { count: 40, color: "rgba(222,196,138,", speed: 18, size: [2, 6], glow: "rgba(120,95,40,0.5)" },
  // Tawḥīd : fine poussière d'étoiles bleutée, lente — voûte céleste
  tawhid: { count: 50, color: "rgba(205,220,255,", speed: 14, size: [1, 5], glow: "rgba(40,70,140,0.45)" },
  // Jugement : fond clair (image blanche) — fines particules sombres discrètes,
  // lueur quasi nulle pour ne pas salir le blanc
  jugement: { count: 32, color: "rgba(120,105,70,", speed: 15, size: [1, 4], glow: "rgba(150,140,110,0.12)" },
  // Coran : fine poussière dorée/parchemin, lente — lumière posée sur le muṣḥaf
  coran: { count: 38, color: "rgba(224,200,142,", speed: 14, size: [2, 6], glow: "rgba(125,95,40,0.42)" },
  // Patience : fine brume matinale bleu-pâle, très lente — l'aube qui se lève
  patience: { count: 44, color: "rgba(206,222,235,", speed: 12, size: [1, 5], glow: "rgba(120,150,180,0.40)" },
  // Miséricorde : fine poussière dorée douce, vert apaisant
  rahma: { count: 40, color: "rgba(232,210,150,", speed: 14, size: [2, 6], glow: "rgba(80,120,90,0.40)" },
  // Repentir : lueur d'aube orangée, lente
  tawba: { count: 42, color: "rgba(235,200,150,", speed: 14, size: [2, 6], glow: "rgba(150,90,50,0.40)" },
  // Gratitude : grains dorés chaleureux
  shukr: { count: 40, color: "rgba(235,205,140,", speed: 16, size: [2, 6], glow: "rgba(150,110,40,0.42)" },
  // Confiance : poussière bleu ciel, sereine
  tawakkul: { count: 44, color: "rgba(200,218,238,", speed: 13, size: [1, 5], glow: "rgba(60,100,150,0.40)" },
  // Piété filiale : poussière dorée tendre
  birr: { count: 38, color: "rgba(232,208,160,", speed: 13, size: [2, 6], glow: "rgba(140,100,60,0.38)" },
  // Méditation : poussière d'étoiles bleutée — voûte céleste
  tafakkur: { count: 50, color: "rgba(205,220,255,", speed: 14, size: [1, 5], glow: "rgba(40,70,140,0.45)" },
  // La mort : fines particules grises, sobres et silencieuses
  mort: { count: 34, color: "rgba(200,205,215,", speed: 12, size: [1, 5], glow: "rgba(90,100,115,0.35)" },
  // Crainte d'Allah : poussière bleu froid, montagne
  taqwa: { count: 42, color: "rgba(200,215,228,", speed: 12, size: [1, 5], glow: "rgba(70,110,150,0.38)" },
  // Espoir : grains dorés perçant l'ombre
  faraj: { count: 46, color: "rgba(238,215,150,", speed: 16, size: [2, 7], glow: "rgba(150,120,50,0.45)" },
  // Le rappel : lueur chaude de lampe, recueillement
  rappel: { count: 38, color: "rgba(230,205,140,", speed: 13, size: [2, 6], glow: "rgba(140,105,45,0.42)" },
};

export const Background: React.FC<{ theme: Theme }> = ({ theme }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const conf = CONF[theme];

  const particles = useMemo(() => {
    const SEEDS: Record<string, number> = {
      enfer: 7, temps: 17, tawhid: 23, jugement: 31, coran: 53, patience: 61,
      rahma: 71, tawba: 83, shukr: 89, tawakkul: 97, birr: 101, tafakkur: 103,
      mort: 107, taqwa: 109, faraj: 113, rappel: 127,
    };
    const rng = mulberry32(SEEDS[theme] ?? 42);
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
