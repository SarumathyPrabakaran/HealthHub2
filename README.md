# HealthHub

This Flask application is designed to manage user authentication, profile management, and activity tracking. It utilizes a PostgreSQL database for data storage and includes the capability to interact with the OpenAI API for explaining medical terms.



## Technical Details:
1. Flask Application:
    Manages routing, request handling, and session management.
    Renders HTML templates with Jinja2.
    Uses flash for displaying messages and url_for for URL generation.

2. SQLAlchemy ORM:
    Manages database connections and operations.
    Defines models for logincred, Profiles, Activity, and ActivityTracking.

3. OpenAI API:
    The application in the other folder would typically make HTTP requests to OpenAI's endpoint, passing the medical term and receiving the explanation in response.