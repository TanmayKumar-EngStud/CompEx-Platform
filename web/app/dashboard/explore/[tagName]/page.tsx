import { getExploreData } from "@/features/exploration/services/explore-queries";
import ExploreDetailClient from "./explore-detail-client";
import { notFound } from "next/navigation";

export const metadata = {
    title: "Train - CompEx",
    description: "Targeted training session for specific topics.",
};

export default async function ExploreDetailPage({ params }: { params: { tagName: string } }) {
    const allTags = await getExploreData();
    const decodedName = decodeURIComponent(params.tagName);

    // Find the tag. If multiple tags have same name (v unlikely), pick first.
    const tag = allTags.find(t => t.name === decodedName);

    if (!tag) {
        notFound();
    }

    return (
        <div className="w-full min-h-screen bg-background text-foreground">
            <ExploreDetailClient tag={tag} />
        </div>
    );
}
