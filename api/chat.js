const MAX_MESSAGE_LENGTH = 4000;
const MAX_HISTORY_ITEMS = 10;
const MODEL = 'gemini-3.6-flash'; // Đã sửa tên model chuẩn của Google

const DOC_FILES = ['PRODUCT_RULES.md', 'USER_GUIDE.md'];
const GITHUB_REPO = 'quickmapshare/doc-FormMail-Hub';
const BRANCH = 'main';

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

// Xử lý Preflight CORS request từ trình duyệt
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
          console.error(`Không thể tải tài liệu (${res.status}): ${filePath}`);
          return '';
        }
        return await res.text();
      })
    );

    return validDocs.filter(Boolean).join('\n\n--- SOURCE DOCUMENT ---\n\n').slice(0, 90000);
  } catch (err) {
    console.error('Lỗi khi fetch tài liệu GitHub:', err);
    return '';
  }
}

// Handler chuẩn cho Vercel Serverless Function
export async function POST(request) {
  const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

  if (!GEMINI_API_KEY) {
    return json({ error: 'Chatbot chưa được cấu hình GEMINI_API_KEY trên Vercel.' }, 503);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Request không hợp lệ.' }, 400);
  }

  const message = typeof body.message === 'string' ? body.message.trim() : '';
  if (!message || message.length > MAX_MESSAGE_LENGTH) {
    return json({ error: 'Tin nhắn phải có độ dài từ 1 đến 4000 ký tự.' }, 400);
  }

  const history = Array.isArray(body.history)
    ? body.history
        .filter((item) => item && ['user', 'model'].includes(item.role) && typeof item.text === 'string')
        .slice(-MAX_HISTORY_ITEMS)
        .map((item) => ({ role: item.role, parts: [{ text: item.text.slice(0, MAX_MESSAGE_LENGTH) }] }))
    : [];

  try {
    const knowledge = await loadKnowledge();
    const systemInstruction = `Bạn là trợ lý tài liệu chính thức của FormMail Hub. Trả lời bằng ngôn ngữ của người dùng, ưu tiên tiếng Việt nếu họ hỏi bằng tiếng Việt. Chỉ sử dụng thông tin trong hai tài liệu SOURCE DOCUMENT bên dưới. Không được bịa đặt tính năng, endpoint, giá, chính sách, tích hợp hoặc hướng dẫn không có trong tài liệu. Nếu câu hỏi nằm ngoài tài liệu, hãy nói rõ rằng tài liệu hiện không cung cấp thông tin đó và đề nghị liên hệ https://formmail.vietutd.com/contact. Trả lời ngắn gọn, rõ ràng.\n\nSOURCE DOCUMENTS:\n${knowledge}`;

    // Gọi TRỰC TIẾP Google Gemini API (Server Vercel tại Mỹ kết nối thẳng Google, không qua Proxy trung gian)
    const targetUrl = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${encodeURIComponent(GEMINI_API_KEY)}`;

    const response = await fetch(targetUrl, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        system_instruction: { parts: [{ text: systemInstruction }] },
        contents: [...history, { role: 'user', parts: [{ text: message }] }],
        generationConfig: { temperature: 0.2, maxOutputTokens: 900 },
      }),
    });

    const rawText = await response.text();
    let result;
    try {
      result = JSON.parse(rawText);
    } catch (parseError) {
      console.error('Gemini response is not valid JSON:', rawText);
      return json({ error: 'Dịch vụ AI phản hồi không hợp lệ.' }, 502);
    }

    if (!response.ok) {
      console.error('Gemini API Error Detail:', result);
      return json({ error: result?.error?.message || 'Gemini không thể xử lý yêu cầu lúc này.' }, 502);
    }

    const answer = result?.candidates?.[0]?.content?.parts?.map((part) => part.text || '').join('').trim();
    if (!answer) return json({ error: 'Không nhận được câu trả lời từ Gemini.' }, 502);

    return json({ answer });
  } catch (error) {
    console.error('Server Internal Error:', error);
    return json({ error: 'Không thể kết nối chatbot lúc này.', detail: error.message }, 502);
  }
}
