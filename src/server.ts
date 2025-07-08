import express from "express"
import cors from "cors"
import helmet from "helmet"
import rateLimit from "express-rate-limit"
import { CampaignsController } from "./api/campaigns"
import { ChatController } from "./api/chat"
import { WhatsAppController } from "./api/whatsapp"
import { WhatsAppSetupController } from "./api/whatsapp-setup"

const app = express()
const PORT = process.env.PORT || 3001

// Middleware
app.use(helmet())
app.use(
  cors({
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    credentials: true,
  }),
)
app.use(express.json({ limit: "10mb" }))
app.use(express.urlencoded({ extended: true }))

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: "Too many requests from this IP",
})
app.use("/api/", limiter)

// Health check
app.get("/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() })
})

// Campaign routes
app.post("/api/campaigns", CampaignsController.createCampaign)
app.get("/api/campaigns", CampaignsController.getCampaigns)
app.post("/api/campaigns/:campaignId/setup", CampaignsController.setupCampaign)
app.post("/api/campaigns/:campaignId/send", CampaignsController.sendCampaign)
app.get("/api/campaigns/:campaignId/analytics", CampaignsController.getCampaignAnalytics)

// Chat routes
app.post("/api/chat/:uniqueLink/session", ChatController.createChatSession)
app.post("/api/chat/message", ChatController.handleChatMessage)
app.get("/api/chat/:sessionToken/history", ChatController.getChatHistory)

// WhatsApp routes
app.get("/api/whatsapp/webhook", WhatsAppController.webhook)
app.post("/api/whatsapp/webhook", WhatsAppController.handleIncoming)
app.post("/api/whatsapp/send", WhatsAppController.sendMessage)

// WhatsApp setup routes
app.get("/api/whatsapp/verify-setup", WhatsAppSetupController.verifySetup)
app.post("/api/whatsapp/setup-templates", WhatsAppSetupController.setupTemplates)
app.get("/api/whatsapp/templates", WhatsAppSetupController.getTemplates)
app.post("/api/whatsapp/test-message", WhatsAppSetupController.testMessage)
app.post("/api/whatsapp/send-template", WhatsAppSetupController.sendTemplateMessage)

// Error handling middleware
app.use((error: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error("Unhandled error:", error)
  res.status(500).json({
    success: false,
    error: "Internal server error",
  })
})

// 404 handler
app.use("*", (req, res) => {
  res.status(404).json({
    success: false,
    error: "Route not found",
  })
})

app.listen(PORT, () => {
  console.log(`🚀 Debt Collection API server running on port ${PORT}`)
  console.log(`📊 Health check: http://localhost:${PORT}/health`)
})

export default app
