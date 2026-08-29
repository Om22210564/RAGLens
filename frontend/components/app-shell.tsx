import Link from "next/link";
import { ConnectionStatus } from "@/components/connection-status";
import { IdentityGate } from "@/components/identity-gate";
import { IdentitySummary } from "@/components/identity-summary";

const navigation = [{ href: "/", label: "Overview" }, { href: "/documents", label: "Documents" }, { href: "/ask", label: "Ask" }, { href: "/traces", label: "Traces" }, { href: "/evaluation", label: "Evaluation" }];

export function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
  return <div className="min-h-screen bg-canvas text-ink">
    <a href="#main-content" className="skip-link">Skip to main content</a>
    <header className="border-b border-line bg-panel px-5 py-4"><div className="mx-auto flex max-w-7xl items-center justify-between gap-4"><Link href="/" className="font-semibold tracking-tight">RAG Engineering Console</Link><div className="flex items-center gap-4"><ConnectionStatus /><IdentitySummary /></div></div></header>
    <div className="mx-auto grid max-w-7xl md:grid-cols-[14rem_1fr]"><nav aria-label="Primary navigation" className="border-b border-line p-4 md:min-h-[calc(100vh-65px)] md:border-b-0 md:border-r"><ul className="flex gap-2 overflow-x-auto md:block md:space-y-1">{navigation.map((item) => <li key={item.href}><Link className="flex items-center justify-between rounded-md px-3 py-2 text-sm hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" href={item.href}>{item.label}</Link></li>)}</ul></nav><main id="main-content" className="p-5 md:p-8"><IdentityGate>{children}</IdentityGate></main></div>
  </div>;
}
