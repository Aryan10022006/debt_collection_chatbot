import type { Request, Response } from "express"
import { CampaignService } from "../services/campaignService"
import { supabase } from "../config/database"

export class CampaignsController {
  static async createCampaign(req: Request, res: Response): Promise<void> {
    try {
      const campaignData = req.body
      const campaign = await CampaignService.createCampaign(campaignData)

      res.status(201).json({
        success: true,
        data: campaign,
      })
    } catch (error) {
      console.error("Create campaign error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to create campaign",
      })
    }
  }

  static async getCampaigns(req: Request, res: Response): Promise<void> {
    try {
      const { status, type, limit = 50, offset = 0 } = req.query

      let query = supabase
        .from("campaigns")
        .select("*")
        .order("created_at", { ascending: false })
        .range(Number(offset), Number(offset) + Number(limit) - 1)

      if (status) {
        query = query.eq("status", status)
      }

      if (type) {
        query = query.eq("type", type)
      }

      const { data, error } = await query

      if (error) throw error

      res.json({
        success: true,
        data,
        pagination: {
          limit: Number(limit),
          offset: Number(offset),
          total: data.length,
        },
      })
    } catch (error) {
      console.error("Get campaigns error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to fetch campaigns",
      })
    }
  }

  static async setupCampaign(req: Request, res: Response): Promise<void> {
    try {
      const { campaignId } = req.params
      const { borrowerIds } = req.body

      const recipients = await CampaignService.setupCampaignRecipients(campaignId, borrowerIds)

      res.json({
        success: true,
        data: recipients,
      })
    } catch (error) {
      console.error("Setup campaign error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to setup campaign",
      })
    }
  }

  static async sendCampaign(req: Request, res: Response): Promise<void> {
    try {
      const { campaignId } = req.params

      // Start campaign sending process (async)
      CampaignService.sendCampaignMessages(campaignId).catch((error) => console.error("Campaign sending error:", error))

      res.json({
        success: true,
        message: "Campaign sending initiated",
      })
    } catch (error) {
      console.error("Send campaign error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to send campaign",
      })
    }
  }

  static async getCampaignAnalytics(req: Request, res: Response): Promise<void> {
    try {
      const { campaignId } = req.params
      const analytics = await CampaignService.getCampaignAnalytics(campaignId)

      res.json({
        success: true,
        data: analytics,
      })
    } catch (error) {
      console.error("Get campaign analytics error:", error)
      res.status(500).json({
        success: false,
        error: "Failed to fetch campaign analytics",
      })
    }
  }
}
