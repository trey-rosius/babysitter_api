From this current design, here are the access patterns available
1) Create/Read/Update/Delete User (Transaction Process) 
- `PK=USER#<Username>`
- `SK=USER#<Username>` 
- `PK=USEREMAIL#<Email>`
- `SK=USEREMAIL#<Email>`
2) Create/Update/Read/Delete Jobs 
- `PK=USER#<Username>` 
- `SK=JOB#<JobId>`
3) Create/Update Application 
- `PK=JOB#<JobId>#APPLICATION#<ApplicationId>` 
- `PK=JOB#<JobId>#APPLICATION#<ApplicationId>`
4) List all jobs per User
- `PK=USER#<Username>` 
- `SK= BEGINS_WITH('JOB#')` 
5) Book a Nanny (Transaction Process) 
- `PK=USER#<Username>` 
- `SK=JOB#<JobId>`
- `PK=JOB#<JobId>#APPLICATION#<ApplicationId>` 
- `PK=JOB#<JobId>#APPLICATION#<ApplicationId>`
<br>

Booking a nanny means, changing the status of a job application from `PENDING`  to `ACCEPTED` , while changing the 
job status from `OPEN` to `CLOSED`
<br>
<br>
The current design has limitations. There are a couple of access patterns it doesn't support yet.
For example, we can't get all job applications for a particular job.We need a Global Secondary index(GSI) for that. 
