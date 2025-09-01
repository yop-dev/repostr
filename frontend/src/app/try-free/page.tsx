/**
 * Try Free Landing Page
 * Dedicated page for anonymous upload feature with conversion optimization
 * Following frontend best practices: SEO, accessibility, performance
 */

import { Metadata } from "next";
import { AnonymousFlow } from "@/components/transcription/AnonymousFlow";

export const metadata: Metadata = {
  title: "Try Free AI Transcription - No Signup Required | Repostr",
  description: "Upload any audio file and see our AI transcription in action. Get instant previews with 95% accuracy. No credit card or signup required to try.",
  keywords: [
    "free transcription",
    "AI transcription",
    "audio to text",
    "speech to text",
    "no signup required",
    "instant transcription"
  ],
  openGraph: {
    title: "Try Free AI Transcription - No Signup Required",
    description: "Upload any audio file and see our AI transcription in action. Get instant previews with 95% accuracy.",
    type: "website",
    url: "/try-free",
  },
  twitter: {
    card: "summary_large_image",
    title: "Try Free AI Transcription - No Signup Required",
    description: "Upload any audio file and see our AI transcription in action. Get instant previews with 95% accuracy.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function TryFreePage() {
  return (
    <main className="min-h-screen bg-background">
      {/* Container with proper spacing */}
      <div className="container mx-auto px-4 pt-24 md:pt-28 pb-8 md:pb-12">
        <AnonymousFlow />
      </div>
      
      {/* Structured Data for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Repostr AI Transcription",
            "description": "Free AI-powered audio transcription service with instant previews",
            "url": "https://repostr.com/try-free",
            "applicationCategory": "ProductivityApplication",
            "operatingSystem": "Web Browser",
            "offers": {
              "@type": "Offer",
              "price": "0",
              "priceCurrency": "USD",
              "description": "Free trial with no signup required"
            },
            "featureList": [
              "AI-powered transcription",
              "95% accuracy rate",
              "Multiple file format support",
              "Instant preview",
              "No signup required for trial"
            ]
          })
        }}
      />
    </main>
  );
}