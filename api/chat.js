const MAX_MESSAGE_LENGTH = 4000;
const MAX_HISTORY_ITEMS = 10;
// Sửa tên model chính xác của Google Gemini API
const MODEL = 'gemini-3.5-flash-lite'; 

const DOC_FILES = ['PRODUCT_RULES.md', 'USER_GUIDE.md'];
const GITHUB_REPO = 'quickmapshare/doc-FormMail-Hub';
const BRANCH = 'main';

let globalKeyPointer = 0;

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'content-type': 'application/json; charset=utf-8',
  'cache-control': 'no-store',
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: corsHeaders,
  });
}

export async function OPTIONS() {
  return new Response(null, { status: 200, headers: corsHeaders });
}

async function loadKnowledge() {
  try {
    const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
    const validDocs = await Promise.all(
      DOC_FILES.map(async (filePath) => {
        const url = GITHUB_TOKEN
          ? `https://api.github.com/repos/${GITHUB_REPO}/contents/${filePath}?ref=${BRANCH}`
          : `https://raw.githubusercontent.com/${GITHUB_REPO}/${BRANCH}/${filePath}`;

        const headers = { 'User-Agent': 'Vercel-Node' };
        if (GITHUB_TOKEN) {
          headers['Authorization'] = `token ${GITHUB_TOKEN}`;
          headers['Accept'] = 'application/vnd.github.v3.raw';
        }

        const res = await fetch(url, { headers });
        if (!res.ok) {
          console.error(`Failed to load document (${res.status}): ${filePath}`);
          return '';
        }
        return await res.text();
      })
    );

    return validDocs.filter(Boolean).join('\n\n--- SOURCE DOCUMENT ---\n\n').slice(0, 90000);
  } catch (err) {
    console.error('Error fetching GitHub documents:', err);
    return '';
  }
}

