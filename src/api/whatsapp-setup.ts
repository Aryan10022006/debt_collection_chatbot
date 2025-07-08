import type { Request, Response } from "express"
import { WhatsAppService } from "../services/whatsappService"
import { WhatsAppTemplateService } from "../services/whatsappTemplateService"
import { WHATSAPP_CONFIG, validateIndianPhoneNumber, formatIndianPhoneNumber } from "../config/whatsapp"

export class WhatsAppSetupController {
  static async verifySetup(req: Request, res: Response): Promise<void> {
    try {
      const isVerified = await WhatsAppService.verifyBusinessAccount()

      if (isVerified) {
        res.json({
          success: true,
          message: "WhatsApp Business Account verified successfully",
          config: {
            businessAccountId: WHATSAPP_CONFIG.BUSINESS_ACCOUNT_ID,
            phoneNumberId: WHATSAPP_CONFIG.PHONE_NUMBER_ID,
            whatsappNumber: WHATSAPP_CONFIG.WHATSAPP_NUMBER,
            appId: WHATSAPP_CONFIG.APP_ID,
          },
        })
      } else {
        res.status(400).json({
          success: false,
          error: "WhatsApp Business Account verification failed",
        })
      }
    } catch (error) {
      console.error("WhatsApp setup verification error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to verify WhatsApp setup",
      })
    }
  }

  static async setupTemplates(req: Request, res: Response): Promise<void> {
    try {
      await WhatsAppTemplateService.setupDefaultTemplates()

      res.json({
        success: true,
        message: "Default message templates created successfully",
      })
    } catch (error) {
      console.error("Template setup error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to setup message templates",
      })
    }
  }

  static async getTemplates(req: Request, res: Response): Promise<void> {
    try {
      const templates = await WhatsAppTemplateService.getApprovedTemplates()

      res.json({
        success: true,
        data: templates,
      })
    } catch (error) {
      console.error("Get templates error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to fetch templates",
      })
    }
  }

  static async testMessage(req: Request, res: Response): Promise<void> {
    try {
      const { phoneNumber, message } = req.body

      if (!validateIndianPhoneNumber(phoneNumber)) {
        res.status(400).json({
          success: false,
          error: "Invalid Indian phone number format",
        })
        return
      }

      const formattedPhone = formatIndianPhoneNumber(phoneNumber)
      await WhatsAppService.sendMessage(formattedPhone, message || "Test message from DebtBot AI")

      res.json({
        success: true,
        message: "Test message sent successfully",
        to: formattedPhone,
      })
    } catch (error) {
      console.error("Test message error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to send test message",
      })
    }
  }

  static async sendTemplateMessage(req: Request, res: Response): Promise<void> {
    try {
      const { phoneNumber, templateName, parameters } = req.body

      if (!validateIndianPhoneNumber(phoneNumber)) {
        res.status(400).json({
          success: false,
          error: "Invalid Indian phone number format",
        })
        return
      }

      const formattedPhone = formatIndianPhoneNumber(phoneNumber)

      // Send template message
      await WhatsAppService.sendTemplateMessage(formattedPhone, templateName, parameters)

      res.json({
        success: true,
        message: "Template message sent successfully",
        to: formattedPhone,
        template: templateName,
      })
    } catch (error) {
      console.error("Template message error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to send template message",
      })
    }
  }
}
