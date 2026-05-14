import Fastify from 'fastify';
import { TelegramClient } from 'telegram';
import { StringSession } from 'telegram/sessions/index.js';
import { MongoClient } from 'mongodb';
import mimetypes from 'mime-types';
import bigInt from 'big-integer';

const PORT = process.env.STREAM_PORT || 8080;
const API_ID = parseInt(process.env.APP_ID || "0");
const API_HASH = process.env.API_HASH || "";
const BOT_TOKEN = process.env.TG_BOT_TOKEN || "";
const MONGODB_URI = process.env.DATABASE_URL || "";
const CHANNEL_ID = process.env.CHANNEL_ID || "";

const fastify = Fastify({ logger: true });

let client: TelegramClient;
let mongoClient: MongoClient;

async function startServer() {
  // 1. Setup Telegram Client
  client = new TelegramClient(new StringSession(""), API_ID, API_HASH, {
    connectionRetries: 5,
  });

  await client.start({
    botAuthToken: BOT_TOKEN,
  });

  // 2. Setup MongoDB
  mongoClient = new MongoClient(MONGODB_URI);
  await mongoClient.connect();

  fastify.get('/stream/:code', async (request, reply) => handleStream(request, reply, false));
  fastify.get('/download/:code', async (request, reply) => handleStream(request, reply, true));

  async function handleStream(request: any, reply: any, isDownload: boolean) {
    const { code } = request.params as { code: string };

    const db = mongoClient.db();
    const record = await db.collection('shortener_verifications').findOne({ _id: code as any });

    if (!record) {
      return reply.code(403).send('Forbidden');
    }

    const msgId = extractMsgId(record.original_url as string);
    if (!msgId) return reply.code(404).send('Media Not Found');

    try {
      const messages = await client.getMessages(CHANNEL_ID, { ids: [msgId] });
      const msg = messages[0];
      const media = (msg as any).video || (msg as any).document;

      if (!media) return reply.code(404).send('No Streamable Media');

      const fileSize = media.size;
      const range = request.headers.range;

      let start = 0;
      let end = fileSize - 1;

      if (range) {
        const parts = range.replace(/bytes=/, "").split("-");
        start = parseInt(parts[0], 10);
        end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
      }

      const chunkSize = 1024 * 1024; // 1MB for higher speed
      const mimeType = media.mimeType || mimetypes.lookup(media.name || 'file.mp4') || 'video/mp4';

      const headers: any = {
        'Content-Range': `bytes ${start}-${end}/${fileSize}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': (end - start) + 1,
        'Content-Type': mimeType,
        'Access-Control-Allow-Origin': '*',
        'X-Accel-Buffering': 'no',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'X-Content-Type-Options': 'nosniff'
      };

      if (isDownload) {
          const fileName = encodeURIComponent(media.name || 'file.mp4');
          headers['Content-Disposition'] = `attachment; filename="${fileName}"`;
      }

      reply.raw.writeHead(range ? 206 : 200, headers);

      const stream = client.iterDownload({
        file: media,
        offset: bigInt(start) as any,
        limit: bigInt(end - start + 1) as any,
        chunkSize: chunkSize,
        requestSize: chunkSize
      });

      for await (const chunk of stream) {
        if (reply.raw.destroyed) break;
        reply.raw.write(chunk);
      }
      reply.raw.end();

    } catch (err) {
      fastify.log.error(err);
      if (!reply.raw.headersSent) {
          return reply.code(500).send('Streaming Error');
      }
    }
  }

  function extractMsgId(url: string) {
      const match = url.match(/get-(\d+)/);
      if (match) return Math.floor(parseInt(match[1]) / Math.abs(parseInt(CHANNEL_ID)));
      return null;
  }

  await fastify.listen({ port: Number(PORT), host: '0.0.0.0' });
}

startServer().catch(err => {
  console.error("Failed to start stream server:", err);
});
