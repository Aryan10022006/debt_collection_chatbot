import type { Request, Response } from "express"
import { WhatsAppService } from "../services/whatsappService"

export class WhatsAppController {
  static async webhook(req: Request, res: Response): Promise<void> {
    try {
      const mode = req.query["hub.mode"]
      const token = req.query["hub.verify_token"]
      const challenge = req.query["hub.challenge"]

      // Verify webhook
      if (mode === "subscribe" && token === process.env.WHATSAPP_VERIFY_TOKEN) {
        console.log("WhatsApp webhook verified")
        res.status(200).send(challenge)
        return
      }

      res.status(403).send("Forbidden")
    } catch (error) {
      console.error("WhatsApp webhook verification error:", error)
      res.status(500).json({
        success: false,
        error: "Webhook verification failed",
      })
    }
  }

  static async handleIncoming(req: Request, res: Response): Promise<void> {
    try {
      await WhatsAppService.handleWebhook(req.body)
      res.status(200).json({ status: "ok" })
    } catch (error) {
      console.error("WhatsApp incoming message error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to process incoming message",
      })
    }
  }

  static async sendMessage(req: Request, res: Response): Promise<void> {
    try {
      const { to, message, templateId } = req.body

      await WhatsAppService.sendMessage(to, message, templateId)

      res.json({
        success: true,
        message: "Message sent successfully",
      })
    } catch (error) {
      console.error("WhatsApp send message error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to send message",
      })
    }
  }
}
