import os
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load API key from .env file
load_dotenv()
client = OpenAI(api_key="")

class FitnessUser:
    """Represents a fitness app user."""
    def __init__(self, id: str, age: int, fitness_level: int, 
                 goals: List[str], preferences: List[str], 
                 limitations: List[str] = None):
        self.id = id
        self.age = age
        self.fitness_level = fitness_level
        self.goals = goals
        self.preferences = preferences
        self.limitations = limitations or []

    def __str__(self):
        return f"User {self.id}: Level {self.fitness_level}, Goals: {', '.join(self.goals)}"


# ========  AGENT 1 — Deterministic Planner ========
# Create a rule-based planner that adjusts:
# - number of workout days
# - intensity
# - workout types
# - session duration
# based on fitness level and goals

def deterministic_agent(user: FitnessUser) -> Dict:
    """
    A rule-based agent that creates workout plans based on user fitness level and goals.
    Returns a dictionary with a weekly schedule.
    """
    # Initialize weekly schedule
    weekly_schedule = {}
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Determine workout parameters based on fitness level
    if user.fitness_level <= 1:  # Beginner
        workout_days = 3
        base_intensity = "light"
        base_duration = 30
        workout_day_indices = [0, 2, 4]  # Monday, Wednesday, Friday
    elif user.fitness_level <= 3:  # Intermediate
        workout_days = 4
        base_intensity = "moderate"
        base_duration = 45
        workout_day_indices = [0, 2, 4, 6]  # Monday, Wednesday, Friday, Sunday
    else:  # Advanced
        workout_days = 5
        base_intensity = "high"
        base_duration = 60
        workout_day_indices = [0, 1, 3, 5, 6]  # Monday, Tuesday, Thursday, Saturday, Sunday
    
    # Adjust for limitations
    if any("time" in limitation.lower() for limitation in user.limitations):
        base_duration = min(base_duration, 30)
        workout_days = min(workout_days, 4)
        
    if any("joint" in limitation.lower() for limitation in user.limitations):
        if base_intensity == "high":
            base_intensity = "moderate"
    
    # Map goals to workout types
    goal_to_workout = {
        "weight management": ["cardio", "HIIT", "strength training"],
        "stress reduction": ["yoga", "active recovery", "cardio"],
        "strength building": ["strength training", "HIIT"],
        "joint mobility": ["flexibility", "swimming", "yoga"],
        "endurance": ["cardio", "swimming"],
        "muscle gain": ["strength training"],
        "flexibility": ["yoga", "flexibility"]
    }
    
    # Select workout types based on user's goals
    user_workout_types = []
    for goal in user.goals:
        for g, workouts in goal_to_workout.items():
            if g.lower() in goal.lower():
                user_workout_types.extend(workouts)
    
    # If no workouts were selected, use a default set
    if not user_workout_types:
        user_workout_types = ["cardio", "strength training", "flexibility"]
    
    # Remove duplicates while preserving order
    user_workout_types = list(dict.fromkeys(user_workout_types))
    
    # Consider user preferences
    for pref in user.preferences:
        if "swimming" in pref.lower() and "swimming" not in user_workout_types:
            user_workout_types.append("swimming")
        elif "outdoor" in pref.lower() and "cardio" not in user_workout_types:
            user_workout_types.append("cardio")
        elif "home" in pref.lower() and all(w not in user_workout_types for w in ["yoga", "HIIT"]):
            user_workout_types.append("HIIT")
    
    # Create descriptions for each workout type
    workout_descriptions = {
        "strength training": "Focus on building muscle with weights or bodyweight exercises",
        "cardio": "Aerobic exercises to improve heart health and endurance",
        "flexibility": "Stretching exercises to improve range of motion",
        "HIIT": "High-intensity interval training for efficient calorie burn",
        "active recovery": "Light activity to promote recovery and reduce soreness",
        "yoga": "Combination of strength, flexibility, and mindfulness",
        "swimming": "Low-impact full-body workout in water"
    }
    
    # Create the weekly schedule
    for i in range(min(workout_days, len(workout_day_indices))):
        day = days[workout_day_indices[i]]
        workout_type = user_workout_types[i % len(user_workout_types)]
        
        # Adjust intensity based on workout type
        intensity = base_intensity
        if workout_type == "active recovery" and intensity != "light":
            intensity = "light"
        elif workout_type == "HIIT" and intensity == "light":
            intensity = "moderate"
        
        # Adjust duration based on workout type
        duration = base_duration
        if workout_type == "HIIT" and duration > 30:
            duration = 30
        elif workout_type == "yoga" and duration < 45:
            duration = 45
        
        weekly_schedule[day] = {
            "type": workout_type,
            "duration": duration,
            "intensity": intensity,
            "description": workout_descriptions.get(workout_type, "Custom workout")
        }
    
    return {"weekly_schedule": weekly_schedule}
   
    



# ======== AGENT 2 — LLM-Based Planner ========
# We've handled the API part. Your task is to COMPLETE THE PROMPT below
# that will instruct the LLM how to generate the plan.

