"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MessageSquare, Phone, Users, TrendingUp, Globe, Shield } from "lucide-react"
import ChatInterface from "@/components/chat-interface"
import DebtorManagement from "@/components/debtor-management"
import Analytics from "@/components/analytics"
import WhatsAppIntegration from "@/components/whatsapp-integration"

export default function DebtCollectionDashboard() {
  const [activeTab, setActiveTab] = useState("chat")

  const stats = [
    {
      title: "Active Conversations",
      value: "1,247",
      change: "+12%",
      icon: MessageSquare,
      color: "text-blue-600",
    },
    {
      title: "Recovery Rate",
      value: "68.5%",
      change: "+5.2%",
      icon: TrendingUp,
      color: "text-green-600",
    },
    {
      title: "Total Debtors",
      value: "3,892",
      change: "+8%",
      icon: Users,
      color: "text-purple-600",
    },
    {
      title: "WhatsApp Reach",
      value: "89.3%",
      change: "+15%",
      icon: Phone,
      color: "text-orange-600",
    },
  ]

  const languages = [
    { code: "hi", name: "Hindi", flag: "🇮🇳" },
    { code: "mr", name: "Marathi", flag: "🇮🇳" },
    { code: "ta", name: "Tamil", flag: "🇮🇳" },
    { code: "te", name: "Telugu", flag: "🇮🇳" },
    { code: "en-IN", name: "Hinglish", flag: "🇮🇳" },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Shield className="h-8 w-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-gray-900">DebtBot AI</h1>
              </div>
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                <Globe className="h-3 w-3 mr-1" />
                Multilingual
              </Badge>
            </div>
            <div className="flex items-center space-x-2">
              {languages.map((lang) => (
                <Badge key={lang.code} variant="secondary" className="text-xs">
                  {lang.flag} {lang.name}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Stats Dashboard */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                    <p className="text-sm text-green-600">{stat.change} from last month</p>
                  </div>
                  <stat.icon className={`h-8 w-8 ${stat.color}`} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="chat">AI Chat Interface</TabsTrigger>
            <TabsTrigger value="debtors">Debtor Management</TabsTrigger>
            <TabsTrigger value="whatsapp">WhatsApp Integration</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="chat">
            <ChatInterface />
          </TabsContent>

          <TabsContent value="debtors">
            <DebtorManagement />
          </TabsContent>

          <TabsContent value="whatsapp">
            <WhatsAppIntegration />
          </TabsContent>

          <TabsContent value="analytics">
            <Analytics />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
