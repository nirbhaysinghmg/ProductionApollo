import config from '../config.js';

/**
 * Generate dynamic suggested questions based on conversation context
 * @param {Array} conversationHistory - Array of conversation messages
 * @param {string} currentTopic - Current topic being discussed
 * @returns {Promise<Array>} Array of suggested questions
 */
export async function generateDynamicQuestions(conversationHistory = [], currentTopic = '') {
    try {
        const response = await fetch(config.dynamicQuestionsUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                conversation_history: conversationHistory,
                current_topic: currentTopic
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.questions || [];
    } catch (error) {
        console.error('Error generating dynamic questions:', error);
        // Return fallback questions if API fails
        return [
            "What is the warranty period for Apollo tyres?",
            "How do I find a nearby Apollo dealer?",
            "What are the different types of Apollo tyres?",
            "How to maintain my tyres properly?",
            "What is the recommended tyre pressure?"
        ];
    }
}

/**
 * Get suggested questions (first 5 hardcoded + dynamic questions)
 * @param {Array} conversationHistory - Array of conversation messages
 * @param {string} currentTopic - Current topic being discussed
 * @returns {Promise<Array>} Combined array of suggested questions
 */
export async function getSuggestedQuestions(conversationHistory = [], currentTopic = '') {
    // If we have conversation history, generate all dynamic questions
    if (conversationHistory.length > 0) {
        try {
            const dynamicQuestions = await generateDynamicQuestions(conversationHistory, currentTopic);
            
            // Use all dynamic questions when there's conversation history
            return dynamicQuestions.slice(0, config.showNumberOfQuestions);
        } catch (error) {
            console.error('Error getting dynamic questions, using fallback:', error);
            // Return fallback questions if dynamic generation fails
            return [
                "What is the warranty period for Apollo tyres?",
                "How do I find a nearby Apollo dealer?",
                "What are the different types of Apollo tyres?",
                "How to maintain my tyres properly?",
                "What is the recommended tyre pressure?"
            ].slice(0, config.showNumberOfQuestions);
        }
    }
    
    // Use initial hardcoded questions only when there's no conversation history
    return config.initialSuggestedQuestions.slice(0, config.showNumberOfQuestions);
}

/**
 * Extract current topic from conversation history
 * @param {Array} conversationHistory - Array of conversation messages
 * @returns {string} Current topic
 */
export function extractCurrentTopic(conversationHistory) {
    if (conversationHistory.length === 0) return '';
    
    // Get the last few messages to determine current topic
    const recentMessages = conversationHistory.slice(-3);
    const lastUserMessage = recentMessages.find(msg => msg.role === 'user')?.text || '';
    
    // Simple topic extraction based on keywords
    const keywords = {
        'warranty': 'warranty',
        'dealer': 'dealer',
        'price': 'pricing',
        'maintenance': 'maintenance',
        'installation': 'installation',
        'safety': 'safety',
        'performance': 'performance'
    };
    
    const lowerMessage = lastUserMessage.toLowerCase();
    for (const [keyword, topic] of Object.entries(keywords)) {
        if (lowerMessage.includes(keyword)) {
            return topic;
        }
    }
    
    return 'general';
} 