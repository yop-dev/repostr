"use client";

import Link from "next/link";
import { useAuth, UserButton } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { usePathname } from "next/navigation";

export function Navbar() {
  const { isSignedIn } = useAuth();
  const pathname = usePathname();

  const isLandingPage = pathname === "/";

  return (
    <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex h-16 items-center justify-between">
          {/* Logo - Left */}
          <div className="flex-1">
            <Link href="/" className="inline-flex items-center space-x-2">
              <div className="text-2xl font-bold text-black">
                Repostr
              </div>
            </Link>
          </div>
          
          {/* Navigation - Center */}
          <nav className="hidden md:flex items-center justify-center flex-1">
            <div className="flex items-center gap-8">
              {isSignedIn ? (
                <>
                  <Link
                    href="/dashboard"
                    className="text-sm font-medium text-gray-600 hover:text-black transition-colors"
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/projects"
                    className="text-sm font-medium text-gray-600 hover:text-black transition-colors"
                  >
                    Projects
                  </Link>
                  <Link
                    href="/templates"
                    className="text-sm font-medium text-gray-600 hover:text-black transition-colors"
                  >
                    Templates
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    href="/#features"
                    className="text-sm font-medium text-gray-600 hover:text-black transition-colors"
                  >
                    Features
                  </Link>
                  <Link
                    href="/#pricing"
                    className="text-sm font-medium text-gray-600 hover:text-black transition-colors"
                  >
                    Pricing
                  </Link>
                  <Link
                    href="/#testimonials"
                    className="text-sm font-medium text-gray-600 hover:text-black transition-colors"
                  >
                    Testimonials
                  </Link>
                  <Link
                    href="/#contact"
                    className="text-sm font-medium text-gray-600 hover:text-black transition-colors"
                  >
                    Contact
                  </Link>
                </>
              )}
            </div>
          </nav>

          {/* Auth Buttons - Right */}
          <div className="flex items-center justify-end gap-4 flex-1">
            {isSignedIn ? (
              <>
                <Button className="bg-black text-white hover:bg-gray-800 rounded-full px-6" size="sm">
                  <Link href="/projects/new">New Project</Link>
                </Button>
                <UserButton afterSignOutUrl="/" />
              </>
            ) : (
              <>
                <Link 
                  href="/sign-in"
                  className="text-sm font-medium text-gray-600 hover:text-black transition-colors px-4"
                >
                  Sign In
                </Link>
                <Button className="bg-black text-white hover:bg-gray-800 rounded-full px-6" size="sm">
                  <Link href="/sign-up">Get Started</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
