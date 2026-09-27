const MAX_MESSAGE_LENGTH = 4000;
const MAX_HISTORY_ITEMS = 10;
const MODEL = 'gemini-3.5-flash-lite';

const DOC_FILES = ['PRODUCT_RULES.md', 'USER_GUIDE.md'];
const GITHUB_REPO = 'quickmapshare/doc-FormMail-Hub';
const BRANCH = 'main';

// Biến lưu con trỏ luân phiên (nằm ngoài hàm POST để duy trì giữa các lượt gọi)
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

// Handle preflight CORS requests
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

// Handler for Vercel Serverless Function
export async function POST(request) {
  // 1. Tách danh sách 5 Key Free và Key Paid riêng biệt
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

  const history = Array.isArray(body.history)
    ? body.history
        .filter((item) => item && ['user', 'model'].includes(item.role) && typeof item.text === 'string')
        .slice(-MAX_HISTORY_ITEMS)
        .map((item) => ({ role: item.role, parts: [{ text: item.text.slice(0, MAX_MESSAGE_LENGTH) }] }))
    : [];

  try {
    const knowledge = await loadKnowledge();
    const systemInstruction = `You are the official documentation assistant for FormMail Hub. Respond in the user's language (prefer English if the prompt is in English). Strictly use only the information provided in the two SOURCE DOCUMENTS below. Do not fabricate features, endpoints, pricing, policies, integrations, or instructions not present in the documentation. If a question is outside the docs, explicitly state that the documentation does not currently provide that information, suggest checking back in 24 to 48 hours as documentation is continuously updated, and suggest contacting https://formmail.vietutd.com/contact for further assistance. Keep answers concise and clear.\n\nSOURCE DOCUMENTS:\n${knowledge}`;
    const payload = {
      system_instruction: { parts: [{ text: systemInstruction }] },
      contents: [...history, { role: 'user', parts: [{ text: message }] }],
      generationConfig: { temperature: 0.2, maxOutputTokens: 900 },
    };

    // 2. Tạo danh sách Key ưu tiên cho LẦN GỌI NÀY theo dạng Luân Phiên (Round-Robin)
    const attemptKeys = [];

    if (freeKeys.length > 0) {
      const startIndex = globalKeyPointer % freeKeys.length;
      // Cập nhật con trỏ cho request tiếp theo
      globalKeyPointer = (globalKeyPointer + 1) % freeKeys.length;

      // Đưa các Key Free vào danh sách bắt đầu từ startIndex
      for (let i = 0; i < freeKeys.length; i++) {
        const index = (startIndex + i) % freeKeys.length;
        attemptKeys.push({
          key: freeKeys[index],
          name: `Free Key #${index + 1}`,
          isPaid: false,
        });
      }
    }

    // Luôn luôn xếp Key Trả Phí ở VỊ TRÍ CUỐI CÙNG (Chỉ dùng khi cả 5 Key Free đều xịt)
    if (paidKey) {
      attemptKeys.push({
        key: paidKey,
        name: 'Paid Key #6 (Backup)',
        isPaid: true,
      });
    }

    let lastErrorStatus = 502;
    let lastErrorMessage = '';

    // 3. Thực hiện xoay vòng thử lần lượt theo thứ tự đã sắp xếp
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
          // Bị 429 (Rate Limit / Quota) -> Bỏ qua, thử Key tiếp theo trong mảng
          if (response.status === 429) {
            console.warn(`[ROTATE] ${item.name} bị dính Limit 429. Đang chuyển sang Key tiếp theo...`);
            lastErrorStatus = 429;
            lastErrorMessage = result?.error?.message || 'Rate limit reached.';
            continue;
          }

          // Lỗi khác (400 Bad Request...) -> Dừng luôn
          console.error(`Gemini API Error Detail (${item.name}):`, result);
          return json({ error: result?.error?.message || 'Gemini is currently unable to process your request.' }, response.status);
        }

        const answer = result?.candidates?.[0]?.content?.parts?.map((part) => part.text || '').join('').trim();
        if (!answer) {
          lastErrorMessage = 'No answer received from Gemini.';
          continue;
        }

        // Cảnh báo nếu phải dùng tới Key Trả Phí
        if (item.isPaid) {
          console.warn('⚠️ TOÀN BỘ KEY FREE ĐÃ BỊ DĨNH LIMIT! Đã kích hoạt Key dự phòng trả phí.');
        }

        // Ghi log chi tiết Key nào đã xử lý thành công
        console.log(`[CHAT_LOG] (${item.name}) User: "${message}" | Bot: "${answer.replace(/\n/g, ' ')}"`);

        // Gửi log về Discord
        const discordUrl = process.env.DISCORD_WEBHOOK_URL;
        if (discordUrl) {
          try {
            await fetch(discordUrl, {
              method: 'POST',
              headers: { 'content-type': 'application/json' },
              body: JSON.stringify({
                content: `💬 **FormMail Hub Chat** *(${item.name})*\n👤 **User:** ${message}\n🤖 **Bot:** ${answer}`,
              }),
            });
          } catch (err) {
            console.error('Discord log error:', err);
          }
        }

        // Trả kết quả thành công
        return json({ answer });

      } catch (fetchErr) {
        console.error(`Lỗi kết nối tới Gemini API (${item.name}):`, fetchErr);
        lastErrorMessage = fetchErr.message;
        continue;
      }
    }

    // Nếu chạy hết mảng mà vẫn thất bại
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
