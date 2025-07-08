import { supabase } from "../config/database"
import type { Campaign, CampaignRecipient } from "../types"
import { WhatsAppService } from "./whatsappService"
import { SMSService } from "./smsService"
import { v4 as uuidv4 } from "uuid"

export class CampaignService {
  static async createCampaign(campaignData: Partial<Campaign>): Promise<Campaign> {
    const { data, error } = await supabase.from("campaigns").insert([campaignData]).select().single()

    if (error) throw error
    return data
  }

  static async setupCampaignRecipients(campaignId: string, borrowerIds: string[]): Promise<CampaignRecipient[]> {
    const recipients = borrowerIds.map((borrowerId) => ({
      campaign_id: campaignId,
      borrower_id: borrowerId,
      unique_link: this.generateUniqueLink(campaignId, borrowerId),
      status: "pending" as const,
    }))

    const { data, error } = await supabase.from("campaign_recipients").insert(recipients).select()

    if (error) throw error
    return data
  }

  static async sendCampaignMessages(campaignId: string): Promise<void> {
    // Get campaign details
    const { data: campaign, error: campaignError } = await supabase
      .from("campaigns")
      .select("*, message_templates(*)")
      .eq("id", campaignId)
      .single()

    if (campaignError) throw campaignError

    // Get pending recipients
    const { data: recipients, error: recipientsError } = await supabase
      .from("campaign_recipients")
      .select(`
        *,
        borrowers(*),
        debt_accounts(*)
      `)
      .eq("campaign_id", campaignId)
      .eq("status", "pending")

    if (recipientsError) throw recipientsError

    // Send messages to each recipient
    for (const recipient of recipients) {
      try {
        await this.sendMessageToRecipient(campaign, recipient)

        // Update recipient status
        await supabase
          .from("campaign_recipients")
          .update({
            status: "sent",
            sent_at: new Date().toISOString(),
          })
          .eq("id", recipient.id)
      } catch (error) {
        console.error(`Failed to send message to recipient ${recipient.id}:`, error)

        // Update recipient status to failed
        await supabase.from("campaign_recipients").update({ status: "failed" }).eq("id", recipient.id)
      }
    }
  }

  private static async sendMessageToRecipient(campaign: any, recipient: any): Promise<void> {
    const borrower = recipient.borrowers
    const debtAccount = recipient.debt_accounts
    const template = campaign.message_templates

    // Personalize message content
    const personalizedContent = this.personalizeMessage(template.content, borrower, debtAccount, recipient.unique_link)

    // Determine platform and send message
    const preferredPlatform = this.determinePreferredPlatform(borrower)

    if (preferredPlatform === "whatsapp") {
      await WhatsAppService.sendMessage(borrower.phone, personalizedContent, template.whatsapp_template_id)
    } else {
      await SMSService.sendMessage(borrower.phone, personalizedContent)
    }
  }

  private static personalizeMessage(template: string, borrower: any, debtAccount: any, uniqueLink: string): string {
    return template
      .replace("{name}", borrower.name)
      .replace("{amount}", `₹${debtAccount.outstanding_amount.toLocaleString("en-IN")}`)
      .replace("{due_date}", new Date(debtAccount.due_date).toLocaleDateString("en-IN"))
      .replace("{account_number}", debtAccount.account_number)
      .replace("{chat_link}", `${process.env.FRONTEND_URL}/chat/${uniqueLink}`)
  }

  private static determinePreferredPlatform(borrower: any): "whatsapp" | "sms" {
    // Logic to determine preferred platform based on borrower data
    // For now, default to WhatsApp if phone number is available
    return borrower.phone ? "whatsapp" : "sms"
  }

  private static generateUniqueLink(campaignId: string, borrowerId: string): string {
    return `${campaignId}-${borrowerId}-${uuidv4().substring(0, 8)}`
  }

  static async getCampaignAnalytics(campaignId: string): Promise<any> {
    const { data, error } = await supabase.from("campaign_recipients").select("status").eq("campaign_id", campaignId)

    if (error) throw error

    const analytics = data.reduce(
      (acc, recipient) => {
        acc[recipient.status] = (acc[recipient.status] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    return {
      total: data.length,
      sent: analytics.sent || 0,
      delivered: analytics.delivered || 0,
      read: analytics.read || 0,
      replied: analytics.replied || 0,
      failed: analytics.failed || 0,
    }
  }
}
