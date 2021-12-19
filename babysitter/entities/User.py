class User:
    def __init__(self, item=None):
        if item is None:
            item = {}
        self.id = item['id']
        self.username = item['username']
        self.email = item['email']
        self.type = item['type']
        self.profilePicUrl = item['profilePicUrl']
        self.firstName = item['firstName']
        self.lastName = item['lastName']
        self.address = item['address']
        self.about = item['about']
        self.longitude = item['longitude']
        self.latitude = item['latitude']
        self.status = item['status']
        self.createdOn = item['createdOn']

    def user_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "profilePicUrl": self.profilePicUrl,
            "address": self.address,
            "about": self.about,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "type": self.type,
            "status": self.status,
            "createdOn": self.createdOn
        }

    def user_jobs(self, jobs=[]):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "profilePicUrl": self.profilePicUrl,
            "address": self.address,
            "about": self.about,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "type": self.type,
            "status": self.status,
            "createdOn": self.createdOn,
            "postedJobs": jobs
        }
