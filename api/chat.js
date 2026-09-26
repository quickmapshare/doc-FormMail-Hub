const MAX_MESSAGE_LENGTH = 4000;
const MAX_HISTORY_ITEMS = 10;
const MODEL = 'gemini-3.6-flash';

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
  const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

  if (!GEMINI_API_KEY) {
    return json({ error: 'Chatbot GEMINI_API_KEY is not configured on Vercel.' }, 503);
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
    const systemInstruction = `You are the official documentation assistant for FormMail Hub. Respond in the user's language (prefer English if the prompt is in English). Strictly use only the information provided in the two SOURCE DOCUMENTS below. Do not fabricate features, endpoints, pricing, policies, integrations, or instructions not present in the documentation. If a question is outside the docs, explicitly state that the documentation does not currently provide that information and suggest contacting https://formmail.vietutd.com/contact. Keep answers concise and clear.\n\nSOURCE DOCUMENTS:\n${knowledge}`;

    // Call Google Gemini API directly from Vercel US server
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
      return json({ error: 'Invalid response from AI service.' }, 502);
    }

    if (!response.ok) {
      console.error('Gemini API Error Detail:', result);
      return json({ error: result?.error?.message || 'Gemini is currently unable to process your request.' }, 502);
    }

    const answer = result?.candidates?.[0]?.content?.parts?.map((part) => part.text || '').join('').trim();
    if (!answer) return json({ error: 'No answer received from Gemini.' }, 502);

    // GHI LOG CHAT TRỰC TIẾP LÊN VERCEL LOGS
    console.log(`[CHAT_LOG] User: "${message}" | Bot: "${answer.replace(/\n/g, ' ')}"`);

    // Gửi log trực tiếp về Discord Webhook
    const discordUrl = process.env.DISCORD_WEBHOOK_URL;
    if (discordUrl) {
      const content = `💬 **FormMail Hub Chat**\n👤 **User:** ${message}\n🤖 **Bot:** ${answer}`;
      fetch(discordUrl, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ content }),
      }).catch((err) => console.error('Discord log error:', err));
    }

    return json({ answer });
  } catch (error) {
    console.error('Server Internal Error:', error);
    return json({ error: 'Unable to connect to the chatbot service at this time.', detail: error.message }, 502);
  }
}
