const fs = require('fs');
const path = require('path');
const axios = require('axios');

const OPENAI_API_KEY = '';

const summarizeConversation = async (csvFilePath) => {
    try {
        // CSVファイルを読み込み
        const data = fs.readFileSync(csvFilePath, 'utf8');
        const rows = data.split('\n').slice(1); // ヘッダー行をスキップ

        let conversationText = '';
        rows.forEach(row => {
            const columns = row.split(',');
            if (columns.length >= 2) {
                const user = columns[0].trim();
                const ai = columns[1].trim();
                if (user && ai) {
                    conversationText += `User: ${user}\nAI: ${ai}\n`;
                }
            }
        });

        const prompt = `以下の会話を基に、ユーザーが何を言いたかったのかを100文字程度で要約してください。家族に伝えたい内容を中心に、感情や重要なポイントを含めてください。\n\n${conversationText}`;

        // OpenAIに要約を依頼
        const response = await axios.post('https://api.openai.com/v1/chat/completions', {
            model: 'gpt-3.5-turbo',
            messages: [
                { role: "system", content: "以下の会話を要約してください。" },
                { role: "user", content: prompt }
            ],
            max_tokens: 150,
        }, {
            headers: {
                'Authorization': `Bearer ${OPENAI_API_KEY}`,
                'Content-Type': 'application/json',
            }
        });

        const summary = response.data.choices[0].message.content.trim();
        console.log(`Summary: ${summary}`);

        // 要約をchat.csvに保存
        fs.writeFileSync(path.join(__dirname, 'chat.csv'), summary);
        console.log('Summary saved to chat.csv');
    } catch (err) {
        console.error(`Error summarizing conversation: ${err.message}`);
        if (err.response) {
            console.error(`Response data: ${JSON.stringify(err.response.data)}`);
        }
    }
};

const csvFilePath = process.argv[2];
summarizeConversation(csvFilePath);
