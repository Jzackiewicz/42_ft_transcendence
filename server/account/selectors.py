from datetime import datetime

# FOR GET, READ REQUESTS

def get_example_data(*, param: str) -> dict:
	if param:
		message = f"Got parameter for GET request: {param}"
	else:
		message = "Provided no parameter for GET request."
	return {
		"message": message,
		"datetime_called": datetime.now().isoformat()
	}