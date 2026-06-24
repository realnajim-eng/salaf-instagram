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
  theme: z.enum(["paradis", "enfer", "temps", "tawhid", "jugement", "coran", "patience"]),
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
  // Tawḥīd : cosmos — voûte étoilée, bleu profond, or sobre
  tawhid: {
    bg: "linear-gradient(160deg, #05060f 0%, #0c1430 55%, #05060f 100%)",
    arabic: "#f4f1e4",
    accent: "#d6bd6e",
    sub: "#aebfdf",
    trans: "#eef1f8",
  },
  // Jugement : balance — image blanche conservée, écriture NOIRE pour ressortir
  jugement: {
    bg: "linear-gradient(160deg, #e9e9ea 0%, #f4f4f5 55%, #e9e9ea 100%)",
    arabic: "#141414",
    accent: "#7a5d22",
    sub: "#4a4a4a",
    trans: "#1c1c1c",
  },
  // Coran : le Livre d'Allah — muṣḥaf relié, parchemin & or sur fond sombre chaud
  coran: {
    bg: "linear-gradient(160deg, #120d07 0%, #2c2012 55%, #120d07 100%)",
    arabic: "#f6ecd2",
    accent: "#cda85a",
    sub: "#d8c9a3",
    trans: "#f2ece0",
  },
  // Patience : aube brumeuse sur les montagnes — bleu froid du petit matin,
  // or doux du jour qui se lève (l'aube après la nuit, fruit du ṣabr)
  patience: {
    bg: "linear-gradient(160deg, #0a0f16 0%, #1a2733 55%, #0a0f16 100%)",
    arabic: "#f3efe2",
    accent: "#d8c081",
    sub: "#b9cad6",
    trans: "#eef3f6",
  },
};

// Thèmes à fond clair : texte foncé, ombres légères (pas d'ombre noire)
const LIGHT_THEME: Record<string, boolean> = { jugement: true };

// Thèmes dont le fond est une image fixe (zoom lent continu), pas une vidéo.
const STILL_IMAGE: Record<string, string> = {
  temps: "Sablier.png",
  tawhid: "Cosmos.png",
  jugement: "Balance.png",
  coran: "Quran.jpg",
  patience: "Patience.jpg",
  paradis: "Paradis.jpg",
  enfer: "Enfer.jpg",
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
  const light = LIGHT_THEME[theme];

  // Ombres de texte : marquées (halo noir) sur fond sombre/vidéo pour la
  // lisibilité ; quasi nulles sur fond clair (texte noir sur blanc).
  const shTitle = light
    ? "0 1px 1px rgba(255,255,255,0.6)"
    : "0 2px 12px rgba(0,0,0,0.8), 0 0 4px rgba(0,0,0,0.6)";
  const shVerse = light
    ? "0 1px 2px rgba(255,255,255,0.55)"
    : "0 3px 22px rgba(0,0,0,0.85), 0 0 8px rgba(0,0,0,0.6), 0 1px 2px rgba(0,0,0,0.7)";
  const shTrans = light ? "none" : "0 2px 14px rgba(0,0,0,0.4)";

  const appear = (delay: number) => {
    const s = spring({ frame: frame - delay, fps, config: { damping: 200 } });
    return {
      opacity: interpolate(s, [0, 1], [0, 1]),
      transform: `translateY(${interpolate(s, [0, 1], [30, 0])}px)`,
    };
  };

  // Thèmes à image fixe (temps, tawhid) : zoom lent continu calé sur toute la
  // durée du réel — même principe que le zoom intégré du paradis, mais natif.
  const stillZoom = interpolate(frame, [0, durationInFrames], [1.0, 1.14], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const stillImage = STILL_IMAGE[theme];

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
      {/* Décor de fond. Temps/Tawḥīd : image fixe avec zoom lent continu.
          Paradis/Enfer : vidéo réelle, zoom intégré étiré jusqu'à la fin de l'audio. */}
      {stillImage ? (
        <Img
          src={staticFile(stillImage)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${stillZoom})`,
            transformOrigin: "center center",
            filter:
              theme === "tawhid"
                ? "brightness(1.0) saturate(1.08) contrast(1.05)"
                : theme === "jugement"
                ? // Balance : image laissée dans son état d'origine (blanc lumineux)
                  "none"
                : theme === "coran"
                ? // Muṣḥaf relié : on assombrit légèrement pour faire ressortir
                  // l'écriture claire posée par-dessus
                  "brightness(0.9) saturate(1.05) contrast(1.06)"
                : theme === "patience"
                ? // Aube brumeuse : luminosité relevée pour un matin plus clair
                  "brightness(1.18) saturate(1.06) contrast(1.03)"
                : theme === "paradis"
                ? // Vallée verdoyante : déjà lumineuse, on rehausse à peine
                  "brightness(1.06) saturate(1.1) contrast(1.04)"
                : theme === "enfer"
                ? // Vallée de lave : on garde l'obscurité dramatique, braises saturées
                  "brightness(1.02) saturate(1.12) contrast(1.06)"
                : "brightness(1.28) saturate(1.08) contrast(1.02)",
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
              : theme === "tawhid"
              ? "radial-gradient(135% 95% at 50% 45%, rgba(0,0,0,0.18) 45%, rgba(0,0,0,0.5) 100%)"
              : theme === "jugement"
              ? "radial-gradient(135% 95% at 50% 45%, rgba(255,255,255,0.0) 55%, rgba(255,255,255,0.35) 100%)"
              : theme === "coran"
              ? "radial-gradient(135% 95% at 50% 45%, rgba(0,0,0,0.22) 42%, rgba(0,0,0,0.58) 100%)"
              : theme === "patience"
              ? "radial-gradient(135% 95% at 50% 45%, rgba(0,0,0,0.20) 45%, rgba(0,0,0,0.55) 100%)"
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
              : theme === "tawhid"
              ? "rgba(7,11,28,0.52)"
              : theme === "jugement"
              ? "rgba(255,255,255,0.42)"
              : theme === "coran"
              ? "rgba(18,13,7,0.50)"
              : theme === "patience"
              ? "rgba(10,15,22,0.48)"
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
            textShadow: shTitle,
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
            textShadow: shVerse,
          }}
        >
          {/* Espace insécable : la parenthèse reste collée au 1er/dernier mot
              et ne se retrouve jamais seule sur une ligne */}
          <span style={{ color: c.accent }}>{"﴿ "}</span>
          {verse_ar}
          <span style={{ color: c.accent }}>{" ﴾"}</span>
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
              textShadow: shTrans,
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
