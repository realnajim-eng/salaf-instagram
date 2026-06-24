import { z } from "zod";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  OffthreadVideo,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Background } from "./Background";

export const verseSchema = z.object({
  theme: z.enum(["paradis", "enfer", "temps"]),
  verse_ar: z.string(),
  translation: z.string(),
  surah_ar: z.string(),
  ref: z.string(),
  audio: z.string(),
  // Étire la lecture de la vidéo de fond pour que son zoom intégré couvre
  // toute la durée du réel (au lieu de boucler/redémarrer). Calculé dans Root.
  videoPlaybackRate: z.number().optional(),
});

// Palettes sobres par thème (contenu sacré — rien de criard)
const PALETTES = {
  paradis: {
    bg: "linear-gradient(160deg, #0b2a22 0%, #14503f 55%, #0b2a22 100%)",
    arabic: "#f7eecb",
    accent: "#d9b65c",
    sub: "#bfe3d2",
    trans: "#eef5f0",
  },
  enfer: {
    bg: "linear-gradient(160deg, #1a0808 0%, #5a1f1a 55%, #1a0808 100%)",
    arabic: "#f9ecdf",
    accent: "#e0a35a",
    sub: "#e3b6a8",
    trans: "#f6ebe4",
  },
  // Temps : sablier — sable doré sur fond sombre sobre
  temps: {
    bg: "linear-gradient(160deg, #14110a 0%, #2a2113 55%, #14110a 100%)",
    arabic: "#f6ecd2",
    accent: "#cda85a",
    sub: "#d8c9a3",
    trans: "#f2ece0",
  },
};

export const QuoteReel: React.FC<z.infer<typeof verseSchema>> = ({
  theme,
  verse_ar,
  translation,
  surah_ar,
  ref,
  audio,
  videoPlaybackRate,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const c = PALETTES[theme];

  const appear = (delay: number) => {
    const s = spring({ frame: frame - delay, fps, config: { damping: 200 } });
    return {
      opacity: interpolate(s, [0, 1], [0, 1]),
      transform: `translateY(${interpolate(s, [0, 1], [30, 0])}px)`,
    };
  };

  // Temps : zoom lent continu sur le sablier (image fixe), calé sur toute la
  // durée du réel — même principe que le zoom intégré du paradis, mais natif.
  const sablierZoom = interpolate(frame, [0, durationInFrames], [1.0, 1.14], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Fondu au noir sur la dernière seconde
  const outro = interpolate(
    frame,
    [durationInFrames - fps, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ background: "#000", opacity: outro }}>
      <Audio src={staticFile(audio)} />
      {/* Décor de fond. Temps : image fixe (sablier) avec zoom lent continu.
          Paradis/Enfer : vidéo réelle, zoom intégré étiré jusqu'à la fin de l'audio. */}
      {theme === "temps" ? (
        <Img
          src={staticFile("Sablier.png")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${sablierZoom})`,
            transformOrigin: "center center",
            filter: "brightness(1.28) saturate(1.08) contrast(1.02)",
          }}
        />
      ) : (
        <OffthreadVideo
          src={staticFile(`video/${theme}.mp4`)}
          muted
          {...(videoPlaybackRate ? { playbackRate: videoPlaybackRate } : { loop: true })}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            filter: "brightness(1.42) saturate(1.12) contrast(1.0)",
          }}
        />
      )}
      {/* Voile pour la lisibilité — léger pour le Paradis (lumineux), plus marqué pour l'Enfer */}
      <AbsoluteFill
        style={{
          background:
            theme === "enfer"
              ? "radial-gradient(125% 85% at 50% 45%, rgba(0,0,0,0.22) 40%, rgba(0,0,0,0.6) 100%)"
              : theme === "temps"
              ? "radial-gradient(135% 95% at 50% 45%, rgba(0,0,0,0.08) 55%, rgba(0,0,0,0.30) 100%)"
              : "radial-gradient(135% 95% at 50% 45%, rgba(0,0,0,0.12) 50%, rgba(0,0,0,0.42) 100%)",
        }}
      />
      <Background theme={theme} />

      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          padding: "80px 70px",
          fontFamily: "Poppins, sans-serif",
        }}
      >
       <div
        style={{
          width: "100%",
          maxWidth: 920,
          padding: "70px 60px",
          borderRadius: 44,
          background:
            theme === "enfer"
              ? "rgba(20,8,6,0.46)"
              : theme === "temps"
              ? "rgba(16,13,7,0.44)"
              : "rgba(6,18,12,0.20)",
          backdropFilter: "none",
          WebkitBackdropFilter: "none",
          border: `1px solid ${c.accent}44`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
       >
        {/* Nom de la sourate */}
        <div
          dir="rtl"
          style={{
            ...appear(0),
            fontFamily: "QuranKFGQPC, serif",
            fontSize: 44,
            color: c.accent,
            marginBottom: 70,
            textShadow: "0 2px 12px rgba(0,0,0,0.8), 0 0 4px rgba(0,0,0,0.6)",
          }}
        >
          {surah_ar}
        </div>

        {/* Verset arabe entre accolades coraniques ﴿ ﴾ */}
        <div
          dir="rtl"
          style={{
            ...appear(6),
            fontFamily: "QuranKFGQPC, serif",
            fontSize: 80,
            lineHeight: 2.15,
            color: c.arabic,
            textAlign: "center",
            marginBottom: 70,
            textShadow:
              "0 3px 22px rgba(0,0,0,0.85), 0 0 8px rgba(0,0,0,0.6), 0 1px 2px rgba(0,0,0,0.7)",
          }}
        >
          <span style={{ color: c.accent }}>﴿ </span>
          {verse_ar}
          <span style={{ color: c.accent }}> ﴾</span>
        </div>

        {/* Séparateur */}
        <div style={{ ...appear(14), width: 120, height: 3, background: c.accent, marginBottom: 50 }} />

        {/* Traduction du sens (libellée explicitement) */}
        <div style={{ ...appear(18), textAlign: "center", maxWidth: 880 }}>
          <div
            style={{
              fontSize: 22,
              letterSpacing: 2,
              textTransform: "uppercase",
              color: c.sub,
              marginBottom: 24,
            }}
          >
            Traduction du sens
          </div>
          <div
            style={{
              fontSize: 39,
              fontWeight: 400,
              lineHeight: 1.55,
              color: c.trans,
              fontStyle: "italic",
              textShadow: "0 2px 14px rgba(0,0,0,0.4)",
            }}
          >
            {translation}
          </div>
        </div>

        {/* Référence + source de la traduction */}
        <div style={{ ...appear(26), textAlign: "center", marginTop: 70 }}>
          <div style={{ fontSize: 30, color: c.accent }}>{ref}</div>
          <div style={{ fontSize: 20, color: c.sub, marginTop: 10 }}>
            Récitation : Mishary al-ʿAfāsī · Traduction du sens : Hamidullah
          </div>
        </div>
       </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
