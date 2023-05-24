Based on Database Design,here are the access patterns available


1) ### Create/Read/Update/Delete User (Transaction Process)
- `PK=USER#<Username>`
- `SK=USER#<Username>`
- `PK=USEREMAIL#<Email>`
- `SK=USEREMAIL#<Email>`
2) ### Create/Update/Read/Delete Jobs
- `PK=USER#<Username>`
- `SK=JOB#<JobId>`
3) ### Create/Update Application
- `PK=JOB#<JobId>#APPLICATION#<ApplicationId>`
- `PK=JOB#<JobId>#APPLICATION#<ApplicationId>`
4) ### List all jobs per User
- `PK=USER#<Username>`
- `SK= BEGINS_WITH('JOB#')`
5) ### Book a Nanny (StepFunctions Workflow)
- `PK=USER#<Username>`
- `SK=JOB#<JobId>`
- `PK=JOB#<JobId>#APPLICATION#<ApplicationId>`
- `PK=JOB#<JobId>#APPLICATION#<ApplicationId>`
<br>

<br>
We need a couple of Global Secondary Indexes(GSI), to create more access patterns.
For example, we can't get all job applications for a particular job, without adding a GSI.
