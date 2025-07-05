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
        const prompt = `Generate exactly 20 common French nouns with their gender. Format each as JSON like this:
{"word": "chambre", "gender": "feminine"}
{"word": "livre", "gender": "masculine"}

Rules:
- Only include common, everyday French nouns
- No proper nouns or names
- Gender must be exactly "masculine" or "feminine"
- No explanations, just the 20 JSON objects, one per line
- Mix of masculine and feminine words
- Words should be appropriate for language learners`;

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
        
        if (words.length < 20) {
            throw new Error('Not enough valid words generated');
        }
        
        res.json({ words: words.slice(0, 20) });
        
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