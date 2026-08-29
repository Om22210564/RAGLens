"use client";

import { useParams } from "next/navigation";
import { DocumentStatus } from "@/features/documents/document-status";

export default function DocumentStatusPage() { const params = useParams<{ documentId: string }>(); return <DocumentStatus documentId={params.documentId} />; }
