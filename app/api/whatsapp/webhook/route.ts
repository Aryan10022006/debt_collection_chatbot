import { NextResponse } from "next/server"

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const mode = searchParams.get("hub.mode")
  const token = searchParams.get("hub.verify_token")
  const challenge = searchParams.get("hub.challenge")

  // Verify webhook (WhatsApp requirement)
  if (mode === "subscribe" && token === process.env.WHATSAPP_VERIFY_TOKEN) {
    return new Response(challenge, { status: 200 })
  }

  return new Response("Forbidden", { status: 403 })
}

export async function POST(request: Request) {
  const body = await request.json()

  // Process incoming WhatsApp messages
  if (body.entry && body.entry[0].changes && body.entry[0].changes[0].value.messages) {
    const message = body.entry[0].changes[0].value.messages[0]
    const from = message.from
    const messageBody = message.text?.body || ""

    // Log the message
    console.log(`Received message from ${from}: ${messageBody}`)

    // Process the message with AI
    await processWhatsAppMessage(from, messageBody)
  }

  return NextResponse.json({ status: "ok" })
}

async function processWhatsAppMessage(from: string, message: string) {
  // In production, this would:
  // 1. Identify the debtor from phone number
  // 2. Get their preferred language
  // 3. Generate AI response using the chat API
  // 4. Send response via WhatsApp Business API

  console.log(`Processing message from ${from}: ${message}`)

  // Mock response for demo
  const response = await generateAIResponse(message, from)
  await sendWhatsAppMessage(from, response)
}

async function generateAIResponse(message: string, phoneNumber: string) {
  // This would call your AI service
  return "नमस्ते! आपका संदेश प्राप्त हुआ है। हमारा एजेंट जल्द ही आपसे संपर्क करेगा।"
}

async function sendWhatsAppMessage(to: string, message: string) {
  // This would send message via WhatsApp Business API
  console.log(`Sending to ${to}: ${message}`)
}
