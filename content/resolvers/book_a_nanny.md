
### Booking a nanny
Booking a nanny entails accepting a job application and rejecting the rest.

We'll orchestrate the booking process using an Express Step Functions Workflow.


Before we proceed, here's a recap of how this endpoint was written before

> The first version of this endpoint didn't use step functions to orchestrate the booking process.
> Everything was done with custom code in a lambda function.
>
>After reviewing the code 2 yrs later, I decided to
> Refactor the lambda function code into a step functions workflow.
>
>Meaning I chose automation over custom logic.
>
>This led to a huge boost in performance for this endpoint.
>
> As a matter of fact, the step functions workflow took half the time the lambda function took to do the job.
>
Here's the full conversation on Linkedin
[Performance Results Are In](https://www.linkedin.com/feed/update/urn:li:activity:7066700086679863296/?commentUrn=urn%3Ali%3Acomment%3A(activity%3A7066700086679863296%2C7066766726595559424)&dashCommentUrn=urn%3Ali%3Afsd_comment%3A(7066766726595559424%2Curn%3Ali%3Aactivity%3A7066700086679863296)&dashReplyUrn=urn%3Ali%3Afsd_comment%3A(7067120504096051201%2Curn%3Ali%3Aactivity%3A7066700086679863296)&replyUrn=urn%3Ali%3Acomment%3A(activity%3A7066700086679863296%2C7067120504096051201))

I used vegeta to run 50 transactions per second for 60 seconds on both the lambda function code and the refactored express step functions workflow.
Here are the results. 

Check out the latencies.
![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/performance.png)

Don't get me wrong, refactoring to Step functions might have improved performance, but increased the cost of running at scale as well. 

Based on my conversation with a couple of respected serverless engineers, I hear step functions is costly to run.

So before you add it to your applications, be sure to have exhausted all other options first.

Let's Proceed.

When a parent creates a job, nannies can apply for that job. The parent would then be able to accept(book a nanny) the application for whomever they see fit for the job.

<br />

Booking a nanny entails,
- Getting all applications for the job in particular.
- accepting one of the job application(changing application status to ACCEPTED),
- declining all other job applications(changing application status to DECLINED),
- closing the job, so that it won't be available anymore for applying to(changing job status to CLOSED).
<br />

Here's a breakdown of how the code would work
- Get all applications for a job with a Dynamodb Query and GSI(Global Secondary Index).
- Update Job Status from OPEN to CLOSED and application status for accepted an applicant from PENDING to ACCEPTED.
- Put the rest of the job applications into an SQS queue, which would then be polled by another lambda function and update the job application status from PENDING to DECLINED asynchronously.
<br />

We'll use an Express Step functions workflow to accomplish this task, since our
use-case would be short-lived and instantaneous.

If you are interested in seeing how this was done using a lambda function, visit this [link](https://github.com/trey-rosius/babysitter_api/blob/master/babysitter/resolvers/jobs/book_nanny_lambda.py)

For added functionality, it'll be good to send a push notification and an email to the applicant whose application was `accepted`. But this functionality isn't within the scope of this tutorial.
<br />

Let's get started.
<br />
