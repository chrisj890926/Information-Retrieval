# README

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [API Endpoints](#api-endpoints)
6. [File Descriptions](#file-descriptions)
   - [app](#app)
   - [chattypes](#chattypes)
   - [coursesranking](#coursesranking)
   - [promptv5](#promptv5)
   - [querygenerator](#querygenerator)
   - [responsegenerator](#responsegenerator)
   - [requirements](#requirements)
7. [Testing](#testing)
8. [Environment Variables](#environment-variables)
9. [Dependencies](#dependencies)

---

## Project Overview

This project is a Flask-based backend system designed to assist with course recommendations using a combination of vector-based matching and semantic analysis. The system handles course data, generates user queries, and provides structured responses.

---

## Features

- Semantic course recommendations using Sentence Transformers.
- Integration with Groq API for enhanced query and response generation.
- Support for multilingual inputs and detailed course descriptions.
- RESTful API design.

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd <project-directory>
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables (see [Environment Variables](#environment-variables)).

---

## Usage

1. Run the Flask server:
   ```bash
   python app.py
   ```
2. The server will be accessible at `http://127.0.0.1:5000/`.

---

## API Endpoints

### `/chat`

- **Method**: POST
- **Description**: Handles course recommendation requests.
- **Request Body**:
  ```json
  {
    "messages": [{"role": "user", "content": "I want to learn machine learning"}],
    "semesters": "Fall 2023",
    "current_selected_course_id": ["12345"]
  }
  ```
- **Response**:
  ```json
  {
    "response": "Here are the top courses...",
    "rankedCourseIds": ["56789", "12345"]
  }
  ```

---

## File Descriptions
### app
### app.py

- **Description**:\
  The main Flask application script that serves as the entry point of the project. It processes user requests and integrates multiple modules for query generation, ranking, and response generation.

- **Key Features**:

  1. Defines the `/chat` endpoint:
     - Accepts JSON input for course recommendations.
     - Processes user queries and generates a ranked list of recommended courses.
  2. Integrates with other modules:
     - `chat_types` for structured message handling.
     - `query_generator` for converting user input into structured queries.
     - `courses_ranking_v5` for ranking courses based on semantic similarity.
     - `response_generator` for generating user-facing responses.
  3. Logs detailed debugging information to track incoming requests and processed data.

- **Usage**:\
  Run the following command to start the server:

  ```bash
  python app.py
  ```

  The server will start on `http://127.0.0.1:5000/`.
### chat_types
### chat\_types.py

- **Description**:\
  Defines the data structures used for communication between different components of the project. It standardizes the input and output formats to ensure consistency.

- **Key Classes**:

  1. `Message`: Represents individual messages exchanged in a chat.

     - **Attributes**:
       - `role` (str): The role of the message sender (e.g., "user" or "assistant").
       - `content` (str): The content of the message.
     - **Methods**:
       - `from_dict`: Converts a dictionary to a `Message` object.
       - `to_dict`: Converts a `Message` object to a dictionary.

  2. `ChatRequest`: Encapsulates a set of messages, semester information, and selected course IDs.

     - **Attributes**:
       - `messages` (List[Message]): A list of messages exchanged.
       - `semesters` (str): The semester for the course recommendations.
       - `current_selected_course_id` (List[str]): List of currently selected course IDs.
     - **Methods**:
       - `from_dict`: Converts a dictionary to a `ChatRequest` object.
       - `to_dict`: Converts a `ChatRequest` object to a dictionary.

  3. `ChatResponse`: Represents the server's response to a chat request.

     - **Attributes**:
       - `response` (str): The generated response message.
       - `rankedCourseIds` (List[str]): List of ranked course IDs.
     - **Methods**:
       - `from_dict`: Converts a dictionary to a `ChatResponse` object.
       - `to_dict`: Converts a `ChatResponse` object to a dictionary.

- **Usage Example**:

  ```python
  # Creating a message
  msg = Message(role="user", content="What courses are available?")
  msg_dict = msg.to_dict()
  print(msg_dict)

  # Creating a ChatRequest
  chat_request = ChatRequest(
      messages=[msg], semesters="Spring 2024", current_selected_course_id=["CSE101"]
  )
  request_dict = chat_request.to_dict()
  print(request_dict)
  ```
### coursesranking
### courses\_ranking\_v5.py

- **Description**:\
  Handles course data loading, encoding, and ranking based on semantic similarity. It processes raw course information to compute rankings that align with user preferences.

- **Key Functions**:

  1. `load_courses_from_file(file_path: str) -> List[Dict]`:
     - Loads course data from a JSON file (`embedding_course_info.json`) and validates its format.

  2. `get_query_vector(query: str, model: str = 'all-MiniLM-L6-v2') -> np.ndarray`:
     - Converts a user query into a vector representation using a pre-trained Sentence Transformer model.

  3. `calculate_similarity(course_vectors: np.ndarray, query_vector: np.ndarray) -> np.ndarray`:
     - Computes cosine similarity between the query vector and each course vector.

  4. `match_and_sort_courses(query: str, course_data: List[Dict]) -> List[Dict]`:
     - Matches the query against course data, ranks the courses by similarity, and returns the sorted results.

  5. `get_top_courses(sorted_courses: List[Dict], top_n: int = 5) -> List[Dict]`:
     - Extracts the top N ranked courses from the sorted list.

- **Usage Example**:

  ```python
  from courses_ranking_v5 import load_courses_from_file, match_and_sort_courses

  # Load courses
  courses = load_courses_from_file("embedding_course_info.json")

  # Match and rank courses
  user_query = "artificial intelligence"
  sorted_courses = match_and_sort_courses(user_query, courses)

  # Print top-ranked courses
  print(sorted_courses[:5])
  ```

- **Highlights**:
  - Implements semantic matching using Sentence Transformers.
  - Logs detailed information to aid debugging and development.
### promptv5
### prompt\_v5.txt

- Template for generating structured course recommendations.
- Specifies detailed formatting and guidelines for output structure.
- **Example**:
  ```
  Course Code: MEME646, Course Name: Special Topics in AI Practice (I)
  Introduction: This course explores foundational AI theories and methods.
  Recommendation Reason: Ideal for students pursuing expertise in AI.
  ```
### querygenerator
### query\_generator.py

- **Description**:\
  Converts user inputs into structured queries for the Groq API, leveraging the predefined system prompt for query generation.

- **Key Functions**:

  1. `convert_messages_to_groq_format(messages: List[Dict[str, str]]) -> str`:
     - Converts a list of user messages into a Groq-compatible format for processing.

  2. `read_system_prompt_r(file_path: str) -> str`:
     - Reads and returns the content of the system prompt template from the specified file path.

  3. `generate_potential_query(messages: List[Dict[str, str]], prompt_path: str) -> Dict[str, str]`:
     - Generates a structured query using the Groq API, based on user input messages and the system prompt.

- **Usage Example**:

  ```python
  from query_generator import convert_messages_to_groq_format, generate_potential_query

  # User messages
  messages = [{"role": "user", "content": "I want to learn data science"}]

  # Convert messages to Groq format
  formatted_messages = convert_messages_to_groq_format(messages)

  # Generate query
  query = generate_potential_query(messages, "prompt_v5.txt")
  print(query)
  ```

- **Highlights**:
  - Integrates Groq API to process user inputs and generate detailed course search parameters.
  - Handles fallback scenarios for missing API keys or invalid configurations.
  - Logs interactions for debugging and development.
### responsegenerator
### response\_generator.py

- Generates detailed responses for ranked courses.
- **Functions**:
  - `convert_messages_to_groq_format`: Formats input messages.
  - `read_system_prompt_u`: Reads response generation prompt template.
  - `generate_response`: Uses Groq API to generate user-facing replies.
- Supports extensive debugging and error handling.
### requirements
### requirements.txt

- Lists project dependencies:
  - Flask
  - flask-cors
  - groq
  - python-dotenv
- Ensures consistent environment setup.

---

## Testing

### Query Generator

Run the `test_query_generator` function in `query_generator.py` to test query generation:

```bash
python query_generator.py
```

### Response Generator

Run the `test_response_generator` function in `response_generator.py` to test response generation:

```bash
python response_generator.py
```

---

## Environment Variables

Create a `.env` file in the root directory and add the following variables:

```env
GROQ_API_KEY=<your-groq-api-key>
```

---

## Dependencies

Listed in `requirements.txt`:

- Flask
- flask-cors
- groq
- python-dotenv

Install them using:

```bash
pip install -r requirements.txt
```

