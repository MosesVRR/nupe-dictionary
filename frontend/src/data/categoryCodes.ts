/**
 * Category codes transcribed from:
 * R. M. Blench, Nupe Dictionary, "Key to codes used in column 3",
 * introductory PDF page 4 (printed page 1), draft printout dated August 5, 2009.
 *
 * Definitions preserve the source wording. The source is marked as a draft.
 */

export interface CategoryCode {
  code: string;
  meaning: string;
}

export const categoryCodes: CategoryCode[] = [
  { code: "a", meaning: "architecture" },
  { code: "ad", meaning: "animal disease" },
  { code: "ai", meaning: "agricultural implement" },
  { code: "am", meaning: "amphibian" },
  { code: "an", meaning: "ant" },
  { code: "ap", meaning: "animal part" },
  { code: "b", meaning: "bird" },
  { code: "bd", meaning: "bead" },
  { code: "bf", meaning: "bodily fluid" },
  { code: "bm", meaning: "body mark, sore etc." },
  { code: "bp", meaning: "body part" },
  { code: "bs", meaning: "basket" },
  { code: "c", meaning: "crop" },
  { code: "ca", meaning: "canoe terms" },
  { code: "cc", meaning: "chicken colour" },
  { code: "ch", meaning: "charm, amulet" },
  { code: "co", meaning: "colour" },
  { code: "cr", meaning: "crustacean" },
  { code: "d", meaning: "disease, sickness" },
  { code: "da", meaning: "domestic animal" },
  { code: "dc", meaning: "dance" },
  { code: "dk", meaning: "drink" },
  { code: "dr", meaning: "item of dress" },

  { code: "e", meaning: "emotions" },
  { code: "et", meaning: "ethnonym" },
  { code: "f", meaning: "fish" },
  { code: "fa", meaning: "farming" },
  { code: "fo", meaning: "food" },
  { code: "fr", meaning: "fruit" },
  { code: "g", meaning: "grass" },
  { code: "ga", meaning: "game" },
  { code: "go", meaning: "gourd" },
  { code: "gr", meaning: "grasshopper" },
  { code: "h", meaning: "herb" },
  { code: "hb", meaning: "horse breed" },
  { code: "hc", meaning: "horse colour" },
  { code: "hg", meaning: "horse gear" },
  { code: "hu", meaning: "hunting equipment" },
  { code: "i", meaning: "insect" },
  { code: "is", meaning: "Islam" },
  { code: "k", meaning: "kinship" },
  { code: "la", meaning: "landscape" },
  { code: "ma", meaning: "mammal" },
  { code: "me", meaning: "medicine" },
  { code: "mi", meaning: "musical instrument" },
  { code: "mn", meaning: "mineral" },
  { code: "mo", meaning: "money" },

  { code: "mt", meaning: "mat" },
  { code: "p", meaning: "person" },
  { code: "pd", meaning: "personal decoration" },
  { code: "pl", meaning: "plant" },
  { code: "po", meaning: "pot" },
  { code: "r", meaning: "reptile, amphibian" },
  { code: "s", meaning: "snake" },
  { code: "sa", meaning: "salutation" },
  { code: "sh", meaning: "shrub" },
  { code: "so", meaning: "song" },
  { code: "t", meaning: "tree" },
  { code: "ti", meaning: "title" },
  { code: "tm", meaning: "temporal (adverbs)" },
  { code: "to", meaning: "tool" },
  { code: "tp", meaning: "tree part" },
  { code: "tr", meaning: "traditional religion" },
  { code: "tx", meaning: "textile" },
  { code: "v", meaning: "vine" },
  { code: "vc", meaning: "vendors’ call" },
  { code: "w", meaning: "water (river etc.)" },
  { code: "wf", meaning: "warfare" },
  { code: "wp", meaning: "weapon" },
  { code: "wv", meaning: "weaving" },
  { code: "wt", meaning: "weather" },
  { code: "z", meaning: "zoological term" },
];

export const categoryCodeMap: Record<string, string> = Object.fromEntries(
  categoryCodes.map(({ code, meaning }) => [code, meaning]),
);

export function getCategoryMeaning(code: string | null | undefined): string | undefined {
  if (!code) return undefined;
  return categoryCodeMap[code.trim()];
}
