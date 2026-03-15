// Legacy landing page — redirects to main page
// The live landing experience lives in app/page.tsx

import { redirect } from "next/navigation";

export default function LandingPage() {
  redirect("/");
}
