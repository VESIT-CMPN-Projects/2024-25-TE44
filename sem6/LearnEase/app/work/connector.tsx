import axios from 'axios';
import dotenv from 'dotenv';
const API_KEY = process.env.GEMINI_API_KEY;
const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${API_KEY}`;

export const generateStudyPlan = async (hoursPerDay: string, weakSubjects: string[], topics: { [key: string]: string[] }) => {
    // Calculate weekly hours
    const weeklyHours = (parseInt(hoursPerDay) * 7).toString();
    
    // Format weak subjects and topics
    const formattedSubjects = Object.keys(topics).map(subject => {
        const isWeak = weakSubjects.includes(subject);
        return `**${subject}${isWeak ? ' (Weak Subject)' : ''}**: ${topics[subject]?.join(', ') || 'General Study'}`;
    }).join('\n');

    const prompt = `
    **🎯 Personalized Study Plan Generator**
    
    Generate a well-structured weekly study plan for a student based on these preferences:

    - **Hours Per Day:** ${hoursPerDay}
    - **Total Weekly Study Hours:** ${weeklyHours}
    - **Subjects & Topics to Focus On:**  
    ${formattedSubjects}
    
    **Important Instructions:**
    - Allocate approximately 60% of the time to weak subjects: ${weakSubjects.join(', ')}
    - Create a balanced schedule across all 7 days of the week
    - For each day, distribute the ${hoursPerDay} hours in logical blocks

    📝 **Study Plan Format:**  
    {
      "studyPlan": [
        {
          "day": "Monday",
          "sessions": [
            {
              "subject": "Subject Name",
              "topic": "Specific Topic Name",
              "time_allocated": "X hours",
              "study_tips": "Specific study tip for this topic"
            }
          ]
        },
        ... (for all 7 days)
      ]
    }

    Ensure that:
    1. The sum of hours for each day matches the specified hours per day (${hoursPerDay})
    2. Weak subjects receive more focus
    3. Every selected topic appears at least once in the week
    4. Each session has a personalized study tip
    `;

    try {
        const response = await axios.post(
            API_URL, 
            {
                contents: [{ parts: [{ text: prompt }] }]
            },
            {
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        // Extract the text from the response
        const generatedText = response.data?.candidates?.[0]?.content?.parts?.[0]?.text;
        
        if (!generatedText) {
            return { 
                error: "Invalid response format from API.",
                studyPlan: [] 
            };
        }
        
        try {
            // Extract JSON content from markdown code blocks if present
            let jsonText = generatedText;
            
            // Check if the response is wrapped in markdown code blocks
            const jsonRegex = /```(?:json)?\s*(\{[\s\S]*\})\s*```/;
            const match = generatedText.match(jsonRegex);
            
            if (match && match[1]) {
                jsonText = match[1];
            }
            
            // Try to parse the JSON
            return JSON.parse(jsonText);
        } catch (parseError) {
            console.error("❌ Error parsing JSON response:", parseError);
            console.log("Raw response:", generatedText);
            return { 
                error: "Failed to parse study plan. The API returned invalid JSON.",
                studyPlan: [] 
            };
        }
        
    } catch (error) {
        console.error("❌ Error generating study plan:", error);
        return { 
            error: "Failed to fetch study plan. Please try again.",
            studyPlan: [] 
        };
    }
};