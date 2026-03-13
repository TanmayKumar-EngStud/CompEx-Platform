
import { Skeleton } from "@/shared/components/ui/skeleton";

export default function Loading() {
    return (
        <div className="p-8 space-y-8 w-full">
            <div className="space-y-4">
                <Skeleton className="h-10 w-[250px]" />
                <Skeleton className="h-4 w-[350px]" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Skeleton className="h-[200px] rounded-xl" />
                <Skeleton className="h-[200px] rounded-xl" />
                <Skeleton className="h-[200px] rounded-xl" />
                <Skeleton className="h-[200px] rounded-xl" />
                <Skeleton className="h-[200px] rounded-xl" />
                <Skeleton className="h-[200px] rounded-xl" />
            </div>
        </div>
    );
}
