# TODO

Flight Plan
X Register flight plan
    X Register a flight plan without constraint
    X Register a flight with constraint
X Request information on a flight plan
    X Flight area details
    ? Authorization
    ? Telemetry
X Inform changes in a flight plan area (Constraints or other flight plans)
    X Authenticate request made by another USS
    X Delete the flight in the DSS
    X Change local flight status to Deleted
X Start the flight
    X Start the flight without obstacles
    X Start the flight with obstacles

USS to USS
X Add token generation
X Add token verification with private key

Refactoring
X Improve the AuthClient. Make it inherit the httpx.Auth instead of httpx.AsyncClient
X Way to store and use the Schemas
    X Improve how to use the post body (parameters in the route handler function?)
    X Improve the file structure
X Improve the database models
X Improve crud operations with the database (in the controllers)

Constraints
- Constraint Management
    X Add constraints
    - Remove constraints
- Constraint Endpoints
    - Get information from constraints
    - Handle changes in the constraints
- Refactor similarities OIR and CR

Subscription
- Add subscription to an area
- When handling operational intent delete, notify the subscribers
- Receive subscription notifications
- Send subscription notifications (When creating a flight)

User Auth
- Add User registration (What information should be provided?)
    - Add User token generation
    - Retrieve user information from a flight plan
- User Websocket to transmit real-time information in active flights

