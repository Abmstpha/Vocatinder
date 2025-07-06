// server.js
const express = require('express');
const path = require('path');
const fetch = require('node-fetch');

const app = express();
const PORT = 3000;

// Mistral API configuration
const MISTRAL_API_KEY = process.env.MISTRAL_API_KEY;
const MISTRAL_API_URL = 'https://api.mistral.ai/v1/chat/completions';

// Serve static files
app.use(express.static('public'));
app.use(express.json());

// API endpoint to generate French words
app.post('/api/generate-words', async (req, res) => {
    try {
        const prompt = `Generate exactly 100 common French nouns with their gender. Format each as JSON like this:
{"word": "chambre", "gender": "feminine"}
{"word": "livre", "gender": "masculine"}

Rules:
- Only include common, everyday French nouns
- No proper nouns or names
- Words must span across daily life: home, work, school, groceries, transport, health, objects, technology, food, street, conversations, etc.
- Ensure diversity: include a mix of indoor/outdoor, physical/abstract, personal/public, and family/social concepts
- Do not include regional slang, archaic, or rare terms
- Make the selection unpredictable and balanced
- Do not repeat words in the same sample
- Gender must be exactly "masculine" or "feminine"
- No explanations or numbering, just the 30 JSON objects, one per line
- Always a balanced mix of masculine and feminine nouns
- Words should be suitable for French learners to improve everyday vocabulary`;

        const response = await fetch(MISTRAL_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${MISTRAL_API_KEY}`
            },
            body: JSON.stringify({
                model: 'mistral-small-latest',
                messages: [{
                    role: 'user',
                    content: prompt
                }],
                max_tokens: 1000,
                temperature: 0.7
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const content = data.choices[0].message.content;
        
        // Parse the JSON lines
        const lines = content.split('\n').filter(line => line.trim());
        const words = [];
        
        for (const line of lines) {
            try {
                const wordObj = JSON.parse(line.trim());
                if (wordObj.word && wordObj.gender && 
                    (wordObj.gender === 'masculine' || wordObj.gender === 'feminine')) {
                    words.push(wordObj);
                }
            } catch (e) {
                console.warn('Failed to parse line:', line);
            }
        }
        
        if (words.length < 30) {
            throw new Error('Not enough valid words generated');
        }
        
        res.json({ words: words.slice(0, 30) });
        
    } catch (error) {
        console.error('Mistral API error:', error);
        res.status(500).json({ error: 'Failed to generate words from Mistral AI' });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`🇫🇷 French Gender Swipe Game Server`);
    console.log(`🚀 Server running at http://localhost:${PORT}`);
    console.log(`🎮 Open your browser and go to: http://localhost:${PORT}`);
    console.log(`🤖 Powered by Mistral AI`);
});