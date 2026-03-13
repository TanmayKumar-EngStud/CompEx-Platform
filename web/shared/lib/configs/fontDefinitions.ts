import {
   Roboto_Slab,
   Montserrat,
   Roboto,
   Nunito,
   Merriweather,
   Lora,
   Poppins,
   Raleway,
   Open_Sans,
   Lato,
   PT_Sans,
   Source_Sans_3,
} from "next/font/google";

const isDev = process.env.NODE_ENV === "development";

// All font loaders MUST be called at the top level for static analysis
const RobotoSlab = Roboto_Slab({ subsets: ["latin"], display: "swap", variable: "--font-primary-1" });
const MerriweatherFont = Merriweather({ subsets: ["latin"], display: "swap", variable: "--font-primary-2", weight: "300" });
const LoraFont = Lora({ subsets: ["latin"], display: "swap", variable: "--font-primary-3" });

const MontserratFont = Montserrat({ subsets: ["latin"], display: "swap", variable: "--font-secondary-1" });
const PoppinsFont = Poppins({ subsets: ["latin"], display: "swap", variable: "--font-secondary-2", weight: "300" });
const RalewayFont = Raleway({ subsets: ["latin"], display: "swap", variable: "--font-secondary-3" });

const RobotoFont = Roboto({ subsets: ["latin"], display: "swap", variable: "--font-body-1", weight: "100" });
const OpenSansFont = Open_Sans({ subsets: ["latin"], display: "swap", variable: "--font-body-2" });
const LatoFont = Lato({ subsets: ["latin"], display: "swap", variable: "--font-body-3", weight: "100" });

const NunitoFont = Nunito({ subsets: ["latin"], display: "swap", variable: "--font-accent-1" });
const PTSansFont = PT_Sans({ subsets: ["latin"], display: "swap", variable: "--font-accent-2", weight: "400" });
const SourceSansProFont = Source_Sans_3({ subsets: ["latin"], display: "swap", variable: "--font-accent-3" });

// In development, we alias secondary fonts to core fonts in the exported arrays 
// to potentially save some rendering/layout calculation time, 
// even though Next.js still pre-resolves the font files.
export const Pfonts = isDev ? [RobotoSlab, RobotoSlab, RobotoSlab] : [RobotoSlab, MerriweatherFont, LoraFont];
export const Sfonts = isDev ? [MontserratFont, MontserratFont, MontserratFont] : [MontserratFont, PoppinsFont, RalewayFont];
export const Bfonts = isDev ? [RobotoFont, RobotoFont, RobotoFont] : [RobotoFont, OpenSansFont, LatoFont];
export const Afonts = isDev ? [NunitoFont, NunitoFont, NunitoFont] : [NunitoFont, PTSansFont, SourceSansProFont];