export async function POST(request) {
  const freeKeys = [
    process.env.GEMINI_API_KEY_1,
    process.env.GEMINI_API_KEY_2,
    process.env.GEMINI_API_KEY_3,
    process.env.GEMINI_API_KEY_4,
    process.env.GEMINI_API_KEY_5,
  ].filter(Boolean).map((k) => k.trim());

  const paidKey = process.env.GEMINI_API_KEY_6?.trim() || process.env.GEMINI_API_KEY?.trim();

  if (freeKeys.length === 0 && !paidKey) {
    return json({ error: 'No Gemini API Keys are configured on Vercel.' }, 503);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Invalid request payload.' }, 400);
  }

  const message = typeof body.message === 'string' ? body.message.trim() : '';
  if (!message || message.length > MAX_MESSAGE_LENGTH) {
    return json({ error: 'Message length must be between 1 and 4000 characters.' }, 400);
  }

  // 🆔 Bổ sung: Lấy Session ID từ request body (Nếu client không truyền, tạo mã 6 ký tự dự phòng)
  const sessionId = typeof body.sessionId === 'string' && body.sessionId.trim()
    ? body.sessionId.trim().slice(0, 20)
    : Math.random().toString(36).substring(2, 8);

  const history = Array.isArray(body.history)
    ? body.history
        .filter((item) => item && ['user', 'model'].includes(item.role) && typeof item.text === 'string')
        .slice(-MAX_HISTORY_ITEMS)
        .map((item) => ({ role: item.role, parts: [{ text: item.text.slice(0, MAX_MESSAGE_LENGTH) }] }))
    : [];

  try {
    const knowledge = await loadKnowledge();
    const systemInstruction = `You are the official documentation assistant for FormMail Hub. Respond in the user's language (prefer English if the prompt is in English). Maintain a warm, helpful, and friendly tone.

Strictly use only the information provided in the two SOURCE DOCUMENTS below. Do not fabricate features, endpoints, pricing, policies, integrations, or instructions not present in the documentation.

- FEATURE REQUESTS & SUGGESTIONS: If the user asks for, suggests, or inquires about a feature/integration that FormMail Hub does not currently support, respond warmly and receptively. Acknowledge their idea, clearly note that you have recorded their request to report it back to the product/development team, and briefly ask if they have any specific workflow or use case details they'd like to share.
- OUT OF SCOPE QUESTIONS: If a question is simply outside the docs (and not a feature request), explicitly state that the documentation does not currently provide that information, suggest checking back in 24 to 48 hours as documentation is continuously updated, and suggest contacting https://formmail.vietutd.com/contact for further assistance.

Keep answers concise and clear. If a general technical question is broad or ambiguous, you may ask ONE brief, relevant follow-up question to clarify their setup and offer better guidance. Do not ask unnecessary questions for simple factual queries.

SOURCE DOCUMENTS:
${knowledge}`;

    const payload = {
      system_instruction: { parts: [{ text: systemInstruction }] },
      contents: [...history, { role: 'user', parts: [{ text: message }] }],
      generationConfig: { temperature: 0.2, maxOutputTokens: 900 },
    };

    const attemptKeys = [];

    if (freeKeys.length > 0) {
      const startIndex = globalKeyPointer % freeKeys.length;
      globalKeyPointer = (globalKeyPointer + 1) % freeKeys.length;

      for (let i = 0; i < freeKeys.length; i++) {
        const index = (startIndex + i) % freeKeys.length;
        attemptKeys.push({
          key: freeKeys[index],
          name: `Free Key #${index + 1}`,
          isPaid: false,
        });
      }
    }

    if (paidKey) {
      attemptKeys.push({
        key: paidKey,
        name: 'Paid Key #6 (Backup)',
        isPaid: true,
      });
    }

    let lastErrorStatus = 502;
    let lastErrorMessage = '';

    for (const item of attemptKeys) {
      const targetUrl = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${encodeURIComponent(item.key)}`;

      try {
        const response = await fetch(targetUrl, {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify(payload),
        });

        const rawText = await response.text();
        let result;
        try {
          result = JSON.parse(rawText);
        } catch {
          console.error(`Gemini response (${item.name}) is not valid JSON:`, rawText);
          lastErrorMessage = 'Invalid response from AI service.';
          continue;
        }

        if (!response.ok) {
          // Bổ sung xoay vòng cho cả lỗi 429 (Rate Limit) và 403 (Invalid / Disabled Key)
          if ([429, 403].includes(response.status)) {
            console.warn(`[ROTATE] ${item.name} gặp lỗi (${response.status}). Đang chuyển sang Key tiếp theo...`);
            lastErrorStatus = response.status;
            lastErrorMessage = result?.error?.message || 'Key limit or auth issue.';
            continue;
          }

          console.error(`Gemini API Error Detail (${item.name}):`, result);
          return json({ error: result?.error?.message || 'Gemini is currently unable to process your request.' }, response.status);
        }

        const answer = result?.candidates?.[0]?.content?.parts?.map((part) => part.text || '').join('').trim();
        if (!answer) {
          lastErrorMessage = 'No answer received from Gemini.';
          continue;
        }

        if (item.isPaid) {
          console.warn('⚠️ TOÀN BỘ KEY FREE ĐÃ BỊ DĨNH LIMIT! Đã kích hoạt Key dự phòng trả phí.');
        }

        // 📝 Console log bao gồm Session ID
        console.log(`[CHAT_LOG] [Session: ${sessionId}] (${item.name}) User: "${message}" | Bot: "${answer.replace(/\n/g, ' ')}"`);

        // 🎨 Gửi log về Discord dưới dạng Rich Embed
        const discordUrl = process.env.DISCORD_WEBHOOK_URL;
        if (discordUrl) {
          try {
            const discordEmbedPayload = {
              username: 'FormMail Hub AI Bot',
              embeds: [
                {
                  title: `💬 Session #${sessionId}`,
                  color: 0x7c3aed, // Màu tím Violet (124, 58, 237)
                  fields: [
                    {
                      name: '👤 User Message',
                      value: message.length > 1024 ? message.slice(0, 1021) + '...' : message,
                      inline: false,
                    },
                    {
                      name: '🤖 Bot Response',
                      value: answer.length > 1024 ? answer.slice(0, 1021) + '...' : answer,
                      inline: false,
                    },
                  ],
                  footer: {
                    text: `Key Used: ${item.name} | FormMail Hub Docs AI`,
                  },
                  timestamp: new Date().toISOString(),
                },
              ],
            };

            await fetch(discordUrl, {
              method: 'POST',
              headers: { 'content-type': 'application/json' },
              body: JSON.stringify(discordEmbedPayload),
              signal: AbortSignal.timeout(3000), // Timeout 3s để tránh delay Vercel Serverless
            });
          } catch (err) {
            console.error('Discord log error:', err.message);
          }
        }

        return json({ answer });

      } catch (fetchErr) {
        console.error(`Lỗi kết nối tới Gemini API (${item.name}):`, fetchErr);
        lastErrorMessage = fetchErr.message;
        continue;
      }
    }

    if (lastErrorStatus === 429) {
      return json({
        error: 'The AI assistant is currently receiving too many requests. Please wait a minute and try again.'
      }, 429);
    }

    return json({ error: lastErrorMessage || 'Unable to process your request across all API keys.' }, 502);

  } catch (error) {
    console.error('Server Internal Error:', error);
    return json({ error: 'Unable to connect to the chatbot service at this time.', detail: error.message }, 502);
  }
}
