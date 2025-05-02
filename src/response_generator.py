import random

class ResponseGenerator:
    """
    Class responsible for generating responses to user queries.
    This is a simple implementation that can be extended with more advanced
    natural language processing or AI capabilities.
    """
    
    def __init__(self):
        """
        Initialize the ResponseGenerator with predefined responses.
        """
        # Dictionary of predefined responses for different types of queries
        self.responses = {
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Greetings! How may I assist you?",
                "Hello! I'm listening. What do you need?"
            ],
            "farewell": [
                "Goodbye! Have a great day!",
                "See you later! Take care!",
                "Farewell! Come back anytime you need assistance.",
                "Goodbye! It was nice talking to you."
            ],
            "thanks": [
                "You're welcome!",
                "Happy to help!",
                "Anytime!",
                "No problem at all!"
            ],
            "weather": [
                "I'm sorry, I don't have access to weather information at the moment.",
                "To get weather information, you would need to connect me to a weather service API.",
                "I can't check the weather right now, but I can help with other things."
            ],
            "time": [
                "I don't have access to the current time. You might want to check your device's clock.",
                "I'm not able to tell the time right now.",
                "Sorry, I can't provide the current time."
            ],
            "default": [
                "I'm not sure how to respond to that. Could you rephrase?",
                "I didn't quite understand. Can you say that differently?",
                "I'm still learning and don't know how to answer that yet.",
                "That's beyond my current capabilities, but I'm learning!"
            ]
        }
    
    def generate_response(self, query):
        """
        Generate a response based on the user's query.
        
        Args:
            query (str): The user's query
            
        Returns:
            str: The generated response
        """
        query_lower = query.lower()
        
        # Check for greetings
        if any(word in query_lower for word in ["hello", "hi", "hey", "greetings"]):
            return random.choice(self.responses["greeting"])
        
        # Check for farewells
        elif any(word in query_lower for word in ["bye", "goodbye", "see you", "farewell"]):
            return random.choice(self.responses["farewell"])
        
        # Check for thanks
        elif any(word in query_lower for word in ["thanks", "thank you", "appreciate"]):
            return random.choice(self.responses["thanks"])
        
        # Check for weather queries
        elif any(word in query_lower for word in ["weather", "temperature", "forecast", "rain", "sunny"]):
            return random.choice(self.responses["weather"])
        
        # Check for time queries
        elif any(word in query_lower for word in ["time", "hour", "clock"]):
            return random.choice(self.responses["time"])
        
        # Default response for unrecognized queries
        else:
            return random.choice(self.responses["default"])
    
    def add_custom_response(self, category, response):
        """
        Add a custom response to a category.
        
        Args:
            category (str): The category to add the response to
            response (str): The response to add
            
        Returns:
            bool: True if the response was added successfully, False otherwise
        """
        if category in self.responses:
            self.responses[category].append(response)
        else:
            self.responses[category] = [response]
        return True