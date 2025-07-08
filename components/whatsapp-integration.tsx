"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { MessageSquare, Send, CheckCircle, Clock } from "lucide-react"

export default function WhatsAppIntegration() {
  const [isConnected, setIsConnected] = useState(true)
  const [autoReply, setAutoReply] = useState(true)
  const [businessHours, setBusinessHours] = useState(true)

  const campaigns = [
    {
      id: "1",
      name: "Payment Reminder - Hindi",
      status: "active",
      sent: 1247,
      delivered: 1198,
      read: 892,
      replied: 234,
    },
    {
      id: "2",
      name: "EMI Offer - Multilingual",
      status: "paused",
      sent: 856,
      delivered: 823,
      read: 645,
      replied: 187,
    },
    {
      id: "3",
      name: "Final Notice - Regional",
      status: "completed",
      sent: 432,
      delivered: 421,
      read: 398,
      replied: 89,
    },
  ]

  const templates = [
    {
      id: "1",
      name: "Payment Reminder",
      language: "Hindi",
      content: "नमस्ते {name}, आपका ₹{amount} का भुगतान {due_date} को देय है। कृपया जल्दी भुगतान करें।",
      approved: true,
    },
    {
      id: "2",
      name: "EMI Offer",
      language: "Hinglish",
      content:
        "Hi {name}, aapke liye special EMI plan available hai. ₹{amount} ko {months} months mein pay kar sakte hain.",
      approved: true,
    },
    {
      id: "3",
      name: "Settlement Offer",
      language: "English",
      content:
        "Dear {name}, we are offering a one-time settlement of ₹{settlement_amount} for your outstanding amount of ₹{total_amount}.",
      approved: false,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-green-600" />
                WhatsApp Business Integration
              </CardTitle>
              <CardDescription>Manage WhatsApp campaigns and automation</CardDescription>
            </div>
            <Badge className={isConnected ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
              {isConnected ? "Connected" : "Disconnected"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="auto-reply">Auto Reply</Label>
              <Switch id="auto-reply" checked={autoReply} onCheckedChange={setAutoReply} />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="business-hours">Business Hours Only</Label>
              <Switch id="business-hours" checked={businessHours} onCheckedChange={setBusinessHours} />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="multilingual">Multilingual Support</Label>
              <Switch id="multilingual" checked={true} disabled />
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="campaigns" className="space-y-4">
        <TabsList>
          <TabsTrigger value="campaigns">Campaigns</TabsTrigger>
          <TabsTrigger value="templates">Message Templates</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="campaigns" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Active Campaigns</h3>
            <Button className="bg-green-600 hover:bg-green-700">
              <Send className="h-4 w-4 mr-2" />
              New Campaign
            </Button>
          </div>

          <div className="grid gap-4">
            {campaigns.map((campaign) => (
              <Card key={campaign.id}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="font-semibold">{campaign.name}</h4>
                      <Badge
                        className={
                          campaign.status === "active"
                            ? "bg-green-100 text-green-800"
                            : campaign.status === "paused"
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-gray-100 text-gray-800"
                        }
                      >
                        {campaign.status}
                      </Badge>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        Edit
                      </Button>
                      <Button variant="outline" size="sm">
                        {campaign.status === "active" ? "Pause" : "Resume"}
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-4 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-blue-600">{campaign.sent}</div>
                      <div className="text-sm text-gray-600">Sent</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-green-600">{campaign.delivered}</div>
                      <div className="text-sm text-gray-600">Delivered</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-purple-600">{campaign.read}</div>
                      <div className="text-sm text-gray-600">Read</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-orange-600">{campaign.replied}</div>
                      <div className="text-sm text-gray-600">Replied</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="templates" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Message Templates</h3>
            <Button variant="outline">Create Template</Button>
          </div>

          <div className="grid gap-4">
            {templates.map((template) => (
              <Card key={template.id}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="font-semibold">{template.name}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline">{template.language}</Badge>
                        {template.approved ? (
                          <Badge className="bg-green-100 text-green-800">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Approved
                          </Badge>
                        ) : (
                          <Badge className="bg-yellow-100 text-yellow-800">
                            <Clock className="h-3 w-3 mr-1" />
                            Pending Approval
                          </Badge>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        Edit
                      </Button>
                      <Button variant="outline" size="sm">
                        Use
                      </Button>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm">{template.content}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>WhatsApp Business API Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="phone-number">Business Phone Number</Label>
                  <Input id="phone-number" value="+91 98765 43210" disabled />
                </div>
                <div>
                  <Label htmlFor="business-name">Business Name</Label>
                  <Input id="business-name" value="DebtBot AI Collection" />
                </div>
              </div>

              <div>
                <Label htmlFor="webhook-url">Webhook URL</Label>
                <Input id="webhook-url" value="https://api.debtbot.ai/webhook/whatsapp" />
              </div>

              <div>
                <Label htmlFor="business-hours">Business Hours</Label>
                <div className="grid grid-cols-2 gap-4 mt-2">
                  <div>
                    <Label htmlFor="start-time" className="text-sm">
                      Start Time
                    </Label>
                    <Input id="start-time" type="time" value="09:00" />
                  </div>
                  <div>
                    <Label htmlFor="end-time" className="text-sm">
                      End Time
                    </Label>
                    <Input id="end-time" type="time" value="18:00" />
                  </div>
                </div>
              </div>

              <div>
                <Label htmlFor="auto-reply-message">Auto Reply Message</Label>
                <Textarea
                  id="auto-reply-message"
                  placeholder="Enter auto-reply message for after business hours..."
                  value="नमस्ते! हमारे व्यावसायिक घंटे समाप्त हो गए हैं। हम कल सुबह 9 बजे आपसे संपर्क करेंगे।"
                />
              </div>

              <Button className="w-full">Save Settings</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Compliance & Privacy</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>TRAI DLT Registration</Label>
                  <p className="text-sm text-gray-600">Distributed Ledger Technology compliance</p>
                </div>
                <Badge className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Registered
                </Badge>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Opt-out Management</Label>
                  <p className="text-sm text-gray-600">Automatic handling of STOP requests</p>
                </div>
                <Switch checked={true} />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Data Encryption</Label>
                  <p className="text-sm text-gray-600">End-to-end message encryption</p>
                </div>
                <Badge className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Enabled
                </Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
