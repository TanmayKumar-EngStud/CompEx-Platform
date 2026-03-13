import { DocsLayout } from "fumadocs-ui/layouts/docs";
import { RootProvider } from "fumadocs-ui/provider";
import type { ReactNode } from "react";
import { learnSource } from "@/lib/learn-source";
import LearnNavbar from "./LearnNavbar";

export default function LearnLayout({ children }: { children: ReactNode }) {
  return (
    <RootProvider>
      <LearnNavbar />
      <DocsLayout
        tree={learnSource.pageTree}
        nav={{ enabled: false }}
        sidebar={{
          banner: (
            <div className="text-sm text-fd-muted-foreground px-2">
              Learn about CompEx and the exams we support
            </div>
          ),
        }}
        links={[
          { text: "Dashboard", url: "/dashboard/explore" },
          { text: "Pricing", url: "/pricing" },
        ]}
      >
        {children}
      </DocsLayout>
    </RootProvider>
  );
}