def llm_agent(user: FitnessUser) -> Dict:
    goals_text = ", ".join(user.goals)
    preferences_text = ", ".join(user.preferences)
    limitations_text = ", ".join(user.limitations) if user.limitations else "None"

    prompt = f"""
As a certified fitness trainer, create a personalized weekly workout plan for this client.

Client Information:
- Age: {user.age}
- Fitness Level: {user.fitness_level}/5 (1=beginner, 5=advanced)
- Goals: {goals_text}
- Preferences: {preferences_text}
- Limitations: {limitations_text}

THINK STEP-BY-STEP using this process:

Step 1: Assess Fitness Level
- Analyze what this fitness level means for workout frequency and intensity
- Consider age-related factors

Step 2: Analyze Goals
- Break down each goal and what types of workouts support it
- Identify primary vs. secondary goals

Step 3: Consider Limitations
- Identify how each limitation affects the plan
- Determine necessary modifications or workout types to avoid

Step 4: Apply Preferences
- Incorporate preferred workout styles and settings
- Balance preferences with goal requirements

Step 5: Design Weekly Structure
- Determine optimal number of workout days
- Allocate workout types across the week
- Balance intensity and recovery

Step 6: Create Specific Workouts
- Define each workout with appropriate duration and intensity
- Include specific exercises that match the client's situation

Output Format:
Return ONLY a valid JSON object (no markdown, no extra text) with this structure:
{{
    "chain_of_thought": {{
        "step_1_fitness_assessment": "Your analysis of their fitness level...",
        "step_2_goal_analysis": "Breaking down their goals...",
        "step_3_limitations_impact": "How limitations affect the plan...",
        "step_4_preferences_integration": "How to incorporate preferences...",
        "step_5_weekly_structure": "Reasoning for number of days and workout distribution...",
        "step_6_final_decisions": "Key decisions made for this specific plan..."
    }},
    "reasoning": "1-2 sentence summary of the overall approach",
    "weekly_schedule": {{
        "Monday": {{
            "type": "cardio",
            "duration": 30,
            "intensity": "moderate",
            "description": "Specific exercises with details"
        }}
    }},
    "considerations": "Special adaptations or progressive recommendations"
}}

Important:
- Work through ALL 6 steps in your chain_of_thought
- Be specific in each reasoning step
- Only include workout days in weekly_schedule
- Ensure proper JSON formatting
- Use realistic durations (20-60 minutes)
- Make descriptions actionable
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a certified fitness trainer specializing in personalized workout planning. You think step-by-step before creating plans. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Slightly higher for better reasoning
        )
        result_text = response.choices[0].message.content
        
        # Clean up potential markdown formatting
        result_text = result_text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        return json.loads(result_text)

    except Exception as e:
        print(f"Error: {e}")
        fallback = deterministic_agent(user)
        return {
            "chain_of_thought": {
                "error": f"LLM failed: {str(e)}"
            },
            "reasoning": "Fallback to rule-based plan due to error",
            "weekly_schedule": fallback["weekly_schedule"],
            "considerations": "Using deterministic agent as backup."
        }


# ======== COMPARISON LOGIC (DO NOT EDIT) ========

def compare_workout_planning(users: List[FitnessUser]):
    print("\n===== WORKOUT PLAN COMPARISON =====")
    for i, user in enumerate(users, 1):
        print(f"\n--- User {i}: {user.id} ---")
        print(f"Age: {user.age} | Fitness Level: {user.fitness_level}/5")
        print(f"Goals: {', '.join(user.goals)}")
        print(f"Preferences: {', '.join(user.preferences)}")
        print(f"Limitations: {', '.join(user.limitations)}")

        det_plan = deterministic_agent(user)
        print("\n[Deterministic Agent]")
        for day, workout in det_plan["weekly_schedule"].items():
            print(f"- {day}: {workout['type']} ({workout['intensity']}, {workout['duration']} min)")

        llm_plan = llm_agent(user)
        print("\n[LLM Agent with Chain-of-Thought]")
        
        # Display the thinking process
        if "chain_of_thought" in llm_plan:
            print("\n🧠 THINKING PROCESS:")
            cot = llm_plan["chain_of_thought"]
            for step_key, step_value in cot.items():
                step_name = step_key.replace("_", " ").title()
                print(f"  {step_name}:")
                print(f"    {step_value}")
        
        print(f"\n📋 REASONING: {llm_plan.get('reasoning', 'No reasoning provided')}")
        
        print("\n📅 WEEKLY SCHEDULE:")
        for day, workout in llm_plan["weekly_schedule"].items():
            print(f"- {day}: {workout['type']} ({workout['intensity']}, {workout['duration']} min)")
            print(f"  → {workout['description']}")
        
        print(f"\n⚠️  CONSIDERATIONS: {llm_plan.get('considerations', 'None')}")
        print("-" * 80)


# ======== SAMPLE USERS ========

def main():
    users = [
        FitnessUser(
            id="U001",
            age=35,
            fitness_level=2,
            goals=["weight management", "stress reduction"],
            preferences=["home workouts", "morning routines"],
            limitations=["limited equipment", "time constraints (max 30 min/day)"]
        ),
        FitnessUser(
            id="U002",
            age=55,
            fitness_level=3,
            goals=["joint mobility", "strength building"],
            preferences=["outdoor activities", "swimming"],
            limitations=["mild joint stiffness"]
        )
    ]

    compare_workout_planning(users)

if __name__ == "__main__":
    main()
