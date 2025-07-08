"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Users, MessageSquare, IndianRupee, Clock } from "lucide-react"

export default function Analytics() {
  const metrics = [
    {
      title: "Total Recovery",
      value: "₹12.5L",
      change: "+18.2%",
      trend: "up",
      icon: IndianRupee,
      description: "This month",
    },
    {
      title: "Response Rate",
      value: "74.3%",
      change: "+5.1%",
      trend: "up",
      icon: MessageSquare,
      description: "Across all languages",
    },
    {
      title: "Active Cases",
      value: "1,247",
      change: "-3.2%",
      trend: "down",
      icon: Users,
      description: "Currently being processed",
    },
    {
      title: "Avg Resolution Time",
      value: "4.2 days",
      change: "-12.5%",
      trend: "up",
      icon: Clock,
      description: "Faster than last month",
    },
  ]

  const languageStats = [
    { language: "Hindi", cases: 456, recovery: "68.2%", color: "bg-blue-500" },
    { language: "English", cases: 342, recovery: "72.1%", color: "bg-green-500" },
    { language: "Marathi", cases: 234, recovery: "65.8%", color: "bg-purple-500" },
    { language: "Tamil", cases: 123, recovery: "71.3%", color: "bg-orange-500" },
    { language: "Telugu", cases: 92, recovery: "69.7%", color: "bg-red-500" },
  ]

  const channelPerformance = [
    { channel: "WhatsApp", messages: 8934, responses: 6721, rate: "75.2%" },
    { channel: "Web Chat", messages: 3456, responses: 2543, rate: "73.6%" },
    { channel: "SMS", messages: 2134, responses: 1234, rate: "57.8%" },
    { channel: "Voice Call", messages: 1567, responses: 1123, rate: "71.7%" },
  ]

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                  <div className="flex items-center mt-1">
                    {metric.trend === "up" ? (
                      <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-600 mr-1" />
                    )}
                    <span className={`text-sm ${metric.trend === "up" ? "text-green-600" : "text-red-600"}`}>
                      {metric.change}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{metric.description}</p>
                </div>
                <metric.icon className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Language Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Performance by Language</CardTitle>
            <CardDescription>Recovery rates across different languages</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {languageStats.map((stat, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${stat.color}`}></div>
                    <div>
                      <p className="font-medium">{stat.language}</p>
                      <p className="text-sm text-gray-600">{stat.cases} cases</p>
                    </div>
                  </div>
                  <Badge variant="outline" className="bg-green-50 text-green-700">
                    {stat.recovery}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Channel Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Channel Performance</CardTitle>
            <CardDescription>Response rates by communication channel</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {channelPerformance.map((channel, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{channel.channel}</span>
                    <span className="text-sm font-medium">{channel.rate}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full" style={{ width: channel.rate }}></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-600">
                    <span>{channel.messages} sent</span>
                    <span>{channel.responses} responses</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recovery Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Recovery Timeline</CardTitle>
          <CardDescription>Monthly recovery performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-end justify-between space-x-2">
            {[
              { month: "Jan", amount: 8.5, height: "45%" },
              { month: "Feb", amount: 9.2, height: "52%" },
              { month: "Mar", amount: 7.8, height: "40%" },
              { month: "Apr", amount: 11.3, height: "65%" },
              { month: "May", amount: 10.7, height: "60%" },
              { month: "Jun", amount: 12.5, height: "75%" },
              { month: "Jul", amount: 14.2, height: "85%" },
              { month: "Aug", amount: 13.8, height: "82%" },
              { month: "Sep", amount: 15.1, height: "90%" },
              { month: "Oct", amount: 16.7, height: "100%" },
              { month: "Nov", amount: 15.9, height: "95%" },
              { month: "Dec", amount: 18.2, height: "100%" },
            ].map((data, index) => (
              <div key={index} className="flex flex-col items-center flex-1">
                <div
                  className="w-full bg-blue-600 rounded-t-sm mb-2 min-h-[20px] flex items-end justify-center"
                  style={{ height: data.height }}
                >
                  <span className="text-white text-xs font-medium mb-1">₹{data.amount}L</span>
                </div>
                <span className="text-xs text-gray-600">{data.month}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Regional Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Regional Performance</CardTitle>
          <CardDescription>Debt collection performance across Indian states</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { state: "Maharashtra", cases: 456, recovery: "72.3%", amount: "₹4.2L" },
              { state: "Karnataka", cases: 342, recovery: "68.7%", amount: "₹3.1L" },
              { state: "Tamil Nadu", cases: 289, recovery: "71.2%", amount: "₹2.8L" },
              { state: "Gujarat", cases: 234, recovery: "69.8%", amount: "₹2.3L" },
              { state: "Andhra Pradesh", cases: 198, recovery: "67.4%", amount: "₹1.9L" },
              { state: "Rajasthan", cases: 167, recovery: "65.9%", amount: "₹1.6L" },
            ].map((region, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <h4 className="font-semibold">{region.state}</h4>
                <div className="mt-2 space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>Cases:</span>
                    <span>{region.cases}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Recovery Rate:</span>
                    <span className="text-green-600">{region.recovery}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Amount:</span>
                    <span className="font-medium">{region.amount}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
