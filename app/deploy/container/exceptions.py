class SecurityIssueError(Exception):
    # Custom class to handle exceptions
    # if the project contains vulnerabilities

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
