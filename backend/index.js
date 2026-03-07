const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { GoogleGenerativeAI } = require('@google/generative-ai');

// Load environment variables from .env file
dotenv.config();

const app = express();
const port = process.env.PORT || 5000;

// Enable CORS for frontend communication
app.use(cors());
// Parse incoming JSON requests
app.use(express.json());

// Initialize Google Gemini AI
// Ensure you have GEMINI_API_KEY in your .env file
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || '');

/**
 * Endpoint: POST /api/generate-email
 * Purpose: Receives email parameters and generates an email using Gemini AI.
 */
app.post('/api/generate-email', async (req, res) => {
    const { purpose, tone, audience, points } = req.body;

    // 1. Basic Validation
    if (!purpose || !tone || !audience || !points) {
        return res.status(400).json({ 
            error: "All fields (purpose, tone, audience, points) are required." 
        });
    }

    try {
        // 2. Access the Gemini-1.5-Flash model (latest and fastest)
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

        // 3. Construct the prompt for AI
        const prompt = `
            You are a professional email writer. Write a well-structured email based on the following details:
            - Purpose: ${purpose}
            - Tone: ${tone}
            - Audience: ${audience}
            - Key Points: ${points}

            Please generate a response in the following JSON format ONLY:
            {
                "subject": "[A compelling subject line]",
                "email": "[The full email body with proper formatting and placeholders where necessary]"
            }
        `;

        // 4. Generate content
        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();

        // 5. Clean and Parse JSON response
        // Sometimes AI includes markdown backticks, we remove them for parsing
        const cleanedText = text.replace(/```json|```/g, '').trim();
        const jsonResponse = JSON.parse(cleanedText);

        // 6. Return the generated email
        res.json(jsonResponse);

    } catch (error) {
        console.error("Error generating email:", error);
        res.status(500).json({ 
            error: "Failed to generate email. Please check your API key and try again.",
            details: error.message 
        });
    }
});

// Root endpoint to check server status
app.get('/', (req, res) => {
    res.send('AI Email Generator Backend is Running!');
});

// Start the server
app.listen(port, () => {
    console.log(`Backend server is spinning at http://localhost:${port}`);
});
