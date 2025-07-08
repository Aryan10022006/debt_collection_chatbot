"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, Bot, User, Languages, Clock, CheckCircle } from "lucide-react"

interface Message {
  id: string
  type: "user" | "bot"
  content: string
  language: string
  timestamp: Date
  status?: "sent" | "delivered" | "read"
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "bot",
      content: "नमस्ते! मैं आपकी ऋण वसूली में सहायता के लिए यहाँ हूँ। आपका खाता संख्या क्या है?",
      language: "Hindi",
      timestamp: new Date(Date.now() - 300000),
      status: "read",
    },
    {
      id: "2",
      type: "user",
      content: "My account number is AC123456789",
      language: "English",
      timestamp: new Date(Date.now() - 240000),
      status: "read",
    },
    {
      id: "3",
      type: "bot",
      content:
        "Thank you! I can see you have an outstanding amount of ₹25,000. आपकी सुविधा के अनुसार, क्या आप आज कुछ भुगतान कर सकते हैं?",
      language: "Hinglish",
      timestamp: new Date(Date.now() - 180000),
      status: "read",
    },
  ])

  const [newMessage, setNewMessage] = useState("")
  const [selectedLanguage, setSelectedLanguage] = useState("auto")
  const [selectedDebtor, setSelectedDebtor] = useState("AC123456789")

  const languages = [
    { value: "auto", label: "Auto Detect" },
    { value: "hi", label: "Hindi" },
    { value: "mr", label: "Marathi" },
    { value: "ta", label: "Tamil" },
    { value: "te", label: "Telugu" },
    { value: "en-IN", label: "Hinglish" },
  ]

  const debtors = [
    { value: "AC123456789", label: "Rajesh Kumar - ₹25,000" },
    { value: "AC987654321", label: "Priya Sharma - ₹18,500" },
    { value: "AC456789123", label: "Arjun Patel - ₹32,000" },
  ]

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: newMessage,
      language:
        selectedLanguage === "auto"
          ? "English"
          : languages.find((l) => l.value === selectedLanguage)?.label || "English",
      timestamp: new Date(),
      status: "sent",
    }

    setMessages((prev) => [...prev, userMessage])
    setNewMessage("")

    // Simulate AI response
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: generateAIResponse(newMessage, selectedLanguage),
        language:
          selectedLanguage === "auto"
            ? "Hinglish"
            : languages.find((l) => l.value === selectedLanguage)?.label || "English",
        timestamp: new Date(),
        status: "delivered",
      }
      setMessages((prev) => [...prev, botResponse])
    }, 1500)
  }

  const generateAIResponse = (userMessage: string, language: string): string => {
    const responses = {
      payment: {
        hi: "धन्यवाद! आपका भुगतान प्राप्त हो गया है। क्या आप बाकी राशि के लिए EMI की व्यवस्था करना चाहेंगे?",
        en: "Thank you for your payment! Would you like to set up an EMI plan for the remaining amount?",
        "en-IN": "Great! Payment received hai. Remaining amount ke liye EMI plan set up karna chahenge?",
      },
      help: {
        hi: "मैं आपकी सहायता कर सकता हूँ। आप भुगतान कर सकते हैं, EMI प्लान बना सकते हैं, या अपना खाता विवरण देख सकते हैं।",
        en: "I can help you with payments, EMI plans, or account details. What would you like to do?",
        "en-IN": "Main aapki help kar sakta hun. Payment, EMI plan, ya account details - kya chahiye?",
      },
    }

    if (userMessage.toLowerCase().includes("payment") || userMessage.toLowerCase().includes("pay")) {
      return responses.payment[language as keyof typeof responses.payment] || responses.payment.en
    }

    return responses.help[language as keyof typeof responses.help] || responses.help.en
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Chat Interface */}
      <div className="lg:col-span-2">
        <Card className="h-[600px] flex flex-col">
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5 text-blue-600" />
                  AI Debt Collection Assistant
                </CardTitle>
                <CardDescription>Multilingual debt recovery chatbot</CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Select value={selectedDebtor} onValueChange={setSelectedDebtor}>
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {debtors.map((debtor) => (
                      <SelectItem key={debtor.value} value={debtor.value}>
                        {debtor.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>

          <CardContent className="flex-1 flex flex-col p-0">
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div key={message.id} className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}>
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        message.type === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        {message.type === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                        <Badge variant="secondary" className="text-xs">
                          {message.language}
                        </Badge>
                        <span className="text-xs opacity-70">{message.timestamp.toLocaleTimeString()}</span>
                      </div>
                      <p className="text-sm">{message.content}</p>
                      {message.type === "user" && (
                        <div className="flex justify-end mt-1">
                          {message.status === "sent" && <Clock className="h-3 w-3 opacity-70" />}
                          {message.status === "delivered" && <CheckCircle className="h-3 w-3 opacity-70" />}
                          {message.status === "read" && <CheckCircle className="h-3 w-3 text-blue-200" />}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>

            <div className="border-t p-4">
              <div className="flex items-center gap-2 mb-2">
                <Languages className="h-4 w-4 text-gray-500" />
                <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {languages.map((lang) => (
                      <SelectItem key={lang.value} value={lang.value}>
                        {lang.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex gap-2">
                <Input
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type your message..."
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                  className="flex-1"
                />
                <Button onClick={handleSendMessage} className="bg-blue-600 hover:bg-blue-700">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions & Templates */}
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full justify-start">
              Send Payment Reminder
            </Button>
            <Button variant="outline" className="w-full justify-start">
              Offer EMI Plan
            </Button>
            <Button variant="outline" className="w-full justify-start">
              Schedule Follow-up
            </Button>
            <Button variant="outline" className="w-full justify-start">
              Generate Settlement Offer
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Message Templates</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="text-sm space-y-2">
              <div className="p-2 bg-gray-50 rounded text-xs">
                <strong>Hindi:</strong> आपका भुगतान देय है। कृपया जल्दी भुगतान करें।
              </div>
              <div className="p-2 bg-gray-50 rounded text-xs">
                <strong>Hinglish:</strong> Aapka payment due hai. Please pay kijiye.
              </div>
              <div className="p-2 bg-gray-50 rounded text-xs">
                <strong>English:</strong> Your payment is overdue. Please make payment immediately.
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Compliance Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">RBI Guidelines</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  Compliant
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">TRAI Regulations</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  Compliant
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Data Privacy</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  Secure
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
