const axios = require('axios');

const OPENAI_API_KEY = '';

const prompt = process.argv[2];
const pastMessages = JSON.parse(process.argv[3] || "[]");

const aiMessage = {
    role: "user",
    content: prompt
};

const systemMessage = {
    role: "system",
    content: "あなたは高齢者に寄り添う会話の専門家です。ユーザーが話すことに対して、短い相槌やおうむ返しを使い、相手の話を促進するようにしてください。話が途切れた場合には、しばらく待って呼びかけをしてください。必ず短く的確に応えてください。"
};

if (pastMessages.length === 0) {
    pastMessages.unshift(systemMessage);
}

pastMessages.push(aiMessage);

axios.post('https://api.openai.com/v1/chat/completions', {
    model: 'gpt-3.5-turbo',
    messages: pastMessages,
    max_tokens: 100,
    stop: ["。", "！", "？"],
}, {
    headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
    }
}).then(response => {
    const responseMessage = response.data.choices[0].message.content;
    pastMessages.push({ role: "assistant", content: responseMessage });
    console.log(JSON.stringify({ responseMessage: responseMessage, pastMessages }));
}).catch(error => {
    console.error('API request failed: ', error.message);
    console.error('Error response: ', error.response ? error.response.data : 'No response data');
    process.exit(1);
});
