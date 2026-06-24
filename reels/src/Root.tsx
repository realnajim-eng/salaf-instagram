import { Composition, staticFile } from "remotion";
import { getAudioDurationInSeconds } from "@remotion/media-utils";
import { QuoteReel, verseSchema } from "./QuoteReel";
import verses from "../public/verses.json";

const FPS = 30;

// Polices : KFGQPC (mushaf de Médine, arabe) + Poppins (latin)
const fontCss = `
@font-face {
  font-family: 'QuranKFGQPC';
  src: url('${staticFile("fonts/UthmanicHafs.woff2")}') format('woff2');
  font-weight: normal;
}
@font-face {
  font-family: 'Poppins';
  src: url('${staticFile("fonts/Poppins-Bold.ttf")}') format('truetype');
  font-weight: 700;
}
`;

if (typeof document !== "undefined") {
  const style = document.createElement("style");
  style.innerHTML = fontCss;
  document.head.appendChild(style);
}

type Verse = {
  theme: "paradis" | "enfer" | "temps" | "tawhid" | "jugement" | "coran" | "patience";
  verse_ar: string;
  translation: string;
  surah_ar: string;
  ref: string;
  audio: string;
};

const sample = verses[0] as Verse;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Verse"
      component={QuoteReel}
      fps={FPS}
      width={1080}
      height={1920}
      schema={verseSchema}
      defaultProps={{
        theme: sample.theme,
        verse_ar: sample.verse_ar,
        translation: sample.translation,
        surah_ar: sample.surah_ar,
        ref: sample.ref,
        audio: sample.audio,
      }}
      // Durée = longueur de la récitation + 2,5 s (respiration + fondu sortant).
      // Tous les thèmes utilisent désormais un fond image fixe (zoom lent continu).
      calculateMetadata={async ({ props }) => {
        const dur = await getAudioDurationInSeconds(staticFile(props.audio));
        const durationInFrames = Math.ceil((dur + 2.5) * FPS);
        return { durationInFrames };
      }}
    />
  );
};
