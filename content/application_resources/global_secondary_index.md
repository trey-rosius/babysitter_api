For this api, we'll create 3 GSI's for additional access patterns.
#### Global Secondary Indexes
1) `jobApplications`: Get applications for a job. Parents have to see all applications for the job
they posted, in-order to book who they intend to work with.
- `PK = GS1PK AND SK=GSI1SK`
2) `jobsAppliedTo`: A Nanny would definitely love to see all the jobs they applied to
- `PK = GSI2PK AND SK=GSI2SK`
3) `jobsByStatus`: It's essential to display OPEN jobs to job seekers. The system admin would also love
to see open /closed jobs.
- `PK = jobStatus AND SK=GSI1SK`

These are the few access patterns we'll cover in this tutorial.There's still a lot to add. You can take up the challenge and push forward.
