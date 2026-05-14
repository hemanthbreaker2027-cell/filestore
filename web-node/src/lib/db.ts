import { MongoClient } from "mongodb";
import Redis from "ioredis";

const uri = process.env.DATABASE_URL || "";
const redisUrl = process.env.REDIS_URL;

let client: MongoClient;
let clientPromise: Promise<MongoClient> | null = null;

if (uri) {
  if (process.env.NODE_ENV === "development") {
    // In development mode, use a global variable so that the value
    // is preserved across module reloads caused by HMR (Hot Module Replacement).
    if (!(global as any)._mongoClientPromise) {
      client = new MongoClient(uri);
      (global as any)._mongoClientPromise = client.connect();
    }
    clientPromise = (global as any)._mongoClientPromise;
  } else {
    // In production mode, it's best to not use a global variable.
    client = new MongoClient(uri);
    clientPromise = client.connect();
  }
}

export const redis = redisUrl ? new Redis(redisUrl) : null;

export default async function getClientPromise() {
  if (!clientPromise) {
      throw new Error("DATABASE_URL is not defined");
  }
  return clientPromise;
}
