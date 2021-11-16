class Application:
    def __init__(self, item=None):
        if item is None:
            item = {}
        self.id = item['id']
        self.username = item['username']
        self.jobId = item['jobId']
        self.jobApplicationStatus = item['jobApplicationStatus']
        self.createdOn = item['createdOn']

    def application_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "jobId": self.jobId,
            "jobApplicationStatus": self.jobApplicationStatus,
            "createdOn": self.createdOn
        }


