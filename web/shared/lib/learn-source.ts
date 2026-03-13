import { docs, meta } from "@/.source";
import { createMDXSource } from "fumadocs-mdx";
import { loader } from "fumadocs-core/source";

export const learnSource = loader({
  baseUrl: "/learn",
  source: createMDXSource(docs, meta),
});
