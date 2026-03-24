# chatbot.py
from openai import OpenAI
import streamlit as st

def get_ayurvedic_advice(user_input, dominant_dosha, api_key):
    """
    Call OpenAI API to get personalized advice based on user input and detected dosha.
    """
    if not api_key:
        return "⚠️ Please provide an OpenAI API key in the sidebar to get AI-powered personalized advice."
    try:
        client = OpenAI(api_key=api_key)
        
        system_prompt = (
            "You are an expert Ayurvedic practitioner. Provide practical, compassionate, "
            "and personalized Ayurvedic advice based on the user's symptoms. "
            "Keep it concise, supportive, and actionable. Format your response clearly with bullet points. "
            "Do not provide medical diagnoses."
        )
        
        user_prompt = f"The user has the following symptoms/concerns: '{user_input}'. "
        if dominant_dosha != "Balanced / Undetermined":
            user_prompt += f"Their dominant imbalanced dosha appears to be {dominant_dosha}. "
        
        user_prompt += "Provide brief, personalized dietary and lifestyle recommendations to bring them back to balance."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        print(response.choices[0].message.content)
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ An error occurred while generating advice: {str(e)}"
