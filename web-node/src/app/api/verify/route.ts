import { NextRequest, NextResponse } from "next/server";
import { jwtVerify } from "jose";
import getClientPromise, { redis } from "@/lib/db";

const SECURE_SECRET_KEY = process.env.SECURE_SECRET_KEY || "HJjdgddjdodkdbdbdmdksksiwkwoahsbdndododjdndndmdkdjdbdmdosjsbsbwkwkwjsbdbdndkdkdkdjdbdbdndndndndna amalapapaksbsbsn";

export async function POST(req: NextRequest) {
  try {
    const { token, browser, tabId } = await req.json();

    if (!token) {
      return NextResponse.json({ success: false, message: "Missing token" }, { status: 400 });
    }

    // 1. Validate JWT Signature and Expiry
    const secret = new TextEncoder().encode(SECURE_SECRET_KEY);
    let payload: any;
    try {
      const { payload: decoded } = await jwtVerify(token, secret);
      payload = decoded;
    } catch (err) {
      return NextResponse.json({ success: false, message: "Invalid or expired token" }, { status: 403 });
    }

    // 2. Browser Consistency Check
    const uaHeader = req.headers.get("user-agent") || "";
    const isChrome = uaHeader.includes("Chrome") && !uaHeader.includes("Edge") && !uaHeader.includes("OPR");

    if (!isChrome && process.env.NODE_ENV === 'production') {
         return NextResponse.json({ success: false, message: "Security Violation: Browser inconsistency detected." }, { status: 403 });
    }

    // 3. Redis Session / Same-tab Lock
    if (redis) {
        const sessionKey = `verify_session:${payload.user_id}:${payload.payload}`;
        const activeTab = await redis.get(sessionKey);

        if (activeTab && activeTab !== tabId) {
            return NextResponse.json({ success: false, message: "Security Violation: Multi-tab session detected." }, { status: 403 });
        }
        await redis.set(sessionKey, tabId, "EX", 60);
    }

    // 4. Link Conversion Logic
    const code = payload.payload;
    const wrappedDomain = "theimmigrationworld.com";
    const finalUrl = `https://${wrappedDomain}/eductionssstudiess/?eductionstudiess=${code}&uiso=9367`;

    // 5. Database update
    const clientPromise = await getClientPromise();
    if (clientPromise) {
        const client = await clientPromise;
        const db = client.db();
        await db.collection("settings").updateOne(
            { user_id: payload.user_id },
            { $set: { verify_token: payload.payload, is_verified: true, verified_time: Date.now() / 1000 } }
        );
    }

    return NextResponse.json({
      success: true,
      redirect: finalUrl,
    });

  } catch (err) {
    console.error("Verify API Error:", err);
    return NextResponse.json({ success: false, message: "Internal Server Error" }, { status: 500 });
  }
}
