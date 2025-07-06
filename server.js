// server.js
const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Serve static files (HTML, CSS, JS, words.json)
app.use(express.static('public'));
app.use(express.json());

// Load words from local JSON file
const WORDS_PATH = path.join(__dirname, 'public', 'words.json');

// API endpoint to serve a random sample of 30 words
app.post('/api/generate-words', async (req, res) => {
    try {
        const rawData = fs.readFileSync(WORDS_PATH, 'utf8');
        const allWords = JSON.parse(rawData);

        if (!Array.isArray(allWords) || allWords.length < 30) {
            throw new Error('words.json must contain at least 30 words');
        }

        // Shuffle and select 30 random words
        const shuffled = allWords.sort(() => Math.random() - 0.5);
        const selectedWords = shuffled.slice(0, 30);

        res.json({ words: selectedWords });
    } catch (error) {
        console.error('Failed to load words:', error);
        res.status(500).json({ error: 'Failed to load words from file' });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`🇫🇷 French Gender Swipe Game Server`);
    console.log(`🚀 Server running at http://localhost:${PORT}`);
    console.log(`📚 Serving words from local file: public/words.json`);
});
