class JobEntity:
    def __init__(self, item=None):
        if item is None:
            item = {}
        self.id = item["id"]
        self.jobType = item['jobType']
        self.username = item['username']
        self.startDate = item['startDate']
        self.endDate = item['endDate']
        self.startTime = item['startTime']
        self.endTime = item['endTime']
        self.longitude = item['longitude']
        self.latitude = item['longitude']
        self.address = item['address']
        self.city = item['city']
        self.cost = item['cost']
        self.jobStatus = item['jobStatus']

    def job_dict(self):
        return {
            "id": self.id,
            "jobType": self.jobType,
            "username": self.username,
            "startDate": self.startDate,
            "endDate": self.endDate,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "address": self.address,
            "city": self.city,
            "cost": self.cost,
            "jobStatus": self.jobStatus

        }

    def all_jobs(self, jobs=None):
        if jobs is None:
            jobs = []
        return {
            "jobs": jobs
        }

    def job_application_dict(self, applications=None):
        if applications is None:
            applications = []
        return {
            "id": self.id,
            "jobType": self.jobType,
            "username": self.username,
            "startDate": self.startDate,
            "endDate": self.endDate,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "address": self.address,
            "city": self.city,
            "cost": self.cost,
            "jobStatus": self.jobStatus,
            "applications": applications

        }
