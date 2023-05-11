#### List All Jobs
As a nanny, you'll definitely wish to see all available jobs around you.And better still,
received notifications, when there's an available job around you. 
<br />

In this section, we'll only implement the retrieval of all available jobs. In an updated version 
of the api, i'll love to use the user's current location(longitude and latitude), alongside each 
jobs current location and get only jobs which are in close proximity to the user. 
<br />

We already get these attributes when creating both users and jobs. So all that's left is the 
calculation. For precision, maybe we won't use the user's saved current location and instead go 
with their location at that exact point in time.

<br />

We created a GSI called `getJobByStatus` to retrieve jobs based on it's status.
<br />

Here's how the code looks like 
```
        response = table.query(
            IndexName="getJobsByStatus",
            KeyConditionExpression=Key('jobStatus').eq(jobStatus),
            ScanIndexForward=False

        )

        logger.info(f'response is {response["Items"]}')
        jobs = [Job(item).job_dict() for item in response['Items']]

        logger.debug({"jobs list is": jobs})
        return jobs


```
We've created a `job entity` class which maps the attributes from dynamodb to a dictionary in the class. 

```
class Job:
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



```
Please go ahead to add the `list_job_by_status` endpoint and test to see how it all comes together.
<br />

As always, the code is available for reference.
