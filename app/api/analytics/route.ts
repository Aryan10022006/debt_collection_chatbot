import { NextResponse } from "next/server"

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const period = searchParams.get("period") || "30d"

  // Mock analytics data - in production, this would query your database
  const analytics = {
    totalRecovery: {
      amount: 1250000,
      change: 18.2,
      period: period,
    },
    responseRate: {
      rate: 74.3,
      change: 5.1,
      period: period,
    },
    activeCases: {
      count: 1247,
      change: -3.2,
      period: period,
    },
  }

  return NextResponse.json(analytics)
}
