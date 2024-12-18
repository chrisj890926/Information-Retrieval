from typing import List

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from chat_types import ChatRequest, Message, ChatResponse
from query_generator import*
from response_generator import*
from courses_ranking_2 import*

app = Flask(__name__)
# Enable CORS (Which allows the frontend to send requests to this server)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat() -> Response:
    data: ChatRequest = ChatRequest.from_dict(request.json)
    messages: List[Message] = data.messages
    semesters: str = data.semesters
    current_selected_course_ids: List[str] = data.current_selected_course_id

    # Debugging
    print("=== Received data ===")
    print(f"semesters: {semesters}")
    [print(f"role: {msg.role}, content: {msg.content}") for msg in messages]
    print(f"currentSelectedCourseId: {current_selected_course_ids}")
    print("=====================")

    ## Forwards the request to the logic module ##

    # Generate query for retrieval
    queryForIR  = generate_potential_query(messages)
    queryForIR_str = dict_to_str(queryForIR)

    # Get retrieval result
    top_course = get_top_courses(queryForIR_str) # list[Dict]
    top_course_str = ranked_to_str(top_course) # str (for LLM)
    #print(f"{'-'*50}\nTop courses:\n{top_course_str}")

    # Generate Assistant Response
    assistant_response = generate_response(messages, top_course_str)

    # Rresponse
    response_message: str = assistant_response
    ranked_course_ids: List[str] = [str(course['course_code']) for course in top_course]
    response: ChatResponse = ChatResponse(response=response_message, ranked_course_ids=ranked_course_ids)

    return jsonify(response.to_dict())

if __name__ == '__main__':
    app.run(debug=True)