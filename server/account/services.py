from datetime import datetime

# For POST, CREATE, UPDATE REQUESTS

def create_example_record(*, message: str, mood_grade: int) -> dict:
	if mood_grade < 4:
		users_mood = "Bad"
	elif mood_grade < 7:
		users_mood = "Neutral"
	else:
		users_mood = "Good"
	return {
		"message": f"POST ECHO: {message}",
		"users_mood": users_mood,
		"datetime_called": datetime.now().isoformat()
	}