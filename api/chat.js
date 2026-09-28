const MAX_MESSAGE_LENGTH = 4000;
const MAX_HISTORY_ITEMS = 10;

// Model mặc định
// ✅ Sử dụng Model ID ổn định nhất trên Groq hiện tại
const GROQ_MODEL = 'llama3-8b-8192';
const GEMINI_MODEL = 'gemini-3.5-flash-lite'; 

const DOC_FILES = ['PRODUCT_RULES.md', 'USER_GUIDE.md'];
const GITHUB_REPO = 'quickmapshare/doc-FormMail-Hub';
const BRANCH = 'main';

let globalGeminiPointer = 0;

// 🎨 Bảng màu tươi sáng cho Discord Embeds
const PALETTE = [
  0x7c3aed, // Violet
  0x3b82f6, // Blue
  0x10b981, // Emerald
  0xf59e0b, // Amber
  0xec4899, // Pink
  0x06b6d4, // Cyan
  0xef4444, // Red
  0x84cc16, // Lime
  0x8b5cf6, // Purple
  0xf97316  // Orange
];

function getSessionColor(sessionId) {
  let hash = 0;
  for (let i = 0; i < sessionId.length; i++) {
    hash = sessionId.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % PALETTE.length;
  return PALETTE[index];
}

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
  // 1. Tải danh sách Groq API Keys (Ưu tiên số 1)
  const groqKeys = [
    process.env.GROQ_API_KEY_1,
    process.env.GROQ_API_KEY_2,
    process.env.GROQ_API_KEY,
  ].filter(Boolean).map((k) => k.trim());
  const uniqueGroqKeys = [...new Set(groqKeys)];

  // 2. Tải danh sách Gemini Free Keys (Dự phòng số 1)
  const freeGeminiKeys = [
    process.env.GEMINI_API_KEY_1,
    process.env.GEMINI_API_KEY_2,
    process.env.GEMINI_API_KEY_3,
    process.env.GEMINI_API_KEY_4,
    process.env.GEMINI_API_KEY_5,
  ].filter(Boolean).map((k) => k.trim());

  // 3. Tải Gemini Paid Key (Dự phòng cuối cùng)
  const paidGeminiKey = process.env.GEMINI_API_KEY_6?.trim() || process.env.GEMINI_API_KEY?.trim();

  if (uniqueGroqKeys.length === 0 && freeGeminiKeys.length === 0 && !paidGeminiKey) {
    return json({ error: 'No AI API Keys (Groq or Gemini) are configured on Vercel.' }, 503);
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

    // Xây dựng danh sách chiến lược thử nghiệm (Groq -> Gemini Free -> Gemini Paid)
    const attemptKeys = [];

    // Thêm các Groq Keys vào đầu danh sách
    for (let i = 0; i < uniqueGroqKeys.length; i++) {
      attemptKeys.push({
        provider: 'groq',
        key: uniqueGroqKeys[i],
        name: `Groq Key #${i + 1}`,
      });
    }

    // Thêm các Gemini Free Keys (Xoay vòng Pointer)
    if (freeGeminiKeys.length > 0) {
      const startIndex = globalGeminiPointer % freeGeminiKeys.length;
      globalGeminiPointer = (globalGeminiPointer + 1) % freeGeminiKeys.length;

      for (let i = 0; i < freeGeminiKeys.length; i++) {
        const index = (startIndex + i) % freeGeminiKeys.length;
        attemptKeys.push({
          provider: 'gemini',
          key: freeGeminiKeys[index],
          name: `Gemini Free Key #${index + 1}`,
          isPaid: false,
        });
      }
    }

    // Thêm Gemini Paid Key dự phòng cuối cùng
    if (paidGeminiKey) {
      attemptKeys.push({
        provider: 'gemini',
        key: paidGeminiKey,
        name: 'Gemini Paid Key #6 (Backup)',
        isPaid: true,
      });
    }

    let lastErrorStatus = 502;
    let lastErrorMessage = '';

    for (const item of attemptKeys) {
      try {
        let response;
        let answer = '';

        if (item.provider === 'groq') {
          // --- XỬ LÝ GỌI GROQ API (Chuẩn OpenAI Format) ---
          const groqMessages = [
            { role: 'system', content: systemInstruction },
            ...history.map((h) => ({
              role: h.role === 'model' ? 'assistant' : 'user',
              content: h.parts?.[0]?.text || '',
            })),
            { role: 'user', content: message },
          ];

          response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${item.key}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              model: GROQ_MODEL,
              messages: groqMessages,
              temperature: 0.2,
              max_tokens: 900,
            }),
          });

          const rawText = await response.text();
          let result;
          try {
            result = JSON.parse(rawText);
          } catch {
            console.error(`Groq response (${item.name}) không phải JSON:`, rawText);
            lastErrorMessage = 'Phản hồi không hợp lệ từ Groq.';
            continue;
          }

          if (!response.ok) {
            if ([429, 403, 500, 502, 503, 504].includes(response.status)) {
              console.warn(`[ROTATE] ${item.name} (Groq) gặp lỗi (${response.status}). Chuyển sang Key tiếp theo...`);
              lastErrorStatus = response.status;
              lastErrorMessage = result?.error?.message || `Lỗi dịch vụ Groq (${response.status}).`;
              continue;
            }
            console.error(`Lỗi Groq API (${item.name}):`, result);
            return json({ error: result?.error?.message || 'Groq không thể xử lý yêu cầu.' }, response.status);
          }

          answer = result?.choices?.[0]?.message?.content?.trim();

        } else if (item.provider === 'gemini') {
          // --- XỬ LÝ GỌI GEMINI API ---
          const targetUrl = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${encodeURIComponent(item.key)}`;
          
          const geminiPayload = {
            system_instruction: { parts: [{ text: systemInstruction }] },
            contents: [...history, { role: 'user', parts: [{ text: message }] }],
            generationConfig: { temperature: 0.2, maxOutputTokens: 900 },
          };

          response = await fetch(targetUrl, {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify(geminiPayload),
          });

          const rawText = await response.text();
          let result;
          try {
            result = JSON.parse(rawText);
          } catch {
            console.error(`Gemini response (${item.name}) không phải JSON:`, rawText);
            lastErrorMessage = 'Phản hồi không hợp lệ từ Gemini.';
            continue;
          }

          if (!response.ok) {
            if ([429, 403, 500, 502, 503, 504].includes(response.status)) {
              console.warn(`[ROTATE] ${item.name} (Gemini) gặp lỗi (${response.status}). Chuyển sang Key tiếp theo...`);
              lastErrorStatus = response.status;
              lastErrorMessage = result?.error?.message || `Lỗi dịch vụ Gemini (${response.status}).`;
              continue;
            }
            console.error(`Lỗi Gemini API (${item.name}):`, result);
            return json({ error: result?.error?.message || 'Gemini không thể xử lý yêu cầu.' }, response.status);
          }

          answer = result?.candidates?.[0]?.content?.parts?.map((p) => p.text || '').join('').trim();
        }

        if (!answer) {
          lastErrorMessage = 'Không nhận được câu trả lời từ AI.';
          continue;
        }

        if (item.isPaid) {
          console.warn('⚠️ TOÀN BỘ KEY FREE (GROQ & GEMINI) ĐÃ BỊ DĨNH LIMIT! Đã kích hoạt Key dự phòng trả phí.');
        }

        console.log(`[CHAT_LOG] [Session: ${sessionId}] (${item.name}) User: "${message}" | Bot: "${answer.replace(/\n/g, ' ')}"`);

        // 🎨 Gửi log về Discord
        const discordUrl = process.env.DISCORD_WEBHOOK_URL;
        if (discordUrl) {
          try {
            const discordEmbedPayload = {
              username: 'FormMail Hub AI Bot',
              embeds: [
                {
                  title: `💬 Session #${sessionId}`,
                  color: getSessionColor(sessionId),
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
                    text: `Provider: ${item.name} | FormMail Hub Docs AI`,
                  },
                  timestamp: new Date().toISOString(),
                },
              ],
            };

            await fetch(discordUrl, {
              method: 'POST',
              headers: { 'content-type': 'application/json' },
              body: JSON.stringify(discordEmbedPayload),
              signal: AbortSignal.timeout(3000),
            });
          } catch (err) {
            console.error('Lỗi gửi Discord log:', err.message);
          }
        }

        return json({ answer });

      } catch (fetchErr) {
        console.error(`Lỗi kết nối tới ${item.name}:`, fetchErr);
        lastErrorMessage = fetchErr.message;
        continue;
      }
    }

    if (lastErrorStatus === 429) {
      return json({
        error: 'Hệ thống AI hiện đang nhận quá nhiều yêu cầu. Vui lòng thử lại sau ít phút.'
      }, 429);
    }

    return json({ error: lastErrorMessage || 'Không thể xử lý yêu cầu qua tất cả các API Key.' }, 502);

  } catch (error) {
    console.error('Server Internal Error:', error);
    return json({ error: 'Không thể kết nối đến dịch vụ chatbot lúc này.', detail: error.message }, 502);
  }
}
