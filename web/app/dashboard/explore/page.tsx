import { getExploreData } from "@/features/exploration/services/explore-queries";
import ExplorePageClient from "./explore-page-client";

export const metadata = {
    title: "Explore - CompEx",
    description: "Explore problem topics and types for GRE and GMAT preparation.",
};

export const dynamic = "force-dynamic";

export default async function ExplorePage() {
    const tags = await getExploreData();

    return (
        <div className="w-full min-h-screen bg-background text-foreground">
            <ExplorePageClient tags={tags} />
        </div>
    );
}
