"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { useState } from "react";
import Navigation from "@/components/navigation";
import { 
  ArrowRight, 
  Sparkles, 
  Clock, 
  Target, 
  Zap,
  FileVideo,
  Globe,
  CheckCircle2,
  Play,
  Mail,
  Twitter
} from "lucide-react";

export default function Home() {
  const [billingPeriod, setBillingPeriod] = useState<"monthly" | "annual">("monthly");
  
  const fadeInUp = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const stagger = {
    visible: {
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  return (
    <div className="relative bg-white">
      <Navigation />
      
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center overflow-hidden py-12 md:py-0 pt-28 md:pt-16">
        {/* Animated background elements */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-20 left-10 w-48 md:w-72 h-48 md:h-72 bg-gray-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob" />
          <div className="absolute top-40 right-10 w-48 md:w-72 h-48 md:h-72 bg-gray-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000" />
          <div className="absolute -bottom-8 left-20 w-48 md:w-72 h-48 md:h-72 bg-gray-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000" />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center w-full md:-mt-16">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
            className="space-y-6 md:space-y-8"
          >
            <motion.div 
              variants={fadeInUp}
              className="inline-flex items-center gap-2 bg-black text-white rounded-full px-3 py-1.5 md:px-4 md:py-2 text-xs md:text-sm font-medium uppercase tracking-wider"
            >
              <Zap className="w-3 h-3 md:w-4 md:h-4" />
              AI-Powered Platform
            </motion.div>

            <motion.div
              variants={fadeInUp}
              className=""
            >
              <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-bold text-black leading-[1.1] md:leading-[1.05] tracking-tight">
                Content repurposing
                <br />
                reimagined
              </h1>
              <p className="text-xl sm:text-2xl md:text-3xl text-gray-500 font-normal mt-4 md:mt-6">
                with artificial intelligence
              </p>
            </motion.div>

            <motion.p 
              variants={fadeInUp}
              className="text-base sm:text-lg md:text-xl lg:text-2xl text-gray-600 max-w-xl md:max-w-2xl lg:max-w-3xl mx-auto px-4 md:px-0 pt-2 leading-relaxed"
            >
              Transform your long-form content into platform-optimized pieces with AI.
              <span className="hidden sm:inline"> Deploy intelligent workflows that understand, adapt, and deliver—in minutes, not hours.</span>
              <span className="sm:hidden"> Deploy intelligent workflows in minutes.</span>
            </motion.p>

            <motion.div 
              variants={fadeInUp}
              className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center pt-6 md:pt-8 px-4 sm:px-0"
            >
              <Button 
                asChild 
                className="bg-black text-white hover:bg-gray-800 rounded-full px-6 sm:px-8 md:px-10 py-4 md:py-5 text-base md:text-lg font-medium flex items-center justify-center h-auto w-full sm:w-auto"
              >
                <Link href="/sign-up" className="flex items-center">
                  Get Started Today
                </Link>
              </Button>
              <Button 
                asChild 
                variant="outline" 
                className="border-2 border-blue-500 text-blue-600 hover:bg-blue-50 rounded-full px-6 sm:px-8 md:px-10 py-4 md:py-5 text-base md:text-lg font-medium flex items-center justify-center h-auto w-full sm:w-auto relative overflow-hidden group"
              >
                <Link href="/try-free" className="flex items-center">
                  <Sparkles className="w-4 h-4 mr-2 group-hover:animate-pulse" />
                  Try Free - No Signup
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
              <Button 
                asChild 
                variant="ghost" 
                className="text-gray-600 hover:text-black hover:bg-gray-50 rounded-full px-6 sm:px-8 md:px-10 py-4 md:py-5 text-base md:text-lg font-medium flex items-center justify-center h-auto w-full sm:w-auto"
              >
                <Link href="#pricing" className="flex items-center">
                  View Pricing
                  <span className="ml-2 text-lg md:text-xl">&gt;</span>
                </Link>
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-16 sm:py-20 md:py-32 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12 md:mb-20"
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-black mb-4 md:mb-6">
              How it works
            </h2>
            <p className="text-base sm:text-lg md:text-xl text-gray-600 max-w-2xl mx-auto px-4 md:px-0">
              Three simple steps to transform your content
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-center px-4 md:px-0"
            >
              <div className="w-16 h-16 md:w-20 md:h-20 bg-black text-white rounded-full flex items-center justify-center text-xl md:text-2xl font-bold mx-auto mb-4 md:mb-6">
                1
              </div>
              <h3 className="text-xl md:text-2xl font-bold text-black mb-3 md:mb-4">Upload</h3>
              <p className="text-sm md:text-base text-gray-600">
                Drop your video, audio, or text content. Support for all major formats.
              </p>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-center px-4 md:px-0"
            >
              <div className="w-16 h-16 md:w-20 md:h-20 bg-black text-white rounded-full flex items-center justify-center text-xl md:text-2xl font-bold mx-auto mb-4 md:mb-6">
                2
              </div>
              <h3 className="text-xl md:text-2xl font-bold text-black mb-3 md:mb-4">AI Processing</h3>
              <p className="text-sm md:text-base text-gray-600">
                Our AI analyzes, transcribes, and understands your content's key messages.
              </p>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="text-center px-4 md:px-0"
            >
              <div className="w-16 h-16 md:w-20 md:h-20 bg-black text-white rounded-full flex items-center justify-center text-xl md:text-2xl font-bold mx-auto mb-4 md:mb-6">
                3
              </div>
              <h3 className="text-xl md:text-2xl font-bold text-black mb-3 md:mb-4">Export</h3>
              <p className="text-sm md:text-base text-gray-600">
                Get platform-optimized content ready to publish across all channels.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-16 sm:py-20 md:py-32 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12 md:mb-20"
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-black mb-4 md:mb-6">
              Built for creators
            </h2>
            <p className="text-base sm:text-lg md:text-xl text-gray-600 max-w-2xl mx-auto px-4 md:px-0">
              Everything you need to repurpose content at scale
            </p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            {[
              { icon: FileVideo, title: "Multi-format support", desc: "Video, audio, and text inputs" },
              { icon: Zap, title: "Lightning fast", desc: "Process hours of content in minutes" },
              { icon: Globe, title: "Platform optimized", desc: "Tailored for each social platform" },
              { icon: Target, title: "Smart extraction", desc: "Key points and highlights" },
              { icon: Clock, title: "Save 10+ hours", desc: "Weekly time savings guaranteed" },
              { icon: Sparkles, title: "Custom templates", desc: "Your brand voice, automated" }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="group p-6 md:p-8 rounded-xl md:rounded-2xl border border-gray-200 hover:border-gray-400 transition-colors"
              >
                <feature.icon className="w-10 h-10 md:w-12 md:h-12 text-black mb-3 md:mb-4" />
                <h3 className="text-lg md:text-xl font-bold text-black mb-2">{feature.title}</h3>
                <p className="text-sm md:text-base text-gray-600">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-16 sm:py-20 md:py-24 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-8 md:mb-10"
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-black mb-3 md:mb-4">
              Simple, transparent pricing
            </h2>
            <p className="text-base sm:text-lg text-gray-600 max-w-xl mx-auto mb-6 md:mb-8 px-4 md:px-0">
              Choose the plan that fits your needs
            </p>
            
            {/* Billing Toggle */}
            <div className="flex items-center justify-center gap-2 sm:gap-3 flex-wrap">
              <span className={`text-xs sm:text-sm font-medium ${billingPeriod === 'monthly' ? 'text-black' : 'text-gray-500'}`}>
                Monthly
              </span>
              <button
                onClick={() => setBillingPeriod(billingPeriod === 'monthly' ? 'annual' : 'monthly')}
                className="relative inline-flex h-5 w-10 sm:h-6 sm:w-11 items-center rounded-full bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
              >
                <span
                  className={`inline-block h-3 w-3 sm:h-4 sm:w-4 transform rounded-full bg-black transition-transform ${
                    billingPeriod === 'annual' ? 'translate-x-5 sm:translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
              <span className={`text-xs sm:text-sm font-medium ${billingPeriod === 'annual' ? 'text-black' : 'text-gray-500'}`}>
                Annual
              </span>
              {billingPeriod === 'annual' && (
                <span className="ml-1 sm:ml-2 inline-flex items-center rounded-full bg-green-100 px-1.5 sm:px-2 py-0.5 text-[10px] sm:text-xs font-medium text-green-800">
                  Save 20%
                </span>
              )}
            </div>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">
            {/* Starter */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-xl md:rounded-2xl p-6 sm:p-8 md:p-10 border border-gray-200 lg:transform lg:scale-100"
            >
              <div className="mb-4 md:mb-6">
                <h3 className="text-xl sm:text-2xl font-bold text-black">Starter</h3>
                <p className="text-sm sm:text-base text-gray-600 mt-1 md:mt-2">For individuals</p>
              </div>
              <div className="mb-6 md:mb-8">
                <span className="text-3xl sm:text-4xl font-bold text-black">$0</span>
                <span className="text-gray-600 text-sm sm:text-base">/{billingPeriod === 'monthly' ? 'mo' : 'yr'}</span>
              </div>
              <Button className="w-full bg-white text-black border border-gray-300 hover:bg-gray-50 rounded-full py-3 md:py-4 mb-6 md:mb-8 text-sm sm:text-base">
                Get Started
              </Button>
              <ul className="space-y-3 md:space-y-4 text-sm sm:text-base">
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-700">3 projects/month</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-700">Basic formats</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-700">1 user</span>
                </li>
              </ul>
            </motion.div>

            {/* Pro - Popular */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="bg-black text-white rounded-xl md:rounded-2xl p-6 sm:p-8 md:p-10 relative border-2 border-black lg:transform lg:scale-105 order-first lg:order-none"
            >
              <div className="absolute -top-3 md:-top-4 left-1/2 transform -translate-x-1/2">
                <div className="bg-black text-white text-xs sm:text-sm px-3 sm:px-4 py-1 sm:py-1.5 rounded-full border border-gray-700">
                  POPULAR
                </div>
              </div>
              <div className="mb-4 md:mb-6">
                <h3 className="text-xl sm:text-2xl font-bold">Pro</h3>
                <p className="text-sm sm:text-base text-gray-400 mt-1 md:mt-2">For growing teams</p>
              </div>
              <div className="mb-6 md:mb-8">
                <span className="text-3xl sm:text-4xl font-bold">
                  ${billingPeriod === 'monthly' ? '29' : '279'}
                </span>
                <span className="text-gray-400 text-sm sm:text-base">/{billingPeriod === 'monthly' ? 'mo' : 'yr'}</span>
                {billingPeriod === 'annual' && (
                  <div className="text-xs sm:text-sm text-gray-400 mt-1 md:mt-2">
                    <span className="line-through">$348</span> Save $69
                  </div>
                )}
              </div>
              <Button className="w-full bg-white text-black hover:bg-gray-200 rounded-full py-3 md:py-4 mb-6 md:mb-8 text-sm sm:text-base">
                Subscribe
              </Button>
              <ul className="space-y-3 md:space-y-4 text-sm sm:text-base">
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span>Unlimited projects</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span>All formats</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span>3 users</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span>API access</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span>Priority support</span>
                </li>
              </ul>
            </motion.div>

            {/* Business */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-xl md:rounded-2xl p-6 sm:p-8 md:p-10 border border-gray-200"
            >
              <div className="mb-4 md:mb-6">
                <h3 className="text-xl sm:text-2xl font-bold text-black">Business</h3>
                <p className="text-sm sm:text-base text-gray-600 mt-1 md:mt-2">For large orgs</p>
              </div>
              <div className="mb-6 md:mb-8">
                <span className="text-3xl sm:text-4xl font-bold text-black">
                  ${billingPeriod === 'monthly' ? '99' : '949'}
                </span>
                <span className="text-gray-600 text-sm sm:text-base">/{billingPeriod === 'monthly' ? 'mo' : 'yr'}</span>
                {billingPeriod === 'annual' && (
                  <div className="text-xs sm:text-sm text-gray-600 mt-1 md:mt-2">
                    <span className="line-through">$1,188</span> Save $239
                  </div>
                )}
              </div>
              <Button className="w-full bg-white text-black border border-gray-300 hover:bg-gray-50 rounded-full py-3 md:py-4 mb-6 md:mb-8 text-sm sm:text-base">
                Subscribe
              </Button>
              <ul className="space-y-3 md:space-y-4 text-sm sm:text-base">
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-700">Unlimited everything</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-700">10+ users</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-700">White label</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-700">Custom integrations</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-700">SLA</span>
                </li>
              </ul>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Testimonials with vertical scroll */}
      <section id="testimonials" className="py-16 sm:py-20 md:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-8 md:mb-12"
          >
            <div className="inline-flex items-center gap-2 bg-gray-100 rounded-full px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm text-gray-700 mb-4 md:mb-6">
              TESTIMONIALS
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-black mb-3 md:mb-4">
              Loved by content teams everywhere
            </h2>
            <p className="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto px-4 md:px-0">
              Join thousands of creators using Repostr
            </p>
          </motion.div>

          {/* Testimonials Grid with vertical scroll - hidden on mobile, visible on md+ */}
          <div className="hidden md:grid md:grid-cols-3 gap-6 max-h-[600px] overflow-hidden">
            {/* Column 1 - Scrolls Up */}
            <div className="space-y-4 animate-scroll-vertical-up">
              {[...Array(2)].map((_, duplicateIndex) => (
                <div key={duplicateIndex} className="space-y-4">
                  {[
                    {
                      text: "The content repurposing options are fantastic. Our social media engagement increased by 300%.",
                      author: "Sarah Mitchell",
                      role: "Content Director",
                      avatar: "SM"
                    },
                    {
                      text: "We've seen a 40% increase in content output. The AI is consistently on-brand.",
                      author: "Marcus Chen",
                      role: "Marketing Manager",
                      avatar: "MC"
                    },
                    {
                      text: "Repostr reduced our content production time by 75% in just two months.",
                      author: "Emily Rodriguez",
                      role: "Head of Content",
                      avatar: "ER"
                    },
                    {
                      text: "The customization options are unmatched. Our content feels natural.",
                      author: "David Park",
                      role: "Creative Director",
                      avatar: "DP"
                    }
                  ].map((testimonial, i) => (
                    <div
                      key={`col1-${duplicateIndex}-${i}`}
                      className="bg-gray-50 p-5 rounded-xl"
                    >
                      <div className="flex gap-1 mb-3">
                        {[...Array(5)].map((_, i) => (
                          <svg key={i} className="w-3 h-3 fill-black" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        ))}
                      </div>
                      <p className="text-gray-700 mb-4 text-sm leading-relaxed">
                        "{testimonial.text}"
                      </p>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-gray-200 to-gray-300 rounded-full flex items-center justify-center text-xs font-semibold text-gray-700">
                          {testimonial.avatar}
                        </div>
                        <div>
                          <div className="font-semibold text-black text-sm">{testimonial.author}</div>
                          <div className="text-xs text-gray-600">{testimonial.role}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>

            {/* Column 2 - Scrolls Down */}
            <div className="space-y-4 animate-scroll-vertical-down">
              {[...Array(2)].map((_, duplicateIndex) => (
                <div key={duplicateIndex} className="space-y-4">
                  {[
                    {
                      text: "The multi-language support has been crucial for our international expansion.",
                      author: "Anna Petersen",
                      role: "Global Content Lead",
                      avatar: "AP"
                    },
                    {
                      text: "Setup was incredibly intuitive. Within an hour, we transformed our workflow.",
                      author: "Roberto Silva",
                      role: "Operations Manager",
                      avatar: "RS"
                    },
                    {
                      text: "Best investment we've made this year. The ROI is incredible.",
                      author: "Jessica Wang",
                      role: "CEO",
                      avatar: "JW"
                    },
                    {
                      text: "Repostr has become essential to our content strategy.",
                      author: "Michael Brown",
                      role: "Content Strategist",
                      avatar: "MB"
                    }
                  ].map((testimonial, i) => (
                    <div
                      key={`col2-${duplicateIndex}-${i}`}
                      className="bg-gray-50 p-5 rounded-xl"
                    >
                      <div className="flex gap-1 mb-3">
                        {[...Array(5)].map((_, i) => (
                          <svg key={i} className="w-3 h-3 fill-black" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        ))}
                      </div>
                      <p className="text-gray-700 mb-4 text-sm leading-relaxed">
                        "{testimonial.text}"
                      </p>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-gray-200 to-gray-300 rounded-full flex items-center justify-center text-xs font-semibold text-gray-700">
                          {testimonial.avatar}
                        </div>
                        <div>
                          <div className="font-semibold text-black text-sm">{testimonial.author}</div>
                          <div className="text-xs text-gray-600">{testimonial.role}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>

            {/* Column 3 - Scrolls Up */}
            <div className="space-y-4 animate-scroll-vertical-up">
              {[...Array(2)].map((_, duplicateIndex) => (
                <div key={duplicateIndex} className="space-y-4">
                  {[
                    {
                      text: "The AI understanding is phenomenal. It captures nuance and context perfectly.",
                      author: "Laura Kim",
                      role: "Product Manager",
                      avatar: "LK"
                    },
                    {
                      text: "Our content quality has improved dramatically. Clients love the consistency.",
                      author: "James Wilson",
                      role: "Agency Owner",
                      avatar: "JW"
                    },
                    {
                      text: "From podcast to social posts in minutes. This tool revolutionized our pipeline.",
                      author: "Sophie Turner",
                      role: "Podcast Producer",
                      avatar: "ST"
                    },
                    {
                      text: "The time savings are real. We're producing 5x more content.",
                      author: "Alex Rivera",
                      role: "Marketing Director",
                      avatar: "AR"
                    }
                  ].map((testimonial, i) => (
                    <div
                      key={`col3-${duplicateIndex}-${i}`}
                      className="bg-gray-50 p-5 rounded-xl"
                    >
                      <div className="flex gap-1 mb-3">
                        {[...Array(5)].map((_, i) => (
                          <svg key={i} className="w-3 h-3 fill-black" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        ))}
                      </div>
                      <p className="text-gray-700 mb-4 text-sm leading-relaxed">
                        "{testimonial.text}"
                      </p>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-gray-200 to-gray-300 rounded-full flex items-center justify-center text-xs font-semibold text-gray-700">
                          {testimonial.avatar}
                        </div>
                        <div>
                          <div className="font-semibold text-black text-sm">{testimonial.author}</div>
                          <div className="text-xs text-gray-600">{testimonial.role}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>

          
          {/* Mobile Testimonials - Horizontal Scroll */}
          <div className="md:hidden overflow-x-auto pb-4">
            <div className="flex gap-4 px-4" style={{ width: 'max-content' }}>
              {[
                {
                  text: "The content repurposing options are fantastic. Our social media engagement increased by 300%.",
                  author: "Sarah Mitchell",
                  role: "Content Director",
                  avatar: "SM"
                },
                {
                  text: "We've seen a 40% increase in content output. The AI is consistently on-brand.",
                  author: "Marcus Chen",
                  role: "Marketing Manager",
                  avatar: "MC"
                },
                {
                  text: "Repostr reduced our content production time by 75% in just two months.",
                  author: "Emily Rodriguez",
                  role: "Head of Content",
                  avatar: "ER"
                }
              ].map((testimonial, i) => (
                <div
                  key={i}
                  className="bg-gray-50 p-4 rounded-xl w-72 flex-shrink-0"
                >
                  <div className="flex gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <svg key={i} className="w-3 h-3 fill-black" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                  <p className="text-gray-700 mb-3 text-sm leading-relaxed">
                    "{testimonial.text}"
                  </p>
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 bg-gradient-to-br from-gray-200 to-gray-300 rounded-full flex items-center justify-center text-[10px] font-semibold text-gray-700">
                      {testimonial.avatar}
                    </div>
                    <div>
                      <div className="font-semibold text-black text-xs">{testimonial.author}</div>
                      <div className="text-[10px] text-gray-600">{testimonial.role}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Stats Section */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 md:gap-8 mt-12 md:mt-16 pt-12 md:pt-16 border-t border-gray-200"
          >
            <div className="text-center">
              <div className="text-2xl sm:text-3xl md:text-4xl font-bold text-black mb-1 md:mb-2">98%</div>
              <div className="text-gray-600 text-xs sm:text-sm">Customer Satisfaction</div>
            </div>
            <div className="text-center">
              <div className="text-2xl sm:text-3xl md:text-4xl font-bold text-black mb-1 md:mb-2">80%</div>
              <div className="text-gray-600 text-xs sm:text-sm">Time Saved</div>
            </div>
            <div className="text-center">
              <div className="text-2xl sm:text-3xl md:text-4xl font-bold text-black mb-1 md:mb-2">3M+</div>
              <div className="text-gray-600 text-xs sm:text-sm">Content Pieces</div>
            </div>
            <div className="text-center">
              <div className="text-2xl sm:text-3xl md:text-4xl font-bold text-black mb-1 md:mb-2">24/7</div>
              <div className="text-gray-600 text-xs sm:text-sm">Availability</div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 sm:py-24 md:py-32 bg-black text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="space-y-4 md:space-y-6"
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold leading-tight px-4 sm:px-0">
              Ready to transform your<br className="hidden sm:inline" />
              <span className="sm:hidden"> </span>content strategy?
            </h2>
            <p className="text-sm sm:text-base md:text-lg text-gray-400 max-w-3xl mx-auto leading-relaxed px-4 sm:px-0">
              Join thousands of businesses delivering exceptional content experiences with AI. 
              <span className="hidden sm:inline">Let's discuss<br />how Repostr can transform your content workflow.</span>
              <span className="sm:hidden">Let's discuss how Repostr can transform your content workflow.</span>
            </p>
            <div className="pt-2 md:pt-4">
              <Button 
                asChild 
                className="bg-white text-black hover:bg-gray-100 rounded-full px-8 sm:px-12 md:px-16 py-4 sm:py-5 md:py-6 text-sm sm:text-base font-medium inline-flex items-center"
              >
                <Link href="/contact" className="flex items-center">
                  <Mail className="mr-2 h-3 w-3 sm:h-4 sm:w-4" />
                  Contact Us
                </Link>
              </Button>
            </div>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6 md:gap-8 pt-6 md:pt-8 text-xs sm:text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-gray-500 rounded-full" />
                <span>14-day free trial</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-gray-500 rounded-full" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-gray-500 rounded-full" />
                <span>Setup in 5 minutes</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-6 sm:gap-8">
            {/* Brand Column */}
            <div className="col-span-2">
              <div className="mb-4">
                <h3 className="text-2xl font-bold text-black">Repostr</h3>
              </div>
              <p className="text-gray-600 text-sm leading-relaxed mb-6">
                Effortless AI content repurposing that feels<br />
                native to your brand.
              </p>
              <p className="text-gray-500 text-xs">
                © 2025 Repostr, Inc.<br />
                All rights reserved.
              </p>
            </div>

            {/* Product Column */}
            <div>
              <h4 className="font-semibold text-black mb-4 text-sm uppercase tracking-wider">Product</h4>
              <ul className="space-y-3">
                <li><Link href="/features" className="text-gray-600 hover:text-black text-sm transition-colors">Features</Link></li>
                <li><Link href="/pricing" className="text-gray-600 hover:text-black text-sm transition-colors">Pricing</Link></li>
                <li><Link href="/api" className="text-gray-600 hover:text-black text-sm transition-colors">API Docs</Link></li>
                <li><Link href="/integrations" className="text-gray-600 hover:text-black text-sm transition-colors">Integrations</Link></li>
              </ul>
            </div>

            {/* Company Column */}
            <div>
              <h4 className="font-semibold text-black mb-4 text-sm uppercase tracking-wider">Company</h4>
              <ul className="space-y-3">
                <li><Link href="/about" className="text-gray-600 hover:text-black text-sm transition-colors">About</Link></li>
                <li><Link href="/blog" className="text-gray-600 hover:text-black text-sm transition-colors">Blog</Link></li>
                <li><Link href="/careers" className="text-gray-600 hover:text-black text-sm transition-colors">Careers</Link></li>
                <li><Link href="/contact" className="text-gray-600 hover:text-black text-sm transition-colors">Contact</Link></li>
              </ul>
            </div>

            {/* Legal Column */}
            <div>
              <h4 className="font-semibold text-black mb-4 text-sm uppercase tracking-wider">Legal</h4>
              <ul className="space-y-3">
                <li><Link href="/privacy" className="text-gray-600 hover:text-black text-sm transition-colors">Privacy</Link></li>
                <li><Link href="/terms" className="text-gray-600 hover:text-black text-sm transition-colors">Terms</Link></li>
                <li><Link href="/security" className="text-gray-600 hover:text-black text-sm transition-colors">Security</Link></li>
                <li><Link href="/gdpr" className="text-gray-600 hover:text-black text-sm transition-colors">GDPR</Link></li>
              </ul>
            </div>

            {/* Connect Column */}
            <div>
              <h4 className="font-semibold text-black mb-4 text-sm uppercase tracking-wider">Connect</h4>
              <ul className="space-y-3">
                <li><Link href="https://twitter.com/repostr" className="text-gray-600 hover:text-black text-sm transition-colors">Twitter</Link></li>
                <li><Link href="https://linkedin.com/company/repostr" className="text-gray-600 hover:text-black text-sm transition-colors">LinkedIn</Link></li>
                <li><Link href="https://github.com/repostr" className="text-gray-600 hover:text-black text-sm transition-colors">GitHub</Link></li>
                <li><Link href="https://discord.gg/repostr" className="text-gray-600 hover:text-black text-sm transition-colors">Discord</Link></li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
