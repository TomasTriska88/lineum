import { GoogleGenerativeAI } from "@google/generative-ai";
import { env } from "$env/dynamic/private";
const { GEMINI_API_KEY } = env;
import aiIndex from "$lib/data/ai_index.json";

// Resilient API key access
// Persona Imports (Live updates via Vite)
import linaPersona from '../../../LINA_PERSONA.md?raw';
import designGuide from '../../../DESIGN_GUIDE.md?raw';

export const SYSTEM_PROMPT = `
${linaPersona}

---

**FROM DESIGN GUIDE (BEHAVIORAL RULES):**
${designGuide}

---

**PROJECT CONTEXT (Context Window):**
Lineum Core is a discrete simulation of field interactions. The current version is defined by the indexed documentation.
You have access to the following indexed project knowledge:
${JSON.stringify(aiIndex.map(f => ({ path: f.path, status: f.status, type: f.type, content: f.content.substring(0, 3000) })), null, 2)}
`;

export async function chat(messages: { role: 'user' | 'model', parts: { text: string }[] }[], context?: string) {
    if (!GEMINI_API_KEY) {
        console.error("CRITICAL: GEMINI_API_KEY is missing from environment variables.");
        throw new Error("I'm waiting for my scientific core to be initialized (API Key missing). Please contact support.");
    }

    try {
        const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);

        let dynamicPrompt = SYSTEM_PROMPT;
        if (context) {
            dynamicPrompt += `\n[CURRENT USER CONTEXT]: The user is currently viewing the page: "${context}". Tailor your response to this location.`;
        }

        const model = genAI.getGenerativeModel({
            model: "gemini-2.5-flash",
            systemInstruction: dynamicPrompt
        });

        const lastMessage = messages[messages.length - 1].parts[0].text;
        const history = messages.slice(0, -1);

        const chatSession = model.startChat({ history });
        const result = await chatSession.sendMessage(lastMessage);
        const response = await result.response;
        return response.text();
    } catch (error: any) {
        console.error("AI Agent Core Error:", error);
        throw new Error(error.message || "I had a small glitch in my simulation logic. Could you try asking that again?");
    }
}
